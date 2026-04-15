import sqlite3
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy import MetaData

# create an engine  that stores data in memory (instead of a file on disk)
engine = create_engine('sqlite:///:memory:', echo=True)

metadata = MetaData()




# database file
database = './test.db'
# create a database connection
@contextmanager
def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    yield conn
    conn.rollback()
    conn.close()
