from  coroweb import get
import logging;logging.basicConfig(level=logging.INFO)

@get('/aa')
def test():
    pass

if __name__=='main':
    print(test.__route__)