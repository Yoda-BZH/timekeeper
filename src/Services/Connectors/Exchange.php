<?php

namespace App\Services\Connectors;
use Symfony\Contracts\Cache\CacheInterface;

class Exchange extends AbstractConnector implements ConnectorInterface
{  
  private $cache = null;
    
  private $emailServer = '';
  private $domain = '';
  
  private $preferedEmailAsLogin;
  
  protected $requestFields = array(
    'showMasked' => '',
  );

  protected $actions = array(
    'event-hide' => array(
      'POST', 
      'hide', 
      array('uid', 'start'),
    ),
  );

  public function __construct(CacheInterface $cache, string $emailServer, string $domain)
  {
    $this->cache = $cache;
    $this->emailServer = $emailServer;
    $this->domain = $domain;
  }

  public function getName()
  {
    return 'exchange';
  }
  
  private function getListOfPossibleUserEmailsUsedAsLogin()
  {
    $listOfEmails = array();

    $this->preferedEmailAsLogin = $this->cache->getItem('user_prefered_email_'.$this->user->getUsername());
    
    if($this->preferedEmailAsLogin->isHit())
    {
      //header('Tk-Email: Using prefered from preferences');
      $listOfEmails[] = $this->preferedEmailAsLogin->get();
    }
    else
    {
      $listOfEmails[] = $this->user->getEntry()->getAttribute('mail')[0];
      $proxyAddresses = $this->user->getEntry()->getAttribute('proxyAddresses');
      //var_dump($proxyAddresses);
      if($proxyAddresses != null)
      {
        foreach($proxyAddresses as $proxyAddress)
        {
          if(\substr($proxyAddress, 0, 5) == 'SMTP:')
          {
            $listOfEmails[] = substr($proxyAddress, 5);
          }
        }
      }
    }
    
    return $listOfEmails;
  }
  
  public function get(string $start, string $end, bool $force = false)
  {
    $start = $this->cleanupDatetime($start);
    $end = $this->cleanupDatetime($end);
    
    $tz = new \DateTimeZone('Europe/Paris');
    
    $startDate = new \DateTime($start);
    $startDate->setTimezone($tz);
    
    $endDate = new \DateTime($end);
    $endDate->setTimezone($tz);

    $strStart = $startDate->format('Y-m-d');
    $strEnd = $endDate->format('Y-m-d');

    $showMasked = (bool) $this->requestFields['showMasked'];
    
    $user = $this->user->getUsername();

    $memcacheKey = $user . '_exchange_'.$startDate->format('Ymd');
    if($showMasked)
    {
      $memcacheKey .= '_withUncached';
    }
    
    $cachedExchangeEl = $this->cache->getItem($memcacheKey);
    if(!$force && $cachedExchangeEl->isHit())
    {
      return $cachedExchangeEl->get();
    }

    $listOfEmails = $this->getListOfPossibleUserEmailsUsedAsLogin();
    
    $exchangeUser = $this->user->getEntry()->getAttribute('userPrincipalName')[0];
    $listOfEmails[] = $exchangeUser;

    $workingAccount = false;
    foreach($listOfEmails as $userEmail)
    {
      $cmd = sprintf('../src/poc-py-exchange/test.py --start=%s --stop=%s --login=%s --mail=%s --server=%s',
        \escapeshellarg($strStart),
        \escapeshellarg($strEnd),
        \escapeshellarg($exchangeUser),
        \escapeshellarg($userEmail),
        \escapeshellarg($this->emailServer),
        \escapeshellarg($this->domain)
      );
      //header('X-Cmd: '.$cmd);

      $descriptorspec = array(
         0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
         1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
         2 => array("file", "/tmp/error-output.txt", "a") // stderr is a file to write to
      );
      
      $r = \proc_open($cmd, $descriptorspec, $pipes);
      if(!$r)
      {
        return array('errors' => 'unable to launch exchange.py');
      }

      /**
       * the script waits for the password through STDIN
       * that way, the password cannot be seen in the process list
       */      
      $this->writePasswordToPipe($pipes[0]);

      \fclose($pipes[0]);
      $entries = \stream_get_contents($pipes[1]);
      \fclose($pipes[1]);
      $returnValue = \proc_close($r);
      
      // should be treat no entry as an error ?
      if(0 != $returnValue || trim($returnValue) == '[]')
      {
        //echo 'got an error, checking for other emails ?'.N;
        continue;
      }
    
      /**
       * yay, found a working account
       */
      $workingAccount = true;
      
      /**
       * save tthis preference in cache
       */
      $this->preferedEmailAsLogin->set($userEmail);
      $this->cache->save($this->preferedEmailAsLogin);
      //echo 'setting '.$userEmail.' as prefered email account'.N;
      break;
    }

    if(false === $workingAccount)
    {
      return array('errors' => 'unable to find a working account, tried '.implode(', ', $listOfEmails));
    }

    if($entries == '')
    {
      // don't bother to json_decode en empty string
      return array('errors' => 'no entries');
    }

    $entries = json_decode($entries, true);
    if(isset($entries['errors']))
    {
      return array('errors' => 'found errors in script output');
    }
    
    $entriesCopy = $entries;
    foreach($entriesCopy as $k => $entry)
    {
      $d = new \DateTime($entry['start']);
      $d->setTimezone($tz);
      
      /**
       * per user and per user preference
       * the user can choose to hide an exchange event
       * each event has a suposedly unique key.
       * unless it's a repeatable event, the key will be identical for each event
       * Compute a cache key per user + day + event key
       * This could cause a problem if the event repeats several times a day
       * all events for the day will be hidden
       */
      $md5 = \md5($d->format(\DateTime::ISO8601));
      
      $entryMaskedStatus = $this->cache->getItem('exchange_hide_' . $user . '_'.$entry['uid'] . $md5);
      if($showMasked == false && isset($entry['uid']) && $entryMaskedStatus->isHit() && $entryMaskedStatus->get() == true)
      {
        // user asked to hide this one, deleting from the response
        unset($entries[$k]);
      }
    }

    $cachedExchangeEl->set($entries);
    $this->cache->save($cachedExchangeEl);

    return $entries;
  }

  /**
   * the user asks to hide an event
   */
  public function hide($args)
  {

    if(!isset($args['uid']))
    {
      throw new \Exception('No uid to hide was provided');
    }

    $uid = $args['uid'];
    $args['start'] = $this->cleanupDatetime($args['start']);
    $start = new \Datetime($args['start']);
    $tz = new \DateTimeZone('Europe/Paris');
    $start->setTimezone($tz);
    $md5 = \md5($start->format(\DateTime::ISO8601));

    if($uid && $md5)
    {
      $key = 'exchange_hide_' . $this->user->getUsername() . '_' . $uid . $md5;
      $keyEntry = $this->cache->getItem($key);
      $keyEntry->set('1');
      $this->cache->save($keyEntry);

      return array();
    }
    
    throw new \Exception('Unable to define which event was to hide');
  }
}
