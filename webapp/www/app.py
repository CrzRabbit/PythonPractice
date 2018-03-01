import logging; logging.basicConfig(level=logging.INFO)
import asyncio, os, time, json
from datetime import datetime
from aiohttp import web
from jinja2 import Environment, FileSystemLoader
from webapp.www.orm import *
from webapp.www.web import *

def init_jinja2(app, **kw):
    logging.info('Init jinja2...')
    options = dict(
        autoescape = kw.get('autoescape', True),
        block_start_string = kw.get('block_start_string', '{%'),
        block_end_string = kw.get('block_end_string', '%}'),
        variable_start_string = kw.get('variable_start_string', '{{'),
        variable_end_string = kw.get('variable_end_string', '}}'),
        auto_reload = kw.get('auto_reload', True)
    )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('Set jinja2 template path: {}'.format(path))
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env

@asyncio.coroutine
def logger_factory(app, handler):
    def logger(request):
        logging.info('Request: {0} {1}'.format(request.method, request.path))
        return (yield from handler(request))
    return logger

@asyncio.coroutine
def data_factory(app, handler):
    def parse_data(requst):
        if requst.method == 'POST':
            if requst.content_type.startwith('application/json'):
                requst.__data__ = yield from requst.json()
                logging.info('data from json: {0}.'.format(requst.__data__))
            if requst.content_type.startwith('application/x-www-form-urlencoded'):
                requst.__data__ = yield from requst.post()
                logging.info('data form form: {0}.'.format(requst.__data__))
        return (yield from handler(requst))
    return parse_data

@asyncio.coroutine
def response_factory(app, handler):
    def response(request):
        logging.info('Response handler...')
        r = yield from handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utr-8'))
            resp.content_type = 'text/html;charset=utr-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r, int) and r > 100 and r < 600:
            return web.Response(r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t > 100 and t < 600:
                return web.Response(t, str(m))
        #default
        resp = web.Response(body=r.encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp
    return response

def datatime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'{0}分钟前'.format(delta/60)
    if delta < 86400:
        return u'{0}小时前'.format(delta/3600)
    if delta < 604800:
        return u'{0}天前'.format(delta/86400)
    dt = datetime.fromtimestamp(t)
    return u'{0}年{1}月{2}日'.format(dt.year, dt.month, dt.day)

@asyncio.coroutine
def init(loop):
    yield from create_pool(loop=loop, host='127.0.0.1', user='root', password='root', database='awesome')
    app = web.Application(loop=loop, middlewares=[
        logger_factory, response_factory
    ])
    init_jinja2(app, filters=dict(datetime=datatime_filter))
    add_routes(app, 'handlers')
    add_static(app)
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('Server is running at {0}:{1}'.format('127.0.0.1', 9000))
    return srv

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()