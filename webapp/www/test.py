import re

_RE_MAIL = re.compile(r'^[\.a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$')

print(_RE_MAIL.match('FWEF22T4T.G42G2G.G24G2.G24G@FWEFWF.FEWFWEF'))

if(_RE_MAIL.match('3g2g.24g2g2@43g3g.ft43t43')):
    print('OK')

print(re.match(r'^[\.a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', '10.16-_8654609@q_-q.co_-m'))