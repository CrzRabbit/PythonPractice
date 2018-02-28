from WebApp.www.ORM import *
from WebApp.www.tables import *

def test():
    loop = asyncio.get_event_loop()
    yield from create_pool(loop, user='root', password='root', database='awesome')
    user = User(name='test', email='fewfew@few.com', passwd='314355', image='about:blank')
    yield from user.save()

for x in test():
    pass