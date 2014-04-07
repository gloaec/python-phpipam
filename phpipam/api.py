# -*- coding: utf-8 -*-
import json
import rijndael
import base64
import urllib
import urllib2

KEY_SIZE = 16
BLOCK_SIZE = 32
DEBUG = False

class Api(object):

    _app_id  = ''
    _app_key = ''
    _api_url = ''
 
    def __init__(self, app_id='', app_key='', api_url=''):
        """ Construct an Api object, 
            taking an APP ID, APP KEY and API URL parameter """
        self._app_id  = app_id
        self._app_key = app_key
        self._api_url = api_url
 
    def sendRequest(self, request_params={}):
        """ Send the request to the API server
            also encrypts the request, then checks
            if the results are valid """
        if DEBUG: print "Request Params: %s" % request_params
        request = json.dumps(request_params).encode('utf-8')
        enc_request = encrypt(self._app_key, request)
        if DEBUG: print "Encrypted Resquest: %s" % enc_request
        params = {'enc_request': enc_request, 'app_id': self._app_id}
        data = urllib.urlencode(params)
        req = urllib2.Request(self._api_url, data)
        if DEBUG: print "Querying '%s'..." % self._api_url
        response = urllib2.urlopen(req)
        try:
            result = json.loads(response.read())
            if DEBUG: print "Result: %s" % result
            return result
        except ValueError, e:
            print "Error", e
            print "Response: %s" % response.read()
        pass

    def getSections(self):
        """ Get all sections """
        res = self.sendRequest({
            'controller': 'sections', 
            'action'    : 'read', 
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

    def exportAddresses(self, format='csv', separator='#'):
       """ Export Ip addresses to desired format:
             * csv
             * dhcpd.conf
       """
       if format == 'csv':
           # IP # State # Description # hostname # MAC # Owner # Device # Port # Note"
           s = ""
           for address in self.getAddresses(format='decimal'):
               s+= separator.join([address['ip_addr'], address['state'], address['description'], \
                   address['dns_name'], address['mac'], address['owner'], \
                   address['switch'], address['note']])+"\n"
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
