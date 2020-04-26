<?php

namespace App\Services\Connectors;

use Symfony\Component\Security\Core\User\UserInterface;

abstract class AbstractConnector
{
  /**
   * User object, usually LdapUser object
   */
  protected $user = null;
  
  /**
   * User password, provided in PHP_AUTH_PW
   */
  private $password = null;
  
  /**
   * GET parameters the connector needs
   */
  protected $requestFields = array();
  
  /**
   * an array of urls to bind to, and method to call
   */
  protected $actions = array();
  
  /**
   * the manager may want to know the GET parameters the connector needs.
   * It returns the parameters names
   */
  public function getRequestFields()
  {
    return \array_keys($this->requestFields);
  }
  
  protected function generateUrl($id)
  {
    return '';
  }
  
  /**
   * assigning one parameter at a time
   */
  public function setField($field, $value)
  {
    $this->requestFields[$field] = $value;
  }
  
  /**
   * For a given URL /{name}/{action}
   * This returns the method name to assign to
   */
  public function getCallback($actionName, $type)
  {
    if(!\array_key_exists($actionName, $this->actions))
    {
      throw new \Exception(\sprintf('No action called "%s" in "%s"', $actionName, $this->getName()));
    }

    $action = $this->actions[$actionName];
    
    /**
     * check if it's the right HTTP method it is (post, get, ...)
     */
    if($type != $action[0])
    {
      throw new \Exception('Action '.$actionName.' is '.$action[0].', not '.$type);
    }
    
    return array($action[1], $action[2] ?? array());
  }

  /**
   * get current timezone
   * 
   * @todo: use the user timezone ? from javascript ? js post to store en tz in cache ?
   */
  public function getTimezone()
  {
    return new \DateTimeZone('Europe/Paris');
  }
  
  /**
   * sometimes, a datetime send in javascript contains some extraneous data
   * eg: Wed Apr 22 2020 14:23:49 GMT+0200 (heure d’été d’Europe centrale)
   * This removes the last part
   */
  public function cleanupDatetime($str)
  {
    return \preg_replace('/\(.*\)$/', '', $str);
  }

  public function setUser(UserInterface $user, string $authPassword)
  {
    $this->user = $user;
    $this->password = $authPassword;
  }
  
  private function createCurlObject($url)
  {
    $curl = \curl_init();
    
    $authentication = \sprintf('%s:%s', $this->user->getUsername(), $this->password);
    
    \curl_setopt($curl, CURLOPT_URL ,$url);
    \curl_setopt($curl, CURLOPT_USERPWD, $authentication);
    \curl_setopt($curl, CURLOPT_HEADER, false);
    \curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
    \curl_setopt($curl, CURLOPT_CONNECTTIMEOUT, 5);
    \curl_setopt($curl, CURLOPT_TIMEOUT, 10);
    
    return $curl;
  }
  
  protected function writePasswordToPipe(&$pipe)
  {
      \fwrite($pipe, $this->password);
  }
  
  protected function jsonCall($url)
  {
    $curl = $this->createCurlObject($url);

    $r = \curl_exec($curl);
    
    $curlInfos = \curl_getinfo($curl);
    
    return array(
      'data' => $r,
      'infos' => $curlInfos,
    );
  }
  
  protected function jsonSend($url, $data, $method = 'POST')
  {
    if(!\in_array($method, array('POST', 'PUT')))
    {
      throw new \Exception(\sprintf('Method "%s" not supported', $method));
    }
    $curl = $this->createCurlObject($url);

    switch($method)
    {
      case 'POST':
        \curl_setopt($curl, CURLOPT_POST, true);
        break;
        
      case 'PUT':
        \curl_setopt($curl, CURLOPT_CUSTOMREQUEST, "PUT");
        break;
        
      default:
        // should not happend
        // seriously.
        // or you've remove the in_array at the beginning of the method.
        throw new \Exception('This method only supports POST and PUT');
        break;
    }
    
    \curl_setopt($curl, CURLOPT_POSTFIELDS, $data);
    $r = \curl_exec($curl);
    
    $curlInfos = \curl_getinfo($curl);
    
    return array(
      'data' => $r,
      'infos' => $curlInfos,
    );
  }
}
