# -*- coding: utf-8 -*-
import json
import rijndael
import base64
import urllib
import urllib2
import socket
import struct 
from IPy import IP

KEY_SIZE = 16
BLOCK_SIZE = 32

class Api(object):

    _app_id  = ''
    _app_key = ''
    _api_url = ''
 
    def __init__(self, app_id='', app_key='', api_url='', debug=False):
        """ Construct an Api object, 
            taking an APP ID, APP KEY and API URL parameter """
        self._app_id  = app_id
        self._app_key = app_key
        self._api_url = api_url
        self._debug   = debug
 
    def sendRequest(self, request_params={}):
        """ Send the request to the API server
            also encrypts the request, then checks
            if the results are valid """
        if self._debug: print "Request Params: %s" % request_params
        request = json.dumps(request_params).encode('utf-8')
        enc_request = encrypt(self._app_key, request)
        if self._debug: print "Encrypted Resquest: %s" % enc_request
        params = {'enc_request': enc_request, 'app_id': self._app_id}
        data = urllib.urlencode(params)
        req = urllib2.Request(self._api_url, data)
        if self._debug: print "Querying '%s'..." % self._api_url
        response = urllib2.urlopen(req)
        try:
            raw_response = response.read()
            result = json.loads(raw_response)
            if self._debug: print "Result: %s" % result
            return result
        except ValueError, e:
            print "Error", e
            print "Response: %s" % raw_response
        return {'success': False, 'error': raw_response}

    def getSections(self, format='ip'):
        """ Get all sections """
        res = self.sendRequest({
            'controller': 'sections', 
            'action'    : 'read', 
            'format'    : format,
            'all'       : True
        })
        return res['data']

    def getSubnets(self, format='ip'):
        """ Get all subnets """
        res = self.sendRequest({
            'controller': 'subnets', 
            'action'    : 'read', 
            'format'    : format,
            'all'       : True
        })
        return res['data']

    def getAddresses(self, format='ip'):
        """ Get all adresses
              format='decimal' returns in decimal form (default)
              format='ip'      returns in IP address """
        res = self.sendRequest({
            'controller': 'addresses', 
            'action'    : 'read', 
            'format'    : format,
            'all'       : True
        })
        return res['data']

    def getSubnetsInSection(self, section_id, format='ip'):
        """ Get all subnets in a specific section 
              format='decimal' returns in decimal form (default)
              format='ip'      returns in IP address """
        res = self.sendRequest({
            'controller': 'subnets', 
            'action'    : 'read', 
            'format'    : format,
            'sectionId' : section_id
        })
        return res['data']

    def getAdressesInSubnet(self, subnet_id, format='ip'):
        """ Get all IP addreses in a specific subnet 
              format='decimal' returns in decimal form (default)
              format='ip'      returns in IP address """
        res = self.sendRequest({
            'controller': 'addresses', 
            'action'    : 'read', 
            'format'    : format,
            'subnetId' : subnet_id
        })
        return res['data']

    def createAddress(self, description=None, ip_addr=None, mac=None, subnet_id=None, mask=24,
                dns_name=None, owner=None, state=None, switch=None, port=None, note=None):
        """ Create a new IP address and calculates the subnet associated """
        i = ip_addr.split('/')
        ip_addr = i[0]
        if len(i) > 1: mask = i[1]
        p = ""
        if subnet_id is None:
            print "Looking for subnet..."
            for s in self.getSubnets(format='ip'):
                if not s['subnet'] or not s['mask']: continue
                ips = IP('%s/%s' % (s['subnet'], s['mask']))
                p = "%s/%s (IPv%s) " % (s['subnet'], s['mask'], ips.version())
                if ips.version() == 6: pass
                elif ip_addr in ips and s['mask'] == str(mask):
                    subnet_id = s['id']
        if subnet_id is None:
            raise Exception("Subnet doesn't exist for ip %s" % ip_addr)
        else:
            print "Adding %s/%s to subnet %s" % (ip_addr, mask, p)
        ip_addr = struct.unpack("!I", socket.inet_aton(ip_addr))[0]
        res = self.sendRequest({
            'controller' : 'addresses',
            'action'     : 'create',
            'format'     : 'ip',
            'subnetId'   : subnet_id,
            'ip_addr'    : ip_addr,
            'description': description,
            'dns_name'   : dns_name,
            'mac'        : mac,
            'owner'      : owner,
            'state'      : state,
            'switch'     : switch,
            'port'       : port,
            'note'       : note
        })
        return res['data']

    def importIpMacBindings(self, separator=','):
       """ Import Ip Addresses and Mac address associated """
       s = ""
       for address in self.getAddresses(format='ip'):
           if not address['description']: address['description'] = 'Unknown'
           if address['ip_addr'] and address['mac']:
               s+= separator.join([address['description'], address['ip_addr'], address['mac']])+"\n"
       return s[:-1]

    def importAddresses(self, format='csv', separator='#'):
       """ Export Ip addresses to desired format:
             * csv
             * dhcpd.conf
       """
       if format == 'csv':
           # IP # State # Description # hostname # MAC # Owner # Device # Port # Note"
           s = ""
           for address in self.getAddresses(format='ip'):
               #s+= separator.join([address['ip_addr'], address['state'], address['description'], \
               #    address['dns_name'], address['mac'], address['owner'], \
               #    address['switch'], address['note']])+"\n"
               s+= separator.join([address['description'], address['ip_addr'], address['mac']])+"\n"
       elif format == 'dhcpd.conf':
           s = "# Generated from %s - %s\n\n" % (self._app_id, self._api_url)
           for address in self.getAddresses(format='ip'):
               s+= "host %s {\n" % address['description']
               s+= "  hardware ethernet %s;\n" % address['mac']
               s+= "  fixed-address %s;\n" % address['ip_addr']
               s+= "}\n\n"
       return s


def encrypt(key, plaintext):
    padded_key = key.ljust(KEY_SIZE, '\0')
    padded_text = plaintext + (BLOCK_SIZE - len(plaintext) % BLOCK_SIZE) * '\0'
    r = rijndael.rijndael(padded_key, BLOCK_SIZE)
    ciphertext = ''
    for start in range(0, len(padded_text), BLOCK_SIZE):
        ciphertext += r.encrypt(padded_text[start:start+BLOCK_SIZE])
    encoded = base64.b64encode(ciphertext)
    return encoded

def decrypt(key, encoded):
    padded_key = key.ljust(KEY_SIZE, '\0')
    ciphertext = base64.b64decode(encoded)
    r = rijndael.rijndael(padded_key, BLOCK_SIZE)
    padded_text = ''
    for start in range(0, len(ciphertext), BLOCK_SIZE):
        padded_text += r.decrypt(ciphertext[start:start+BLOCK_SIZE])
    plaintext = padded_text.split('\x00', 1)[0]
    return plaintext
