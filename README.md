###Python-CAS-Client
'python-cas-client' is a client plugin for django based application to authenticate via CAS (Central authentication service). It support all CAS version including CAS 1.0. 
It includes a middleware that intercepts the call on '/login' and '/logout' uri and forward them to CASified version.
###Configuration
In 'settings.py' , add CAS server url in CAS_SERVER_URL:

CAS_SERVER_URL = "Add you CAS server url Example- https://www.localcas.com/cas"
###Installation 
Clone this repository and integrate the code with your python django-application.


###How it works

Step - 1: The resource in application which required authentication, add decorator 'login_required' import from auth_decorator.py before accessing the resource. 
example:

````python
from auth_decorator import login_required
@login_required(login=True)
def access_authenticated_resource(self):
    pass
````
    
Step -2 : When the browser send any request to authenticated resource, it first check whether 
          the given request is authenticated or not. So, initially, there is no session/cookies maintain by application, so decorator function call '/login' function from views.py.

Step -3 : On views.py, login function, call CAS login url with appropriate service and next parameter.

Step -4: After step-3, User's get a CAS login will ask to enter the credential. After successfull credential, CAS will generate a Service-Ticket, and redirect to '/login' url of application.

Step -5: Again login function of views.py call, this time it find the ticket in the url, and call '/serviceValidate' method of CAS with 'service' and 'ticket' parameter.

Step-6: CAS get the /serviceValidate response, and on valid 'ticket' & 'service' param, it send the user's attribute field in response.

Step -7: CAS-plugin get the user's reponse and store it in User's SSO model. And also create a secure cookies which store the user's aatribute with signature and expiry time. Expiry time decide the life time of cookies.

Step -8: During Step-7, authicated=True will be set, when cookies will be create.
