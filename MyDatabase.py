import os


from sqlobject import *
from options import Options


prefs = Options().Prefs()

if prefs['db'] == 1:
    database = 'sqlite'
elif prefs['db'] == 2:
    database = 'postgresql'
elif prefs['db'] == 3:
    database = 'firebird'
elif prefs['db'] == 4:
    database = 'mysql'
else:
    database = None


if database:
    conn = connectionForURI("%s://%s" % \
            (database, os.path.expanduser("~/.abeni/abeni_sqlite_db")))
else:
    conn = None

class Ebuild(SQLObject):

    """Record containing notes/bugzilla info"""

    _connection = conn

    _columns = [StringCol('cpvr', length=60, alternateID=True, notNull=1),
                IntCol('bugz', notNull=0),
                StringCol('notes', length=2048, notNull=0)]

try:
    Ebuild.createTable(ifNotExists=True)
except:
    pass

