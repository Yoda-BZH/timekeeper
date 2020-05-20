<?php

namespace App\Services\Connectors;


class MetaBaseEntryManager {

  public $lastEntryPerDay = array();
  public $entries = array();
  public $cumulated = array();
  public $type = '';
  protected $tz;
  private $endpoint;
  
  public function __construct(\DateTimeZone $tz)
  {
    $this->tz = $tz;
  }
  
  public function getLastEntry($entry)
  {
    $dayFormat = $entry['end']->format('Y-m-d');
    //var_dump(
    //  $this->lastEntryPerDay,
    //  isset($this->lastEntryPerDay[$this->type][$dayFormat]),
    //  $this->lastEntryPerDay[$this->type][$dayFormat] instanceof Datetime,
    //  $this->lastEntryPerDay[$this->type][$dayFormat] instanceof Datetime && $this->lastEntryPerDay[$this->type][$dayFormat]->format('s') > $entry['start']->format('s'),
    //  );
    if (
      isset($this->lastEntryPerDay[$this->type][$dayFormat])
      &&
      $this->lastEntryPerDay[$this->type][$dayFormat] instanceof Datetime
      &&
      $this->lastEntryPerDay[$this->type][$dayFormat]->format('U') > $entry['start']->format('U')
    )
    {
      return clone $this->lastEntryPerDay[$this->type][$dayFormat];
    }

    return false;
  }

  //public function fixStartEndRedmine($entry)
  //{
  //  global $lastEntryForDay;
  //  if($entry['comments'] != '' && \preg_match('/TK:\[([^\]]*) - ([^\]]*)\] ?(.*)?/', $entry['comments'], $matches) === 1)
  //  {
  //    $entry['start'] = new \Datetime($matches[1]);
  //    $entry['end'] = new \Datetime($matches[2]);
  //    $comment = $matches[3] ?? '';
  //  }
  //  else
  //  {
  //    $entry['start'] = new \Datetime($entry['spent_date'].' 08:00:00');
  //    $dayFormat = $entry['start']->format('Y-m-d');
  //    $entry['end'] = clone $entry['start'];
  //    if ($lastEntry = $this->getLastEntry($entry))
  //    {
  //      $entry['start'] = $lastEntry;
  //    }
  //    //$end->add(new DateInterval('PT'.round($entry['spent_time'] * 60 ).'M'));
  //    $entry['end']->modify('+ '.$entry['spent_time'].' minutes');
  //    $comment = $entry['comments'];
  //  }
  //  $dayFormat = $entry['end']->format('Y-m-d');
  //  $this->lastEntryPerDay[$this->type][$dayFormat] = $entry['end'];
  //  $entry['comment'] = $comment;
  //
  //  return $entry;
  //}

  public function fixStartEndOtrs($entry)
  {
    global $lastEntryForDay;
    $entry['end'] = new \Datetime($entry['spent_date']);
    $entry['start'] = clone $entry['end'];
    $entry['start']->modify('- '.$entry['spent_time'].' minutes');
    //if ($lastEntry = $this->getLastEntry($entry))
    //{
    //  //echo 'got last entry';
    //  $entry['start'] = $lastEntry;
    //  $entry['end'] = clone $entry['start'];
    //  $entry['end']->modify('+ '.$entry['spent_time'].' minutes');
    //  //echo '// fixing '.PHP_EOL;
    //}
    //else
    //{
    //  //echo 'no fixxing'.PHP_EOL;
    //  //$entry['start']->modify('- '.$entry['spent_time'].' minutes');
    //}

    $dayFormat = $entry['end']->format('Y-m-d');
    $this->lastEntryPerDay[$this->type][$dayFormat] = $entry['end'];
    //var_dump($this->lastEntryPerDay);

    return $entry;
  }

  public function fixStartEndGitlab($entry)
  {
    global $lastEntryForDay;

    $entry['start'] = new \Datetime($entry['spent_date'].' 08:00:00');
    $dayFormat = $entry['start']->format('Y-m-d');
    $entry['end'] = clone $entry['start'];
    if ($lastEntry = $this->getLastEntry($entry))
    {
      $entry['start'] = $lastEntry;
    }
    if($entry['spent_time'] < 0)
    {
      $entry['spent_time'] = 0;
    }
    //$end->add(new DateInterval('PT'.round($entry['spent_time'] * 60 ).'M'));
    $entry['end']->modify('+ '.$entry['spent_time'].' minutes');
    $comment = $entry['comments'];

    $dayFormat = $entry['end']->format('Y-m-d');
    $this->lastEntryPerDay[$this->type][$dayFormat] = $entry['end'];
    $entry['comment'] = $comment;

    return $entry;
  }

  /**
   * fixme: find a better way to "fix" start and stop times
   */
  public function fixStartEnd($entry)
  {
    switch($entry['type'])
    {
      case 'gitlab':
        return $this->fixStartEndGitlab($entry);
      //case 'redmine':
      //  return $this->fixStartEndRedmine($entry);
      case 'otrs':
        return $this->fixStartEndOtrs($entry);
    }
  }

  public function convertMetabaseToTK($entry)
  {
    $this->type = $entry['type'];
    $d = new \Datetime($entry['spent_date']);
    $d->setTimezone($this->tz);

    $originalSpentTime = $entry['spent_time'];

    //if($entry['spent_time'] < 15)
    //{
    //  $entry['spent_time'] = 15;
    //}

    $entry = $this->fixStartEnd($entry);

    $lastEntryForDay = $d->format('Y-m-d');

    //switch($this->type)
    //{
    //  case 'redmine':
    //    $end->modify('+ '.$entry['spent_time'].' minutes');
    //    break;
    //  case 'otrs':
    //    $end->modify('- '.$entry['spent_time'].' minutes');
    //    break;
    //}
    $newEntry = array(
      'start'    => $entry['start'], //->format(DateTime::ISO8601),
      'end'      => $entry['end'], //->format(DateTime::ISO8601),
      'title'    => $entry['title'],
      'spent'    => (int) $entry['spent_time'],
      'comments' => $entry['comments'],
      'type'     => $this->type,
    );
    switch($this->type)
    {
      //case 'redmine':
      //  $newEntry['comment'] = $entry['comments'];
      //  $newEntry['rid'] = $entry['redmine_id'];
      //  $newEntry['url'] = $this->generateUrl($entry['redmine_id']);
      //  break;
      case 'redmine':
        throw new \Exception('Redmine is not on metabase');
        break;
      case 'otrs':
        $newEntry['url'] = $entry['link'];
        $newEntry['oid'] = $entry['ticket_id'];
        break;
      case 'gitlab':
        break;
    }

    //$dayFormat = $entry['end']->format('Y-m-d');
    //if(!isset($this->cumulated[$dayFormat]))
    //{
    //  $this->cumulated[$dayFormat] = 0;
    //}
    //$this->cumulated[$dayFormat] += (int) $originalSpentTime;

    return $newEntry;
  }

  public function consolidate($id)
  {
    if($this->entries[$id]['type'] == 'gitlab' && $this->entries[$id]['spent'] <= 0)
    {
      $this->entries[$id] = false;
      return;
    }

    if($this->entries[$id]['type'] != 'otrs')
    {
      return;
    }

    if($this->entries[$id]['spent'] > 15)
    {
      //echo 'main';
      return;
    }

    foreach($this->entries as $k => $e)
    {
      if(!$e ||!$this->entries[$id])
      {
        continue;
      }
      if($e['oid'] != $this->entries[$id]['oid'])
      {
        continue;
      }
      if($k == $id)
      {
        continue;
      }
      if($this->entries[$id]['start']->format('Ymd') != $e['start']->format('Ymd'))
      {
        continue;
      }
      //if($e['spent'] < 15)
      //{
      //  continue;
      //}
      //echo 'cosolidating'.PHP_EOL;
      //var_dump($e, $this->entries[$id]);
      $this->entries[$k]['spent'] += (int) $this->entries[$id]['spent'];
      $this->entries[$k]['end']->modify('+ '.$this->entries[$id]['spent'].' minutes');

      $this->entries[$id] = false;
      //return;
    }

    return;
  }

  public function formatDates($entry)
  {
    $entry['start'] = $entry['start']->format(\DateTime::ISO8601);
    $entry['end'] = $entry['end']->format(\DateTime::ISO8601);

    return $entry;
  }

  public function setTo15Minutes($entry)
  {
    if($entry['spent'] > 15)
    {
      return $entry;
    }

    $entry['end']->modify('+ '.(15 - $entry['spent']).' minutes');

    return $entry;
  }

  public function convert()
  {
    // convert format
    $this->entries = \array_map(array($this, 'convertMetabaseToTK'), $this->entries);

    // merge entries less than 15 minutes with main events, if found
    $nbEntry = \count($this->entries);
    for($k = 0; $k < $nbEntry; $k++)
    {
      $this->consolidate($k);
    }
    // entries less than 15 minutes merges are set to false, remove them
    $this->entries = \array_filter($this->entries);
    // dates are datetimes, now convert to datetimes

    $this->entries = \array_map(array($this, 'setTo15Minutes'), $this->entries);
    $this->entries = \array_map(array($this, 'formatDates'), $this->entries);

    return $this->entries;
  }
}
