from django.http import HttpResponse, HttpResponseForbidden,HttpResponseRedirect
from functools import wraps
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

def login_required(login=False):
    """
    Decorator for views that checks valid server request otherwise show 403 forbidden error
    A web server may return a 403 Forbidden HTTP status code in response to a request from a client for a web page
    or resource to indicate that the server refuses to allow the requested action. It includes
        403.1 - Execute access forbidden.
        403.2 - Read access forbidden.
        403.3 - Write access forbidden.
        403.4 - SSL required.
        403.5 - SSL 128 required.
        403.6 - IP address rejected.
        403.7 - Client certificate required.
        403.8 - Site access denied.
        403.9 - Too many users.
        403.10 - Invalid configuration.
        403.11 - Password change.
        403.12 - Mapper denied access.
        403.13 - Client certificate revoked.
        403.14 - Directory listing denied.
        403.15 - Client Access Licenses exceeded.
        403.16 - Client certificate is untrusted or invalid.
        403.17 - Client certificate has expired or is not yet valid.
        403.18 - Cannot execute request from that application pool.
    """
    def decorator(func):

        def inner_decorator(request, *args, **kwargs):
            if request.user.is_authenticated():
                return func(request, *args, **kwargs)
            else:
                if login:
                    return HttpResponseRedirect('/accounts/login?next=%s' % (request.get_full_path()) )
                else:
                    return HttpResponseForbidden('HTTP 403 forbidden error')
                
        return wraps(func)(inner_decorator)
    return decorator