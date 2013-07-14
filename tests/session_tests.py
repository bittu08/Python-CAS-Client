'''
Created on 16-Apr-2013

@author: bittu
'''
import time
import unittest
import base64
import json
from hashlib import sha256
from pyplugin.session_manager import CookieSessionManager , SessionExpired, \
    SignatureIncorrect

class SessionTest(unittest.TestCase):
    
    def test_session(self):
        sm = CookieSessionManager("MyPassword")
        expected_user = get_test_user()
        session_key = sm.create_session_key(expected_user)
        actual_user = sm.get_user_from_session_key(session_key)
        
        keys = ["user_name", "accessToken", "first_name", "last_name", "nonce"]
        for key in keys:
            self.assertEqual(actual_user[key], expected_user[key], "%s does not match" % key)

    def test_session_expiry(self):
        sm = CookieSessionManager("MyPassword", 1)
        expected_user = get_test_user()
        session_key = sm.create_session_key(expected_user)
        time.sleep(2)
        self.assertRaises(SessionExpired, sm.get_user_from_session_key, (session_key))
        
    def test_session_key_modification(self):
        sm = CookieSessionManager("MyPassword")
        expected_user = get_test_user()
        session_key = sm.create_session_key(expected_user)
        modify_decode = base64.b64decode(session_key)
        modify_decode=modify_decode.replace(modify_decode[20],'9')
        modify_decode=modify_decode.replace(modify_decode[21],'9')
        modify_decode=modify_decode.replace(modify_decode[22],'9')
        modify_key = base64.b64encode(modify_decode)
        self.assertRaises(SignatureIncorrect, sm.get_user_from_session_key, (modify_key))
        

def get_test_user():
    return {"user_name": "bittu.kumar", "accessToken": "1EA02826-4003-4CC7-88FE-BD7D2A5AA6A0", "first_name": "Bittu", "last_name": "Kumar",
            "nonce": 342359238232, "roles": ["manager", "provider", "admin"]}

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
