"""CAS authentication middleware"""

from util import validate_cookies
import models
import logging
logger = logging.getLogger(__name__)

__all__ = ['CASMiddleware']

class CASMiddleware(object):
    """Middleware that allows CAS authentication on admin pages"""
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Forwards unauthenticated requests to the admin page to the CAS
        login URL, as well as calls to django.contrib.auth.views.login and
        logout.
        """
        
        if request.COOKIES.has_key('user_detail'):
            user = validate_cookies(request)
            if user :
                request.user = models.SSOUser(**user)
                logger.debug("User Authentication : %s " % request.user.is_authenticated() )
        return
