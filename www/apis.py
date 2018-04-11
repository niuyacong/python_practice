'''
JSON API definition.
'''

import json,logging,inspect,functools

class APIError(Exception):
    '''
    the base APIError which contains error(required), data(optional) and message(optional).
    '''
    def __init__(self,error,data="",messge=""):
        super(APIError,self).__init__(messge)
        self.error=error
        self.data=data
        self.message=messge

class APIValueError(APIError):
    '''
     Indicate the input value has error or invalid. The data specifies the error field of input form.
    '''
    def __init__(self,field,message=''):
        super(APIValueError,self).__init__('value:not found',field,message)


class APIResourceNotFoundError(APIError):
    '''
    Indicate the resource was not found. The data specifies the resource name.
    '''
    def __init__(self,field,message=''):
        super(APIResourceNotFoundError,self).__init__('value:not found',field,message)


class APIPermissionError(APIError):
    '''
    Indicate the api has no permission.
    '''
    def __init__(self,message=''):
        super(APIPermissionError,self).__init__('permission :forbidden ','permission',message)