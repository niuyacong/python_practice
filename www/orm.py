# 创建连接池

# 我们需要创建一个全局的连接池，每个HTTP请求都可以从连接池中直接获取数据库连接。
# 使用连接池的好处是不必频繁地打开和关闭数据库连接，而是能复用就尽量复用。

# 连接池由全局变量__pool存储，缺省情况下将编码设置为utf8，自动提交事务：

import asyncio

import aiomysql

import logging;logging.basicConfig(level=logging.INFO)

@asyncio.coroutine
def create_pool(loop,**kw):
    logging.info("create database conntion pool...");
    global __pool
    __pool=yield from aiomysql.create_pool(
        host=kw.get('host','localhost'),
        port=kw.get('port',3306),
        user=kw.get('root','root'),
        password=kw.get('password','111111'),
        db=kw.get('db','test'),
        charset=kw.get('charset','utf8'),
        autocommit=kw.get('autocommit',True),
        maxsize=kw.get('maxsize',10),
        minsize=kw.get('minsizw',1),
        loop=loop
    )
# Select

# 要执行SELECT语句，我们用select函数执行，需要传入SQL语句和SQL参数：

@asyncio.coroutine
def select(sql,args,size=None):
    logging.info(sql,args)
    global __pool
    with(yield from __pool)as conn:
        cur=yield from conn.cursor(aiomysql.DictCursor)
        yield from cur.execute(sql.replace('?','%'),args or ())
        if size:
            rs=yield from cur.fetmany(size)
        else:
            rs=yield from cur.fetchall()
        yield from cur.close()
        logging.info('rows returned %s '%len(rs))
        return rs
# SQL语句的占位符是?，而MySQL的占位符是%s，select()函数在内部自动替换。注意要始终坚持使用带参数的SQL，而不是自己拼接SQL字符串，这样可以防止SQL注入攻击。

# 注意到yield from将调用一个子协程（也就是在一个协程中调用另一个协程）并直接获得子协程的返回结果。

# 如果传入size参数，就通过fetchmany()获取最多指定数量的记录，否则，通过fetchall()获取所有记录。

# Insert, Update, Delete

# 要执行INSERT、UPDATE、DELETE语句，可以定义一个通用的execute()函数，因为这3种SQL的执行都需要相同的参数，以及返回一个整数表示影响的行数：

@asyncio.coroutine
def execute(sql,args):
    logging.info(sql)
    with (yield from __pool)as conn:
        try:
            cur=yield from conn.cursor()
            yield from cur.execute(sql.replace('?','%s'),args)
            affected=cur.rowcount
            yield from cur.close()
            yield from conn.commit()
        except BaseException as e:
            raise ;
        return affected

# execute()函数和select()函数所不同的是，cursor对象不返回结果集，而是通过rowcount返回结果数。
# 定义Model
# ORM
# 定义Model

# 首先要定义的是所有ORM映射的基类Model：
import logging;logging.basicConfig(level=logging.INFO)
import asyncio 

def create_args_string(num):
    L=[];
    for n in range(num):
        L.append('?');
    return ', '.join(L)

# 字段 
class Field(object):
    
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)

# 布尔字段
class BooleanFiled(Field):
    def __init__(self,name=None,default=False):
        super().__init__(name,'boolean',False,default)

# 整数型字段
class IntegerFiled(Field):
    def __init__(self,name=None,primary_key=False,default=0):
        super().__init__(name,'bigint',primary_key,default)

# 浮点型字段
class FloatFiled(Field):
    def __init__(self,name=None,primary_key=False,default=0.0):
        super().__init__(name,'real',primary_key,default)

# text字段
class TextFiled(Field):
    def __init__(self,name=None,primary_key=False,default=None):
        super().__init__(name,'text',primary_key,default)

class ModelMetaclass(type):
    def __new__(cls,name,bases,attrs):
        if name=='Model':
            return type.__new__(cls,name,bases,attrs)
        tableName=attrs.get('__table__',None)or name
        logging.info('found Model : %s(table:%s)'%(name,tableName))
        mappings=dict()
        fileds=[]
        primaryKey=None
        for k,v in attrs.items():
            if isinstance(v,Field):
                logging.info(' found mapping:%s==>%s'%(k,v))
                mappings[k]=v
                if v.primary_key:
                    # 找到主键:
                    if primaryKey:
                        pass
                    primaryKey=k
                else:
                    fileds.append(k)
        if not primaryKey:
            pass
        for k in mappings.keys():
            attrs.pop(k);
        escaped_fields = list(map(lambda f: '`%s`' % f, fileds))
        attrs['__mappings__']=mappings
        attrs['__tables__']=tableName
        attrs['__primary_key__']=primaryKey
        attrs['__fields__']=fileds
        attrs['__select__']= 'select `%s`,%s from `%s`'%(primaryKey,', '.join(escaped_fields),tableName)
        attrs['__insert__']= 'insert into `%s` (%s,`%s`) values (%s)'%(tableName,', '.join(escaped_fields),primaryKey,
        create_args_string(len(escaped_fields)+1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName,
         ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fileds)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)

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

    def getValue(self,key):
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
    async def findAll(cls,where=None,args=None,**kw):
        logging.info('find objects by where clause');
        sql=[cls.__select__]
        if where :
            sql.append('where')
            sql.append(where)
        if args is None:
            args=[]
        orderby=kw.get('orderBy' ,None)
        if orderby:
            sql.append('order by')
            sql.append(orderby)
        limit =kw.get('limit',None)
        if limit:
            sql.append('limit')
            if isinstance (limit,int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit,tuple) and len(limit)==2:
                sql.append('?,?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value :%s '%str(limit))
            rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
            rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    async def find(cls, pk):
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)
        

    async def update(self):
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warn('failed to update by primary key: affected rows: %s' % rows)

    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.warn('failed to remove by primary key: affected rows: %s' % rows)
        


# 有了基本的select()和execute()函数，我们就可以开始编写一个简单的ORM了。

# 设计ORM需要从上层调用者角度来设计。

# 我们先考虑如何定义一个User对象，然后把数据库表users和它关联起来。

# class User(Model):
#     __table__='user'

#     id= IntegerFiled(primary_key=True)

#     name=StringField()

# 注意到定义在User类中的__table__、id和name是类的属性，不是实例的属性。
# 所以，在类级别上定义的属性用来描述User对象和表的映射关系，而实例属性必须通过__init__()方法去初始化，所以两者互不干扰：

# 创建实例:

# async def main(loop):
#     await create_pool(loop)
#     user = User(id=123,name='niu')
#     await user.remove()
#     return user.name

# loop = asyncio.get_event_loop()
# task = asyncio.ensure_future(main(loop))
# res = loop.run_until_complete(task)
# print(res)