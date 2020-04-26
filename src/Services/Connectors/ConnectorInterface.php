<?php

namespace App\Services\Connectors;
use Symfony\Component\Security\Core\User\UserInterface;

interface ConnectorInterface {
  public function get(string $start, string $end, bool $force = false);
  
  public function getName();
  public function setUser(UserInterface $user, string $password);
  
}
