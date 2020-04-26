<?php

namespace App\Services\Connectors;

use Symfony\Component\Security\Core\Security;
use Symfony\Component\HttpFoundation\RequestStack;

class Manager
{
  private $connectors = array();
  
  public function __construct(array $connectors, Security $security, RequestStack $requestStack)
  {
    $user = $security->getUser();
    $authPassword = $requestStack->getCurrentRequest()->server->get('PHP_AUTH_PW');

    /**
     * initialize all connectors
     */
    foreach($connectors as $connector)
    {
      $name = $connector->getName();
      
      /**
       * some connectors need the user/password to authenticate on the APIs
       */
      $connector->setUser($user, $authPassword);
      
      /**
       * passing GET parameters the connector needs
       */
      foreach($connector->getRequestFields() as $field)
      {
        $connector->setField($field, $requestStack->getCurrentRequest()->query->get($field));
      }
      /**
       * storing the connector
       */
      $this->connectors[$name] = $connector;
    }
  }
  
  /**
   * @param string $name The connector name
   * 
   * @return ConnectorInterface a connector
   */
  public function get(string $name)
  {
    if(!\array_key_exists($name, $this->connectors))
    {
      $allConnectorsDeclared = \array_keys($this->connectors);
      $connectorNames = \implode(', ', $allConnectorsDeclared);
      throw new \Exception(sprintf('Service "%s" not found in connectors. I only know those: %s', $name, $connectorNames));
    }
    
    return $this->connectors[$name];
  }

}
