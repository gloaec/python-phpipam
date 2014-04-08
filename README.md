python-phpipam
==============

API written in python for phpipam

Important notice
----------------

Please use with this version of phpipam :

[https://github.com/gloaec/phpipam](https://github.com/gloaec/phpipam)

The API is inconsistent on master repository enovance/phpipam

Installation instructions
-------------------------

1. Dependencies: `apt-get install python-argparse`
2. Install **phpipam** and enable the API from the interface
3. Setup API credentials in `phpipam.conf`

Usage
-----

Use `./create_address` to create or modify addresses

    usage: create_address [-h] [-v] [-d DESCRIPTION] [-D] [-m MAC] [-n MASK] ip
    
    positional arguments:
      ip                    IP address (CIDR format supported)
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -d DESCRIPTION, --description DESCRIPTION
                            Ip address description
      -D, --debug           Debug mode
      -m MAC, --mac MAC     Mac address
      -n MASK, --mask MASK  Netmask

Use `./get_ipmac_bindings` to get the csv export of IP/MAC addresses bindings
Use `./get_addresses` to get addresses data to desired format
