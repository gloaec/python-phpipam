<?php

/**
 *	phpIPAM API class to work with addresses
 *
 * Reading addresses:
 *	get by id: 	?controller=addresses&action=read&id=1
 *	get by name: 	?controller=addresses&action=read&name=address name
 *	get all:	?controller=addresses&action=read&all=true
 */

class Addresses
{
	/* variables */
	private $_params;
	
	/* set parameters, provided via post */
	public function __construct($params)
	{
		$this->_params = $params;
		
		//ip address format, can be decimal or ip
		if(!$this->_params['format']){ $this->_params['format'] = "decimal"; }
		//verify IP address format
		if(!($this->_params['format']=="decimal" || $this->_params['format']== "ip")) {
			throw new Exception('Invalid format');
		}
	}

	/** 
	* create new address 
	*/
	public function createAddresses($_params)
	{
		//init section class
		$address = new Address();
		//required parameters
		$address->action      		= $this->_params['action'];
		$address->sectionId        	= $this->_params['sectionId'];
		$address->masterAddressId 	= $this->_params['masterAddressId'];
		$address->address		= $this->_params['address'];
		$address->mask	  		= $this->_params['mask'];
		$address->description	  	= $this->_params['description'];
		$address->vrfId			= $this->_params['vrfId'];
		$address->vlanId		= $this->_params['vlanId'];
		$address->allowRequests		= $this->_params['allowRequests'];
		$address->showName		= $this->_params['showName'];
		$address->permissions		= $this->_params['permissions'];
		$address->pingAddress		= $this->_params['pingAddress'];

		//create section
		$res = $address->createAddress(); 	
		//return result
		return $res;
	}


	/** 
	* read addresses 
	*/
	public function readAddresses()
	{
		//init address class
		$address = new Address();
		
		//set IP address format
		$address->format = $this->_params['format'];
		
		//get all addresses
		if($this->_params['all']){ $address->all = true; }
		//get all addresses in address
		elseif($this->_params['sectionId']) { $address->sectionId = $this->_params['sectionId']; }
		//get address by ID
		else { $address->id = $this->_params['id']; }
		
		//fetch results
		$res = $address->getAddress(); 
		
		//return address(s) in array format
		return $res;
	}	
	
	
	/** 
	* update existing address 
	*/
	public function updateAddresses()
	{
		/* not yet implementes */
		throw new Exception('Action not yet implemented');
	}	
	
	
	/** 
	* delete address 
	*/
	public function deleteAddresses()
	{
		/* not yet implementes */
		throw new Exception('Action not yet implemented');
	}
}

?>
