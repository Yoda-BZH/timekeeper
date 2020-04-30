<?php

namespace App\Services\Connectors;
use Symfony\Contracts\Cache\CacheInterface;

class Gitlab extends Metabase implements ConnectorInterface {  
  public function getName()
  {
    return 'gitlab';
  }
  
  public function get(string $start, string $end, bool $force = false)
  {
    return $this->metabase($start, $end, $force);
  }
}
