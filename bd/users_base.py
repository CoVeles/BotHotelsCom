import sqlite3
from pathlib import Path


class UsersBase:
    def __init__(self, db_path):
        self.db = Path(db_path)
        print(self.db)
        try:
            self.db.resolve(strict=True)
        except FileNotFoundError:
            print("Database not found, trying to create a new one.")
            try:
                self.init_sqlite()
            except Exception as e:
                print("Error when creating database : ", e.__repr__(), e.args)
                pass
            else:
                print("Success.")

    def sqlite_connect(self):
        conn = sqlite3.connect(self.db, check_same_thread=False)
        conn.execute("pragma journal_mode=wal;")
        return conn

    def init_sqlite(self):
        conn = self.sqlite_connect()
        c = conn.cursor()
        c.execute(
            '''CREATE TABLE user_hist 
            (id integer primary key, 
            user_id integer, 
            user_name text, 
            user_surname text, 
            town_search text)'''
        )
        conn.commit()
        conn.close()
        return
