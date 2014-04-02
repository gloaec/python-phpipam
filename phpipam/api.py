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

    _app_id = ''
    _app_key = ''
    _api_url = ''
 
    def __init__(self, app_id='', app_key='', api_url=''):
        """ Construct an Api object, 
            taking an APP ID, APP KEY and API URL parameter """
        self._app_id = app_id
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
        result = json.loads(response.read())
        if DEBUG: print "Result: %s" % result
        return result

    def getSections(self):
        """ Retrieve Phpipam sections """
        res = self.sendRequest({
            'controller': 'sections', 
            'action'    : 'read', 
            'all'       : True
        })
        return res['data']

    def getSubnetsInSection(self, section_id, format='ip'):
        """ Get all subnets in a specific section """
        res = self.sendRequest({
            'controller': 'subnets', 
            'action'    : 'read', 
            'format'    : format,
            'sectionId' : section_id
        })
        return res['data']
    

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
