"""CAS authentication backend"""

from django.conf import settings
from urllib import urlencode, urlopen
from urlparse import urljoin
import re
import logging
import models

__all__ = ['CASBackend']
logger = logging.getLogger(__name__)


def _verify_cas1(ticket, service):
    """Verifies CAS 1.0 authentication ticket.

    Returns username on success and None on failure.
    """
    params = {'ticket': ticket, 'service': service}
    url = (urljoin(settings.CAS_SERVER_URL, 'validate') + '?' +
           urlencode(params))
    page = urlopen(url)
    try:
        verified = page.readline().strip()
        if verified == 'yes':
            return page.readline().strip()
        else:
            return None
    finally:
        page.close()


def _verify_cas2(ticket, service):
    """Verifies CAS 2.0+ XML-based authentication ticket.

    Returns user's attribute  on success and None on failure.
    """
    try:
        from xml.etree import ElementTree
    except ImportError:
        from elementtree import ElementTree

    params = {'ticket': ticket, 'service': service}
    url = (urljoin(settings.CAS_SERVER_URL, 'serviceValidate') + '?' +
           urlencode(params))
    page = urlopen(url)
    try:
        response = page.read()
        '''Remove \n\t character from response xml'''
        response = re.sub(r'(?m)[\t\n]+', "", response)
        tree = ElementTree.fromstring(response)
        if tree[0].tag.endswith('authenticationSuccess'):
            member_of = []
            access_token = None
            user_name = None
            first_name = None
            last_name = None
            department = None
            for xmlTag in tree[0]:
                if xmlTag.tag.endswith('user'):
                    user_name = xmlTag.text
                elif xmlTag.tag.endswith('firstName'):
                    first_name = xmlTag.text
                elif xmlTag.tag.endswith('lastName'):
                    last_name = xmlTag.text

            user_args = {
                "user_name":user_name,
                "first_name": first_name,
                "last_name": last_name
            }
            
            return user_args
        else:
            return None
    except Exception, e:
        logger.error(e)
    finally:
        page.close()


_PROTOCOLS = {'1': _verify_cas1, '2': _verify_cas2}

if settings.CAS_VERSION not in _PROTOCOLS:
    raise ValueError('Unsupported CAS_VERSION %r' % settings.CAS_VERSION)

_verify = _PROTOCOLS[settings.CAS_VERSION]


class CASBackend(object):

    """CAS authentication backend"""
    def authenticate(self, ticket, service, request):
        """Verifies CAS ticket and gets or creates User object"""
        user = _verify(ticket, service)
        logger.debug("Verified User %s" % user)
        if user is None:
            return None

        return models.SSOUser(**user)
