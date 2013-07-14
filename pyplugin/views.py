"""CAS login/logout replacement views"""

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from session_manager import CookieSessionManager
from urllib import urlencode
from urlparse import urljoin
import logging
from django.contrib import auth
from pyplugin.backends import CASBackend

__all__ = ['login', 'logout']
logger = logging.getLogger(__name__)

sm = CookieSessionManager(settings.SECRET_KEY)

def _service_url(request, redirect_to=None):
    """Generates application service URL for CAS"""
    protocol = ('http://', 'https://')[request.is_secure()]
    host = request.get_host()
    service = protocol + host + request.path
    if redirect_to:
        if '?' in service:
            service += '&'
        else:
            service += '?'
        service += urlencode({REDIRECT_FIELD_NAME: redirect_to})
    return service


def _redirect_url(request):
    """Redirects to referring page, or CAS_REDIRECT_URL if no referrer is
    set.
    """
    next = request.GET.get(REDIRECT_FIELD_NAME)
    if not next:
        if settings.CAS_IGNORE_REFERER:
            next = settings.CAS_REDIRECT_URL
        else:
            next = request.META.get('HTTP_REFERER', settings.CAS_REDIRECT_URL)
        prefix = (('http://', 'https://')[request.is_secure()] + 
                  request.get_host())
        if next.startswith(prefix):
            next = next[len(prefix):]
    return next


def _login_url(service, **kwargs):
    """Generates CAS login URL"""
    kwargs.update({'service': service})
    if settings.CAS_EXTRA_LOGIN_PARAMS:
        kwargs.update(settings.CAS_EXTRA_LOGIN_PARAMS)
    #Add renew=True, if user's want  force login into CAS
    return urljoin(settings.CAS_SERVER_URL, 'login') + '?' + urlencode(kwargs)


def _logout_url(request, next_page=None):
    """Generates CAS logout URL"""
    url = urljoin(settings.CAS_SERVER_URL, 'logout')
    # This is done for nginx due to ELB sending request at http
    if next_page.startswith('http'):
        url += '?' + urlencode({'service': next_page})
    else:
        protocol = ('http://', 'https://')[request.is_secure()]
        host = request.get_host()
        url += '?' + urlencode({'service': protocol + host + next_page})
    return url


def login(request):
    """Forwards to CAS login URL or verifies CAS ticket"""
    next_page = request.GET.get('next')
    if not next_page:
        next_page = _redirect_url(request)

    if hasattr(request, 'user') and request.user.is_authenticated():
        return HttpResponseRedirect(next_page)

    ticket = request.GET.get('ticket')  
    service = _service_url(request, next_page)
    
    logger.debug("Trying to Login. Ticket : %s \n Cookie : %s \n" % (ticket, request.COOKIES.get('user_detail')))
    
    if ticket :
        auth = CASBackend()
        user = auth.authenticate(ticket=ticket, service=service, request=request)
        logger.debug("Found User %s" % user)
        
        if user :
            logger.debug('Successfully authenticated %s' % user.get_username())
            logger.debug('Redirecting to ' + next_page)
            response = HttpResponseRedirect(next_page)
            
            # We set a user cookie so that re-login is not needed everytime
            session_key = sm.create_session_key(user.get_cookie_args())
            response.set_cookie(key="user_detail", value=session_key)
            return response
        else:
            logger.debug("Ticket is Invalid")
            return HttpResponseRedirect(_login_url(service, invalid_ticket=1))
    else:
        logger.debug('User is not authenticated -- redirecting to CAS')
        return HttpResponseRedirect(_login_url(service))


def logout(request, next_page=None):
    """Redirects to CAS logout page"""
    
    if request.COOKIES.has_key('user_detail'):
        del request.COOKIES['user_detail']
    
    if not next_page:
        next_page = _redirect_url(request)
        
    if settings.CAS_LOGOUT_COMPLETELY:
        response = HttpResponseRedirect(_logout_url(request, next_page))
    else:
        response = HttpResponseRedirect(next_page)
    
    response.delete_cookie('user_detail')
    return response

        