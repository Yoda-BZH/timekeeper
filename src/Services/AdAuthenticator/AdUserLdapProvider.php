<?php

namespace App\Services\AdAuthenticator;

use Symfony\Component\Ldap\Security\LdapUserProvider;
use Symfony\Component\HttpFoundation\RequestStack;
use Symfony\Component\Ldap\LdapInterface;
use Symfony\Contracts\Cache\CacheInterface;
use Symfony\Component\Ldap\Entry;
use Symfony\Component\Security\Core\Exception\InvalidArgumentException;

class AdUserLdapProvider extends LdapUserProvider
{
  private $cache = null;
  public function __construct(
    CacheInterface $cache,
    RequestStack $requestStack,
    LdapInterface $ldap, 
    string $baseDn,
    string $domain,
    string $searchDn = null, 
    string $searchPassword = null, 
    array $defaultRoles = [], 
    string $uidKey = null, 
    string $filter = null, 
    string $passwordAttribute = null, 
    array $extraFields = []
  )
  {
    $this->cache = $cache;
    $this->requestStack = $requestStack;
    
    /**
     * connect on the LDAP using the user credentials
     */
    $authPassword = $requestStack->getCurrentRequest()->server->get('PHP_AUTH_PW');
    $authLogin = $requestStack->getCurrentRequest()->server->get('PHP_AUTH_USER');
    $searchDn = sprintf('%s\%s', $domain, $authLogin);

    parent::__construct($ldap, $baseDn, $searchDn, $authPassword, $defaultRoles, $uidKey, $filter, $passwordAttribute, $extraFields);
  }

}

