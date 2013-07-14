"""Module to handle with cookie management"""

import copy
import hmac
import base64
import json
from hashlib import sha256
import time
import logging
logger = logging.getLogger(__name__)

JsonHandler = lambda payload:json.dumps(payload, encoding='latin-1', sort_keys=True)

class SessionExpired(Exception):{}

class SignatureIncorrect(Exception):{}

class CookieSessionManager(object):
    def __init__(self, secret_key, expires = 2*60*60):
        self.secret_key = secret_key
        self.expires = expires
        
    def create_session_key(self, user):
        expiry_time = int(time.time()) + self.expires
        user["expiry_time"] = expiry_time
        serialized_user = JsonHandler(user)
        signature = self.generate_signature(serialized_user)        
        user["signature"] = signature
        session_key = base64.b64encode(JsonHandler(user))
        return session_key
    
    def get_user_from_session_key(self, session_key):
        cookie_content = base64.b64decode(session_key)        
        user = json.loads(cookie_content)
        user_clone = copy.deepcopy(user)        
        del user_clone['signature']
        serialized_user = JsonHandler(user_clone)
        digest_signature = self.generate_signature(serialized_user)
        actual_signature = JsonHandler(user['signature'])
        expected_signature = JsonHandler(digest_signature)        
        current_timestamp = int(time.time())
        if user["expiry_time"] < current_timestamp:
            user['authenticated'] = False
        else:
            user['authenticated'] = True
        if expected_signature == actual_signature:
            return user
        else:
            raise SignatureIncorrect()
    
    def generate_signature(self, payload):
        hashed = hmac.new(self.secret_key, payload, sha256)
        signature = hashed.digest()
        return signature
    
