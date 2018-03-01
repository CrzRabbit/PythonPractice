from webapp.www.orm import *
from webapp.www.tables import *

def test(loop):
    yield from create_pool(loop=loop,user='root',password='root',database='awesome')
    u1 = User(name='test1',email='test1@test.com',passwd='test1',image='about:blank')
    yield from u1.save()
    u2 = User(name='test2',email='test2@test.com',passwd='test2',image='about:blank')
    yield from u2.save()
    u3 = User(name='test3',email='test3@test.com',passwd='test3',image='about:blank')
    yield from u3.save()
    u4 = User(name='test4',email='test4@test.com',passwd='test4',image='about:blank')
    yield from u4.save()
    #yield from u1.clear()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.run_forever()