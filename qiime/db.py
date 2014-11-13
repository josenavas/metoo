import sqlite3


def _initialize_db():
    conn = sqlite3.connect('qiime2.db')
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS artifact "
              "(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT, "
              " data BLOB)")

    c.close()
    conn.commit()
    return conn


def get_connection():
    return _connection


# TODO this should be specified in a config file and we should support multiple
# types of databases
_connection = _initialize_db()
