import time,uuid

from orm import Model,StringField,BooleanFiled,FloatFiled,TextFiled

def next_id():
    return '%015d%s000'%(int(time.time()*1000),uuid.uuid4().hex)

class User(Model):
    __table__="users"
    id=StringField(primary_key=True,default=next_id,ddl="varchar(50)")
    email=StringField(ddl="varchar(50)")
    passwd=StringField(ddl="varchar(50)")
    admin=BooleanFiled()
    name=StringField(ddl="varchar(50)")
    image=StringField(ddl="varchar(500)")
    created_at=FloatFiled(default=time.time)


class Blog(Model):
    __table__="blogs"
    id=StringField(primary_key=True,default=next_id,ddl="varchar(50)")
    user_id=StringField(ddl="varchar(50)")
    user_name=StringField(ddl="varchar(50)")
    user_img=StringField(ddl="varchar(50)")
    name=StringField(ddl="varchar(50)")
    summary=StringField(ddl="varchar(200)")
    content=TextFiled()
    created_at=FloatFiled(default=time.time)


class Comment(Model):
    __table__="comments"
    id=StringField(primary_key=True,default=next_id,ddl="varchar(50)")
    blog_id=StringField(ddl="varchar(50)")
    user_id=StringField(ddl="varchar(50)")
    user_name=StringField(ddl="varchar(50)")
    user_image=StringField(ddl="varchar(500)")
    content=TextFiled()
    created_at=FloatFiled(default=time.time)

# 在编写ORM时，给一个Field增加一个default参数可以让ORM自己填入缺省值，非常方便。并且，缺省值可以作为函数对象传入，在调用save()时自动计算。

# 例如，主键id的缺省值是函数next_id，创建时间created_at的缺省值是函数time.time，可以自动设置当前日期和时间。

# 日期和时间用float类型存储在数据库中，而不是datetime类型，这么做的好处是不必关心数据库的时区以及时区转换问题，排序非常简单，显示的时候，只需要做一个float到str的转换，也非常容易。

# 初始化数据库表

# 如果表的数量很少，可以手写创建表的SQL脚本：schema.sql

# 如果表的数量很多，可以从Model对象直接通过脚本自动生成SQL脚本，使用更简单。

# 测试插入数据
# import orm
# import asyncio 
# async def test(loop):
#     await  orm.create_pool(loop, db='awesome');
#     u=User(name='Test',email='doudou@qq.com',passwd='123',image='about:blank')
#     await u.save()

# loop = asyncio.get_event_loop()
# task = asyncio.ensure_future(test(loop))
# res = loop.run_until_complete(task)
# print(res)




