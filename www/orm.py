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
        
    )
