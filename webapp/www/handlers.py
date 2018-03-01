from webapp.www.web import *
from webapp.www.tables import *

@get('/')
def index(request):
    users = yield from User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }