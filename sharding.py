import sqlite3
from sqlite3 import Error
import uuid
global games_table_query, users_table_query
games_table_query="""CREATE TABLE games(user_id INTEGER NOT NULL, game_id INTEGER NOT NULL, finished DATE DEFAULT CURRENT_TIMESTAMP, guesses INTEGER, won BOOLEAN, PRIMARY KEY(user_id, game_id), FOREIGN KEY(user_id) REFERENCES users(user_id)); """
users_table_query = """ CREATE TABLE users( user_id INTEGER PRIMARY KEY, username VARCHAR UNIQUE);"""

def open_db(name):
    conn = sqlite3.connect(name)
    conn.row_factory = sqlite3.Row
    return conn

def copy_table(table, src, dest):
    global games_table_query
    sc= src.execute('SELECT * FROM %s' %table)
    ins = None
    dc = dest.cursor()
    dc.execute('DROP TABLE IF EXISTS %s;' %table)
    if table == "games":
        dc.execute(games_table_query)
    elif table == "users":
        dc.execute(users_table_query)
    for row in sc.fetchall():
        if not ins:
            cols = tuple([k for k in row.keys() if k != 'id'])
            ins = 'INSERT OR REPLACE INTO %s %s VALUES (%s)' % (table, cols,','.join(['?']*len(cols)))
        c=[row[c] for c in cols]
        dc.execute(ins, c)

    dest.commit()

# src_conn = open_db("populated.db")
# dest_conn = open_db("game_db.db")

# copy_table('games',src_conn, dest_conn)

# src_conn = open_db("populated.db")
# dest_conn = open_db("user_db.db")

# copy_table('users', src_conn, dest_conn)

def add_UUID(db):
    conn= open_db(db)
    sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
    sqlite3.register_adapter(uuid.UUID, lambda u: memoryview(u.bytes_le))
    conn= sqlite3.connect('game_db.db', detect_types= sqlite3.PARSE_DECLTYPES)

    c=conn.cursor()
    if c.execute("SELECT length(guid) AS column_size FROM games"):
        print("Column alredy exists")
    else:
        c.execute('ALTER TABLE games ADD COLUMN guid GUID')

    # for row in c.execute('SELECT * FROM games'):
    for i in range(1,1000000):
        data = [uuid.uuid4(),i]
        c.execute('UPDATE games SET guid = (?) WHERE game_id = (?)',data)
    # c.execute('CREATE TABLE uniqueID (guid GUID PRIMARY KEY)')
    # for i in range(1,1000000):
    #     data = [uuid.uuid4()]
    #     c.execute('INSERT INTO uniqueID VALUES (?)',data)

    conn.commit()


    # print('Result data:')


add_UUID('game_db.db')