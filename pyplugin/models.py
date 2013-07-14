
class SSOUser(object):
    
    def __init__(self, **kwargs):
        self._kwargs = {}
        self._kwargs.update(kwargs)
        
        if 'authenticated' in self._kwargs:
            self._kwargs.pop('authenticated')
        
        self.username = kwargs.get('user_name', None)
        self.first_name = kwargs.get('first_name', None)
        self.last_name = kwargs.get('last_name', None)
        self.authenticated = kwargs.get('authenticated', False)
    
    def get_cookie_args(self):
        return self._kwargs
    
    def get_username(self):
        return self.username

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name
        
    def is_anonymous(self):
        return not self.is_authenticated()

    def is_authenticated(self):
        return self.authenticated

    def set_password(self, raw_password):
        raise Exception("Passwords for SSO users cannot be changed in applications")

    def check_password(self, raw_password):
        raise Exception("Passwords for SSO users cannot be checked in applications")

    def set_unusable_password(self):
        raise Exception("Passwords for SSO users cannot be changed in applications")
    
    def has_usable_password(self):
        return True
