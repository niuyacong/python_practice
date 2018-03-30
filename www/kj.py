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
        post=kw.get('post',3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
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
            yield from cur.execute(sql.replace('?','%S'),args)
            affected=cur.rowcount
            yield from cur.close()
        except BaseException as e:
            raise;
        return affected

# execute()函数和select()函数所不同的是，cursor对象不返回结果集，而是通过rowcount返回结果数。


# ORM

# 有了基本的select()和execute()函数，我们就可以开始编写一个简单的ORM了。

# 设计ORM需要从上层调用者角度来设计。

# 我们先考虑如何定义一个User对象，然后把数据库表users和它关联起来。

from orm import Model,StringField,IntegerField

class User(Model):
    __table__='users'

    id= IntegerField(primary_key=True)

    name=StringField()

# 注意到定义在User类中的__table__、id和name是类的属性，不是实例的属性。
# 所以，在类级别上定义的属性用来描述User对象和表的映射关系，而实例属性必须通过__init__()方法去初始化，所以两者互不干扰：

# 创建实例:
user=User(id=123,name='niu')
# 存入数据库:
user.insert();