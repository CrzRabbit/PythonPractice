from webapp.www.orm import *
from webapp.www.tables import *

def test(loop):
    yield from create_pool(loop=loop,user='root',password='root',database='awesome')
    u = User(name='test3',email='test4@test.com',passwd='test',image='about:blank')
    yield from u.save()
    yield from u.update()
    yield from u.remove()
    yield from u.clear()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.run_forever()