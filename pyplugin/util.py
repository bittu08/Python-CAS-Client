'''
Created on 02-May-2013

@author: bittu
'''
from django.conf import settings
import logging

from session_manager import CookieSessionManager, SessionExpired, \
    SignatureIncorrect

    
logger = logging.getLogger(__name__)

def is_cookies(request):
    return True if request.COOKIES.has_key('user_detail') else False
        
def validate_cookies(request):
    cookie = request.COOKIES['user_detail']
    try:
        sm = CookieSessionManager(settings.SECRET_KEY)
        user = sm.get_user_from_session_key(cookie)
        return user
    except SignatureIncorrect:
        logger.info("incorrect cookies signature")
    except Exception as ex:
        logger.exception(ex)
        logger.info("unhandled exception thrown")
    return None

def get_username(request):
    if is_cookies(request):
        user = validate_cookies(request)
        if user:
            return user['user_name']
        else:
            return None
    return None
