from webapp.www.web import get
from webapp.www.tables import User

@get('/')
def index(request):
    users = yield from User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }