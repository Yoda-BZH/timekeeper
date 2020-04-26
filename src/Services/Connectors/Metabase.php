<?php

namespace App\Services\Connectors;
use Symfony\Contracts\Cache\CacheInterface;

abstract class Metabase extends AbstractConnector implements ConnectorInterface
{  
  protected $cache = null;
  private $metabaseBaseUrl = '';
  protected $queryUrl = '';
  protected $queryParameters = '';

  public function __construct(CacheInterface $cache, string $metabase, string $queryUrl, string $queryParameters)
  {
    $this->cache = $cache;
    $this->metabaseBaseUrl = $metabase;
    $this->queryUrl = $queryUrl;
    $this->queryParameters = $queryParameters;
  }
  
  public function getQueryUrl()
  {
    return $this->queryUrl;
  }
  
  public function getMetabaseBaseUrl()
  {
    return $this->metabaseBaseUrl;
  }
  
  public function metabase(string $from, string $to, bool $force = false)
  {
    $tz = new \DateTimeZone('Europe/Paris');
    $from = $this->cleanupDatetime($from);
    $to = $this->cleanupDatetime($to);

    $beginOfWeek = new \Datetime($from);
    $beginOfWeek->setTimezone($tz);
    $endOfWeek = new \Datetime($to);
    $endOfWeek->setTimezone($tz);

    $type = $this->getName();

    $user = $this->user->getUsername();
    $memcacheKey = $user.'_metabase_'.$type.'_'.$beginOfWeek->format('Ymd');
    $cachedInfosEl = $this->cache->getItem($memcacheKey);
    if(!$force && $cachedInfosEl->isHit())
    {
      return $cachedInfosEl->get();
    }

    $urlParams = \sprintf($this->queryParameters,
      $beginOfWeek->format('Y-m-d'),
      $endOfWeek->format('Y-m-d'),
      $user
    );

    $url = $this->getMetabaseBaseUrl() . $this->getQueryUrl() . $urlParams;

    $r = $this->jsonCall($url);
    
    $ret = $r['data'];
    $infos = $r['infos'];

    if('' == $ret || null == $ret)
    {
      return array();
    }

    $ret = \json_decode($ret, true);

    $entryManager = new MetaBaseEntryManager($tz);
    $entryManager->entries = $ret;
    $entries = $entryManager->convert();

    foreach($entryManager->cumulated as $k => $c)
    {
      $entries[] = array(
        'title' => 'Total: '.$this->nicetime($c),
        'start' => $k,
        'end'   => $k,
        'type'  => $entryManager->type,
        'spent' => $c,
        'allDay'=> True,
      );
    }
    
    $cachedInfosEl->set($entries);
    $cachedInfosEl->expiresAfter($expiration = 600);
    $this->cache->save($cachedInfosEl);
    
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

    return sprintf($format, $hours, $minutes);
  }
}
