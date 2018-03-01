import asyncio
import aiomysql
import logging; logging.basicConfig(level=logging.INFO)

@asyncio.coroutine
def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global __pool
    __pool = yield from aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['database'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )

@asyncio.coroutine
def select(sql, args, size=None):
    #logging(create_tables, args)
    global __pool
    with (yield from __pool) as conn:
        cur = yield from conn.cursor(aiomysql.DictCursor)
        yield from cur.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = cur.fetchmany(size)
        else:
            rs = cur.fetchall()
        yield from cur.close()
        logging.info('Rows returned: {0}'.format(len(rs)))
        return rs

@asyncio.coroutine
def execute(sql, args):
    print(sql.replace('?', '%s'))
    print(args)
    with (yield from __pool) as conn:
        try:
            cur = yield from conn.cursor()
            yield from cur.execute(sql.replace('?', '%s'), args or ())
            affected = cur.rowcount
            yield from cur.close()
        except BaseException as e:
            raise
        return affected

class ModelMetaClass(type):

    def __new__(cls, name, bases, attrs):
        #排除Model类本身
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        #获取tablename
        tableName = attrs.get('__table__', None) or name
        logging.info('Find model {0} (table {1}).'.format(name, tableName))
        #获取所有field和主键名
        mappings = dict()
        fields = []
        primary_key = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v
                if v.primary_key:
                    if primary_key:
                        raise RuntimeError('Duplicate primary key for field: {0}.'.format(k))
                    primary_key = k
                else:
                    fields.append(k)

        if not primary_key:
            raise RuntimeError('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '{0}'.format(f), fields))
        attrs['__mappings__'] = mappings        #映射关系
        attrs['__table__'] = tableName          #表名
        attrs['__primary_key__'] = primary_key  #主键
        attrs['__fields__'] = fields            #其他属性
        #构造默认的select, insert, update, delete语句
        attrs['__select__'] = 'SELECT {0}, {1} FROM {2} '.format(primary_key, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'INSERT INTO {0} ({1}, {2}) VALUES ({3})'.format(tableName, ', '.join(escaped_fields), primary_key, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'UPDATE {0} set {1} WHERE {2}=?'.format(tableName, ', '.join(map(lambda f: '{0}=?'.format(mappings.get(f).name or f), fields)), primary_key)
        attrs['__delete__'] = 'DELETE FROM {0} WHERE {1}=?'.format(tableName, primary_key)
        attrs['__delete_all__'] = 'DELETE FROM {0}'.format(tableName)
        return type.__new__(cls, name, bases, attrs)

def create_args_string(len):
    args = list()
    for i in range(len):
        args.append("?")
    return ', '.join(args)

class Model(dict, metaclass=ModelMetaClass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' has no key {0}.".format(key))

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('Using default value for {0}: {1}'.format(key, value))
                setattr(self, key, value)
        return value

    @classmethod
    @asyncio.coroutine
    def find(cls, pk):
        rs = yield from select('%s where `%s`=?'.format(cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    @asyncio.coroutine
    def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append('{0}'.format(self.getValueOrDefault(self.__primary_key__)))
        rows = yield from execute(self.__insert__, args)
        if rows != 1:
            logging.warning('Insert value failed, affected rows: {0}'.format(rows))

    @asyncio.coroutine
    def update(self):
        pass
        # args = list()
        # for i in range(len(self.__fields__) + 1):
        #     args.append(' ')
        # rows = yield from execute(self.__update__, args)
        # if rows == 0:
        #     logging.warning('Updata value failed, no rows affected.')

    @asyncio.coroutine
    def delete(self):
        pass

    @asyncio.coroutine
    def clear(self):
        args = list()
        rows = yield from execute(self.__delete_all__, args)
        logging.warning('Clear completed, {0} rows affected'.format(rows))

class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<{0} {1}: {2}>'.format(self.__class__.__name__, self.column_type, self.name)

class StringField(Field):

    def __init__(self, name = None, primary_key = False, default = None, ddl = 'varchar(100)'):
        super().__init__(name, ddl, primary_key, default)

class IntegerField(Field):

    def __init__(self, name = None, primary_key = False, default = None, ddl = 'bigint'):
        super().__init__(name, ddl, primary_key, default)

class BooleanField(Field):

    def __init__(self, name = None, primary_key = False, default = False, ddl = 'boolean'):
        super().__init__(name, ddl, primary_key, default)

class FloatField(Field):

    def __init__(self, name = None, primary_key = False, default = None, ddl = 'real'):
        super().__init__(name, ddl, primary_key, default)

class TextField(Field):

    def __init__(self, name = None, primary_key = False, default = '', ddl = 'text'):
        super().__init__(name, ddl, primary_key, default)