# The middle ware and auth backends should be added to 
# Django settings files

# The contract is that once a user is authenticated and logs following conditions
# will hold true
# 1. request.user is populated
# 2. request.user.security_groups is populated


from pyplugin.middleware import CASMiddleware
from pyplugin.backends import CASBackend

from pyplugin.views import login
from pyplugin.views import logout


__all__ = ['CASMiddleware','CASBackend', 'login', 'logout']
