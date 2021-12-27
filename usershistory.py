import sqlite3


class UsersLog:

    def __init__(self, dbname="users.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        tbl_stmt = '''CREATE TABLE IF NOT EXISTS usersLog (
                    user_id integer,
                    command text not null,
                    datetime text
                    hotels text)'''
        user_id_idx = '''CREATE INDEX IF NOT EXISTS usersIndex 
                        ON usersLog (user_id ASC)'''
        self.conn.execute(tbl_stmt)
        self.conn.execute(user_id_idx)
        self.conn.commit()

    def add_users_command(self, user_id: int, command: str,
                          datetime: str, hotels: str):
        stmt = '''INSERT INTO 
                usersLog (user_id, command, datetime, hotels) 
                VALUES (?, ?, ?, ?)'''
        args = (user_id, command, datetime, hotels)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_user(self, user_id: int):
        stmt = "DELETE FROM usersLog WHERE user_id = (?)"
        args = (user_id,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_commands_for_user(self, user_id: int) -> str:
        stmt = "SELECT user_id FROM usersLog WHERE user_id = (?)"
        args = (user_id,)
        return ', '.join(x[0] for x in self.conn.execute(stmt, args))

    # def is_user_is_known(self, user_id: int):
    #     stmt = "SELECT * FROM usersIndex WHERE user_id = (?)"
    #     args = (user_id,)

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.conn.close()
