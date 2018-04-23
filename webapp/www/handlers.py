# from PythonPractice.webapp.www.web import get, post
# from PythonPractice.webapp.www.tables import User, Blog
# from PythonPractice.webapp.www.apierror import *
# from PythonPractice.webapp.conf.config import *
from webapp.www.web import get, post
from webapp.www.tables import User, Blog
from webapp.www.apierror import *
from webapp.conf.config import *
from aiohttp import web
import time
import re
import hashlib
import json
import uuid
import asyncio
import logging

def next_id():
    return '{0:0>15}{1}000'.format(int(time.time() * 1000), uuid.uuid4().hex)

def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError

def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs['session']['secret']

def user2cookie(user, max_age):
    # build cookie str by user.
    expires = str(int(time.time() + max_age))
    s = '{0}-{1}-{2}-{3}'.format(user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

@asyncio.coroutine
def cookie2user(cookie_str):
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = yield from User.find(uid)
        if user is None:
            return None
        s = '{0}-{1}-{2}-{3}'.format(user.id, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

@get('/')
def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time() - 3600),
        Blog(id='1', name='Learn Swift', summary=summary, created_at=time.time() - 7200)
    ]
    user = request.__user__
    return {
        '__template__': 'blogs.html',
        'blogs': blogs,
        'user': user
    }

#register
@get('/register')
def register(request):
    return {
        '__template__': 'register.html'
    }

_RE_MAIL = re.compile(r'^[\.a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

@post('/register')
def api_resister_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_MAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = yield from User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register: failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd ='%s: %s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravtar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    yield from users.save()
    #make session cookie
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

@post('/api/users')
def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_MAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = yield from User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '{0}:{1}'.format(email, passwd)
    print(passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=passwd,
                image='http://www.gravatar.com/avatar/{0}?d=mm&s=120'.format(hashlib.md5(email.encode('utf-8')).hexdigest()))
    yield from user.save()
    #make session cookie
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

#singin
@get('/signin')
def signin(request):
    return {
        '__template__': 'signin.html'
    }

@post('/api/authenticate')
def atuthenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password')
    users = yield from User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    #check password
    sha1 = hashlib.sha1()
    sha1.update(user.email.encode('utf-8'))
    sha1.update(b':')
    sha1.update(user.passwd.encode('utf-8'))
    print(passwd)
    print(user.passwd)
    if passwd != user.passwd:
        raise APIValueError('passwd', 'Wrong password')
    #authenticate ok
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r

@get('/manage/create')
def manage_create_blog(request):
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs'
    }

@get('/api/blogs/{id}')
def api_get_blog(request):
    return {
        '__template__': 'manage_blog_edit.html',
        'id': id,
        'action': '/api/blogs'
    }

@post('/api/blogs')
def api_create_blog(request, *, name, summary, content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content connot be empty.')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image,
                name=name.strip(), summary=summary.strip(), content=content.strip())
    yield from blog.save()
    return blog