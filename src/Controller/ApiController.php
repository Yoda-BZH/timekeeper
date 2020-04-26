<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Security\Core\Security;

use App\Services\Connectors\Manager;


class ApiController extends AbstractController
{
    /**
     * @Route("/api/update", name="api")
     */
    public function update(Request $request, Manager $connectorManager)
    {
      $type = $request->query->get('type');
      $force = (bool) $request->query->get('force');
      
      //try {
        $connector = $connectorManager->get($type);
      //}
      //catch(\Exception $e)
      //{
      //  $response = new Response(json_encode(array()));
      //  $response->headers->set('Content-Type', 'application/json');
      //  return $response;
      //}
      $data = $connector->get(
        $request->query->get('start'),
        $request->query->get('end'), 
        $force
      );
      
      $response = new Response(json_encode($data));
      $response->headers->set('Content-Type', 'application/json');
      
      return $response;
    }
    
    /**
     * @Route("/api/{type}/{action}", methods={"GET"})
     */
    public function handleGetActions($type, $action, Request $request, Manager $connectorManager)
    {
      $connector = $connectorManager->get($type);
      $cbData = $connector->getCallback($action, 'GET');
      $cb = $cbData[0];
      $args = array();
      foreach($cbData[1] as $queryName)
      {
        $args[$queryName] = $request->query->get($queryName);
      }
      $data = $connector->$cb($args);
      
      $response = new Response(json_encode($data));
      $response->headers->set('Content-Type', 'application/json');

      return $response;
    }
    
    /**
     * @Route("/api/{type}/{action}", methods={"POST"})
     */
    public function handlePostActions($type, $action, Request $request, Manager $connectorManager)
    {
      $connector = $connectorManager->get($type);
      $cbData = $connector->getCallback($action, 'POST');
      $cb = $cbData[0];
      $args = array();
      foreach($cbData[1] as $queryName)
      {
        $args[$queryName] = $request->request->get($queryName);
      }
      $data = $connector->$cb($args);

      $response = new Response(\json_encode($data));
      $response->headers->set('Content-Type', 'application/json');
      return $response;
    }

    /**
     * @Route("/api/user", name="user")
     */
    public function user(Security $security)
    {
      $username = $security->getUser()->getUsername();
      
      $response = new Response(\json_encode(array('user' => $username)));
      $response->headers->set('Content-Type', 'application/json');
      
      return $response;
    }
    
}
