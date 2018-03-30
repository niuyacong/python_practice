# 定义Model

# 首先要定义的是所有ORM映射的基类Model：
import logging;logging.basicConfig(level=logging.INFO)


def create_args_string(num):
    L=[];
    for n in range(num):
        L.append('?');
    return ', '.join(L)
        
class Filed(object):
    def __init__(self,name,column_type,primary_key,default):
        self.name=name;
        self.column_type=column_type;
        self.primary_key=primary_key;
        self.default=default; 

class Model(dict,metaclass=ModelMetaclass):
    def __init__(self,**kw):
        super(Model,self).__init__(**kw)
    def __getattr__(self,key):
        try:
            return self[key]
        except  KeyError:
            raise AttributeError(r"'Model' object has no attrbute '%s'"%key)
    def __setattr__(self,key,value):
        self[key]=value

    def getValue(self,value):
        return getattr(self,key,None)

    def getValueOrDefault(self,key):
        value=getattr(self,key,None)
        if value is None:
            filed=self.__mappings__[key]
            if filed.default is not None:
                value=filed.default() if callable(filed.default)else filed.default
                logging.debug('using default value for %s : %s'%(key,str(value)))
                setattr(self,key,value)
        return value;
    
    @classmethod

