import sqlite3


class UsersLog:
    def __init__(self, dbname="users_history.sqlite"):
        self.dbname = dbname
        self.connection = sqlite3.connect(dbname)
        self.cursor = self.connection.cursor()

    def setup(self):
        """Creating a table and index if not exist"""
        tbl_stmt = '''CREATE TABLE IF NOT EXISTS usersLog (
                    user_id integer,
                    command text not null,
                    datetime text,
                    hotels text)'''
        user_id_idx = '''CREATE INDEX IF NOT EXISTS usersIndex 
                        ON usersLog (user_id ASC)'''
        with self.connection:
            self.cursor.execute(tbl_stmt)
            self.cursor.execute(user_id_idx)

    def add_user_command(self, user_id: str, command: str,
                          datetime: str, hotels: str) -> None:
        stmt = '''INSERT INTO 
                usersLog (user_id, command, datetime, hotels) 
                VALUES (?, ?, ?, ?)'''
        args = (user_id, command, datetime, hotels)
        with self.connection:
            self.cursor.execute(stmt, args)

    def delete_user(self, user_id: int):
        stmt = "DELETE FROM usersLog WHERE user_id = (?)"
        args = (user_id,)
        self.connection.execute(stmt, args)
        self.connection.commit()

    def get_commands_for_user(self, user_id: int) -> list:
        stmt = "SELECT * FROM usersLog WHERE user_id = (?)"
        args = (user_id,)
        with self.connection:
            result: list = self.cursor.execute(stmt, args).fetchall()
        return result

