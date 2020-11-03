"""
Storing NumPy arrays in SQLAlchemy databases
"""

import sqlalchemy as sql
from sqlalchemy.engine import Engine
import random, struct, time, os

chunk = 2048

# timing functions
t = [0]
def tic():
    t[0] = time.time()

def toc(msg=''):
    print '%0.3f s elapsed, %s' % (
            time.time() - t[0], msg)

# use fk constraints in sqlite
@sql.event.listens_for(Engine, "connect")
def set_sqlite_pragma(conn, _):
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# fn for gen & manip arrays
def randn(n):
    return [random.gauss(0.0, 1.0) for i in xrange(n)]

def pack(xs):
    return struct.pack('d' * len(xs), *xs)

def unpack(s):
    return struct.unpack('d' * (len(s) / 8), s)

def parts(xs, size):
    i = -1
    for i in range(len(xs) / size):
        yield xs[i * size:(i + 1) * size]
    yield xs[(i + 1) * size:]

def test1():
    xss = list(parts(randn(7), 3))
    print xss
    print [unpack(pack(xs)) for xs in xss]

# setup tables
metadata = sql.MetaData()
array = sql.Table('array', metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('ndim', sql.Integer, nullable=False),
    sql.Column('type', sql.String(1), nullable=False), )

array_dim = sql.Table('array_dim', metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('array_id', None, sql.ForeignKey('array.id'), nullable=False),
    sql.Column('dim', sql.Integer , nullable=False ),
    sql.Column('size', sql.Integer , nullable=False ) )

array_data = sql.Table('array_data', metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('array_id', None, sql.ForeignKey('array.id'), nullable=False),
    sql.Column('len', sql.Integer, nullable=False),
    sql.Column('data', sql.Binary, nullable=False) )

def put(conn, xs):
    r = conn.execute(array.insert(), ndim=1, type='d')
    array_id = r.inserted_primary_key[0]
    conn.execute(array_dim.insert(), array_id=array_id, dim=1, size=len(xs))
    conn.execute(array_data.insert(), [
      {'array_id': array_id, 'len': len(part), 'data': pack(part)}
      for part in parts(xs, chunk)])
    return array_id

def get(conn, array_id):
    # ftm, assume vectors
    q = sql.select([array_data]).where(array_data.c.array_id == array_id)
    r = conn.execute(q)
    data = []
    for _, _, len, bs in r:
        data += list(unpack(bs))
    return data

if os.path.exists('num.db'):
    os.unlink('num.db')

engine = sql.create_engine('sqlite:///num.db', echo=True)
metadata.create_all(engine)
conn = engine.connect()
n = 370 * (256 * 60)
print n

tic()
x = randn(n)
toc('randn')

tic()
x_id = put(conn, x)
toc('put')

tic()
xq = get(conn, x_id)
toc('get')

print all([xi==xqi for xi, xqi in zip(x, xq)])

conn.close()

import os

dbsize = os.stat('num.db').st_size
print 'db disk size' , dbsize / 1024, 'K'
print dbsize / 8.0 / n * 100 - 100, '% overhead'

import numpy as np

x_a = np.array(x)

tic()
np.save('x.npy', x_a)
toc('save np')

tic()
np.load('x.npy')
toc('load np')

import code
code.interact(local=locals())
