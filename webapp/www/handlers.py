from webapp.www.web import get
from webapp.www.tables import User

@get('/')
def index(request):
    users = yield from User.findAll()
    if users is not None:
        return {
        '__template__': 'test.html',
        'users': users
        }
    return {
        '__template__': 'test1.html'
    }