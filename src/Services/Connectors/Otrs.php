<?php

namespace App\Services\Connectors;
use Symfony\Contracts\Cache\CacheInterface;

class Otrs extends Metabase implements ConnectorInterface
{  
  public function getName()
  {
    return 'otrs';
  }
  
  public function get(string $start, string $end, bool $force = false)
  {
    return $this->metabase($start, $end, $force);
  }
}
