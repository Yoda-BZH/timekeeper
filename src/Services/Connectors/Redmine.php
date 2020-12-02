<?php

namespace App\Services\Connectors;
use Symfony\Contracts\Cache\CacheInterface;

class Redmine extends AbstractConnector implements ConnectorInterface {

  private $cache = null;
  private $useActivity = false;
  protected $actions = array(
    'assigned' => array(
      'GET',
      'assigned',
    ),
    'assign' => array(
      'GET',
      'assign',
    ),
    'add' => array(
      'POST',
      'add',
      array('start', 'end', 'comment', 'rid', 'uid', 'activity')
    ),
    'timeentry-update' => array(
      'POST',
      'update',
      array('teid', 'start', 'end', 'comment', 'rid')
    ),
    'autocomplete' => array(
      'GET',
      'autocomplete',
      array('term')
    ),
    'activities' => array(
      'GET',
      'projectActivities',
      array('redmineId'),
    ),
  );

  private $redmineBaseUrl = '';

  public function __construct(CacheInterface $cache, string $redmineUrl, bool $useActivity = false)
  {
    $this->cache = $cache;
    $this->redmineBaseUrl = $redmineUrl;
    $this->useActivity = $useActivity;
  }

  protected function generateUrl($id)
  {
    return $this->redmineBaseUrl. '/issues/' . $id;
  }

  public function getRedmineBaseUrl()
  {
    return $this->redmineBaseUrl;
  }

  public function getName()
  {
    return 'redmine';
  }

  public function get(string $start, string $end, bool $force = false)
  {
    $tz = $this->getTimezone();

    $start = $this->cleanupDatetime($start);
    $end = $this->cleanupDatetime($end);

    $startDate = new \Datetime($start);
    $startDate->setTimezone($tz);
    $endDate = new \Datetime($end);
    $endDate->setTimezone($tz);

    $user = $this->user->getUsername();

    $curDate = clone $startDate;
    $cumulated = array();

    //return array('fake' => 'data');

    $cacheRedmineUserId = 'redmine_uid_'.$user;
    $redmineUserIdEl = $this->cache->getItem($cacheRedmineUserId);

    if($redmineUserIdEl->isHit())
    {
      $redmineUserId = $redmineUserIdEl->get();
    }
    else
    {
      $url = $this->getRedmineBaseUrl() . '/users/current.json';

      $r = $this->jsonCall($url);
      $userInfos = \json_decode($r['data'], true);
      $redmineUserId = $userInfos['user']['id'];
      $redmineUserIdEl->set($redmineUserId);
      $this->cache->save($redmineUserIdEl);
    }
    //header('X-Redmine-user-ID: '.$redmineUserId);

    $this->cacheKey = $user.'_redmine_'.$startDate->format('Ymd');

    $cachedRedmineEl = $this->cache->getItem($this->cacheKey);
    if(!$force && $cachedRedmineEl->isHit())
    {
      return $cachedRedmineEl->get();
    }

    $url = $this->getRedmineBaseUrl() . '/time_entries.json?user_id='.$redmineUserId.'&period_type=2&from='.$startDate->format('Y-m-d').'&to='.$endDate->format('Y-m-d').'&limit=100';

    $r = $this->jsonCall($url);

    $timeEntries = json_decode($r['data'], true);

    if(!isset($timeEntries['time_entries']))
    {
      $timeEntries['time_entries'] = array();
    }
    $lastEntryPerDay = $cumulated;

    $entries = array();
    foreach($timeEntries['time_entries'] as $timeEntry)
    {
      $title = $timeEntry['issue']['id'];
      if($timeEntry['comments'] != '' && \preg_match('/(?<commentbefore>.*)? ?TK:\[(?<timestart>[^\]]*) - (?<timeend>[^\]]*)\] ?(?<commentafter>.*)?/', $timeEntry['comments'], $matches) === 1)
      {
        $start = new \Datetime($matches['timestart']);
        //$end = new Datetime($matches['timeend']);
        $comment = '';
        if($matches['commentbefore'] != '')
        {
          $comment = $matches['commentbefore'];
        }
        elseif($matches['commentafter'] != '')
        {
          $comment = $matches['commentafter'];
        }
      }
      else
      {
        $start = new \Datetime($timeEntry['spent_on'].' 08:00:00');
        $dayFormat = $start->format('Y-m-d');
        if (isset($lastEntryPerDay[$dayFormat]) && $lastEntryPerDay[$dayFormat] instanceof \Datetime && $lastEntryPerDay[$dayFormat]->format('U') >= $start->format('U'))
        {
          $start = clone $lastEntryPerDay[$dayFormat];
        }
        $comment = $timeEntry['comments'];
      }
      $end = clone $start;
      $end->modify('+ '.round($timeEntry['hours'] * 60 ).' minutes');

      $dayFormat = $start->format('Y-m-d');
      if(!isset($cumulated[$dayFormat]))
      {
        $cumulated[$dayFormat] = 0;
      }
      $cumulated[$dayFormat] += ($timeEntry['hours'] * 60 );
      $lastEntryPerDay[$dayFormat] = clone $end;

      $cachedIssueEl = $this->cache->getItem('redmine_'.$timeEntry['issue']['id']);

      if($cachedIssueEl->isHit())
      {
        $cachedIssue = $cachedIssueEl->get();
        $title = $cachedIssue['subject'];
      }
      else
      {
        $title = '';
      }

      $entries[] = array(
        'title'   => '#'.$timeEntry['issue']['id'] . ' ' . $title . (isset($comment) ? ' -- '.$comment : ''),
        'comment' => $comment,
        'start'   => $start->format(\DateTime::ISO8601),
        'end'     => $end->format(\DateTime::ISO8601),
        'type'    => 'redmine',
        'rid'     => $timeEntry['issue']['id'],
        'teid'    => $timeEntry['id'],
        'url'     => $this->getRedmineBaseUrl() . '/issues/' . $timeEntry['issue']['id'],
      );
    }

    //foreach($cumulated as $k => $c)
    //{
    //  $entries[] = array(
    //    'title' => 'Total: '.$this->nicetime($c),
    //    'start' => $k,
    //    'end'   => $k,
    //    'type'  => 'redmine',
    //    'rid'   => '',
    //    'spent' => $c,
    //    'allDay'=> True,
    //  );
    //}

    $cachedRedmineEl->set($entries);
    $cachedRedmineEl->expiresAfter($expiration = 600);
    $r = $this->cache->save($cachedRedmineEl);

    if(!$r)
    {
      return array();
    }

    return $entries;
  }

  public function nicetime($t)
  {
    if ($t < 1) {
      return;
    }
    $format = '%02d:%02d';
    $hours = floor($t / 60);
    $minutes = ($t % 60);
    return \sprintf($format, $hours, $minutes);
  }

  public function assigned()
  {
    $user = $this->user->getUsername();
    $cacheEl = $this->cache->getItem('redmine_'.$user);

    if(!$cacheEl->isHit())
    {
      $r = array();
    }
    else
    {
      $r = $cacheEl->get();
    }

    $ret = array('count' => \count($r));

    return $ret;
  }

  public function assign()
  {
    /**
     * @idea: fetch from user preferences the first day of the week
     */
    $day1 = new \Datetime('monday this week');
    $day7 = new \Datetime('sunday this week');

    $limit = 50;
    $offset = 0;
    $url = $this->getRedmineBaseUrl() . '/issues.json?limit='.$limit.'&status_id=*';

    $userIssues = array();
    $projects = array();
    foreach(array('assigned_to_id=me', 'watcher_id=me') as $search)
    {
      $offset = 0;
      do {
        $r = $this->jsonCall($s = $url . '&'.$search . '&offset='.((string) (int) $offset));

        $issues = \json_decode($r['data'], true);

        if (!isset($issues['issues']))
        {
          break;
        }

        foreach($issues['issues'] as $issue)
        {
          $userIssues[] = $issue['id'];
          $projects[] = $issue['project']['id'];
          //$memcache->set('redmine_'.$issue['id'], array('id' => $issue['id'], 'subject' => $issue['subject']));
          $redmineCacheEl = $this->cache->getItem('redmine_'.$issue['id']);
          $redmineCacheEl->set(array('id' => $issue['id'], 'subject' => $issue['subject'], 'projectId' => $issue['project']['id']));
          $this->cache->save($redmineCacheEl);
        }
        $offset += $limit;
      }
      while($offset < $issues['total_count']);
    }

    if ($this->useActivity)
    {
      foreach($userIssues as $redmineIssue)
      {
      }
      $projects = array_unique($projects);
      foreach($projects as $project)
      {
        $projectActivitiesCacheKey = sprintf('redmine_project_%d_activities', $project);
        $projectActivitiesCache = $this->cache->getItem($projectActivitiesCacheKey);
        if(!$projectActivitiesCache->isHit())
        {
          $projectUrl = sprintf('%s/projects/%s.json?include=time_entry_activities', $this->getRedmineBaseUrl(), $project);
          $projectActivitiesResult = $this->jsonCall($projectUrl);
          $projectActivities = \json_decode($projectActivitiesResult['data'], true);
          if(!$projectActivities['project'])
          {
            break;
          }
          $projectActivitiesCache->set($projectActivities['project']['time_entry_activities']);
          $this->cache->save($projectActivitiesCache);
        }
      }
    }

    $redmineUserIssuesCacheEl = $this->cache->getItem('redmine_'.$this->user->getUsername());
    $redmineUserIssuesCacheEl->set($userIssues);
    $this->cache->save($redmineUserIssuesCacheEl);

    return array('count' => \count($userIssues));
  }

  public function createCommentTag(string $comment, \Datetime $start, \Datetime $end)
  {
    return \sprintf(
      '%s TK:[%s - %s]',
      $comment,
      $start->format('r'),
      $end->format('r')
    );
  }

  /**
   * create a new time entry for a given redmine issue id
   */
  public function add($args)
  {
    $url = $this->getRedmineBaseUrl() . '/time_entries.json';

    $args['start'] = $this->cleanupDatetime($args['start']);
    $args['end'] = $this->cleanupDatetime($args['end']);

    $start = new \Datetime($args['start']);
    $end   = new \Datetime($args['end']);

    $interval = $end->diff($start);

    $spent = $interval->h + (($interval->i / 15) * 0.25 );

    $comment = $this->createCommentTag($args['comment'], $start, $end);

    $fields = array(
      'time_entry[issue_id]' => $args['rid'],
      //'spent_on' =>
      'time_entry[hours]' => $spent,
      'time_entry[comments]' => $comment,
      'time_entry[spent_on]' => $start->format('Y-m-d'),
    );
    if($args['activity'])
    {
      $fields['time_entry[activity_id]'] = $args['activity'];
    }

    $ret = $this->jsonSend($url, $fields);
    $curlInfos = $ret['infos'];

    if(201 != $curlInfos['http_code'])
    {
      throw new \Exception('Unable to add new redmine event');
    }

    if(isset($args['uid']) && $args['uid'] != '')
    {
      $key = 'exchange_hide_' . $this->user->getUsername() . '_' . strtr($args['uid'], '{}()/\\@:\"', '---------') . md5($start->format(\DateTime::ISO8601));
      $exchangeToHide = $this->cache->getItem($key);
      $exchangeToHide->set('1');
      $this->cache->save($exchangeToHide);
    }

    $newEntry = array(
      'title' => 'Redmine (pending #'.$args['rid'].')',
      'start' => $start->format(\DateTime::ISO8601),
      'end'   => $end->format(\DateTime::ISO8601),
      'type'  => 'redmine',
      'rid'   => $args['rid'],
      'comment' => $comment,
    );

    return $newEntry;
  }

  public function update($args)
  {
    if(!isset($args['teid']))
    {
      throw new \Exception('No time entry provided, cannot update redmine time entry');
      return;
    }
    $url = $this->getRedmineBaseUrl() . '/time_entries/'.$args['teid'].'.json';

    $args['start'] = $this->cleanupDatetime($args['start']);
    $args['end'] = $this->cleanupDatetime($args['end']);

    $start = new \Datetime($args['start']);
    $end   = new \Datetime($args['end']);

    $interval = $end->diff($start);

    $spent = $interval->h + (($interval->i / 15) * 0.25 );

    $currentComment = $args['comment'];

    //$comment = \sprintf(
    //  'TK:[%s - %s] %s',
    //  $start->format('r'),
    //  $end->format('r'),
    //  $currentComment
    //);
    $comment = $this->createCommentTag($currentComment, $start, $end);

    $fields = array(
      'time_entry[issue_id]' => $args['rid'],
      //'spent_on' =>
      'time_entry[hours]' => $spent,
      'time_entry[comments]' => $comment,
      'time_entry[spent_on]' => $start->format('Y-m-d'),
    );

    $curlData = $this->jsonSend($url, $fields, 'PUT');
    $r = $curlData['data'];
    $curlInfos = $curlData['infos'];

    if(200 != $curlInfos['http_code'])
    {
      throw new Exception('Unable to update redmine time entry');
      return;
    }

    $newEntry = array(
      'title' => 'Redmine (pending #'.$args['rid'].')',
      'start' => $start->format(\DateTime::ISO8601),
      'end'   => $end->format(\DateTime::ISO8601),
      'type'  => $this->getName(),
      'rid'   => $args['rid'],
    );

    return $newEntry;
  }

  /**
   * @fixme redmine ID can be smaller ...
   */
  private function isRedmineIssueID($terms, &$matches)
  {
    return \preg_match('/^\d{5}$/', $terms, $matches);
  }

  public function autocomplete(array $get)
  {
    $issuesCacheEl = $this->cache->getItem('redmine_'.$this->user->getUsername());
    if(!$issuesCacheEl->isHit())
    {
      return array();
    }
    $issues = (array) $issuesCacheEl->get();

    $ret = array();

    $terms = \trim(\strtolower($get['term']));

    $matches = array();
    if($this->isRedmineIssueID($terms, $matches))
    {
      //$issue = $memcache->get('redmine_'.$matches[0]);
      $issueEl = $this->cache->getItem('redmine_'.$matches[0]);

      if($issueEl->isHit())
      {
        $issue = $issueEl->get();
        !isset($ret[$terms]) && $ret[$terms] = array();
        $ret[$terms][$issue['id']] = array('rid' => $issue['id'], 'label' => sprintf('#%d - %s', $issue['id'], $issue['subject']));
      }
    }

    if('' != $terms)
    {
      $t = \array_filter(explode(' ', $terms));
      foreach($t as $term)
      {
        !isset($ret[$term]) && $ret[$term] = array();
        foreach($issues as $issueId)
        {
          $issueEl = $this->cache->getItem('redmine_'.$issueId);
          if(!$issueEl->isHit())
          {
            continue;
          }
          $issue = $issueEl->get();
          if(\strpos($issue['id'], $term) !== false || \strpos(\strtolower($issue['subject']), $term) !== false)
          {
            $ret[$term][$issue['id']] = array('rid' => $issue['id'], 'label' => \sprintf('#%d - %s', $issue['id'], $issue['subject']));
          }
        }
      }
    }

    if(\count($ret) > 1)
    {
      $ret = \array_values($ret);
      $ret = \array_intersect_key(...$ret);
    }
    elseif($terms != '')
    {
      $ret = $ret[$terms];
    }

    return $ret;
  }

  public function projectActivities(array $get)
  {
    if(!$this->useActivity)
    {
      return array();
    }
    $redmineId = $get['redmineId'];
    $issueCache = $this->cache->getItem('redmine_'.$redmineId);
    if(!$issueCache->isHit())
    {
      return array();
    }
    $issue = (array) $issueCache->get();

    $projectActivitiesCacheKey = sprintf('redmine_project_%d_activities', $issue['projectId']);

    $projectActivities = $this->cache->getItem($projectActivitiesCacheKey);
    if(!$projectActivities->isHit())
    {
      return array();
    }

    return $projectActivities->get();
  }
}
