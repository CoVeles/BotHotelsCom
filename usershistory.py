import datetime
import sqlite3
from loguru import logger


class User:
    """
    This class contains a dictionary of users of session
    Every user has a state of step and requirement parameters for
    requests to Hotels API
    """
    users_dct = dict()

    def __init__(self, user_id: int):
        self.user_id: int = user_id
        self.command: str = 'start'
        self.state: int = 0
        self.lang_id: int = 0
        self.req_params = dict()
        User.add_user(user_id, self)

    @classmethod
    def add_user(cls, user_id: int, user: 'User') -> None:
        user.init_req_params()
        cls.users_dct[user_id] = user
        logger.info(f'User {user_id} is added to class dict')

    @classmethod
    def get_user(cls, user_id: int) -> 'User':
        return cls.users_dct.get(user_id)

    def set_state(self, state: int) -> None:
        self.state = state

    def init_req_params(self) -> None:
        """Reset user parameters"""
        self.state = 0
        self.req_params: dict = {'loc_id': '', 'hotels_amount': 0,
                                 'price_min': 0, 'price_max': 0,
                                 'distance': 0, 'pictures': 0,
                                 'check_in': '', 'days': 1}


class UserHistory:
    def __init__(self, dbname="users_history.sqlite"):
        self.dbname = dbname
        logger.info('Attempt to create a DB file')
        self.connection = sqlite3.connect(dbname)
        self.cursor = self.connection.cursor()

    def setup(self) -> None:
        """Creating a table and index if not exist"""
        tbl_stmt = '''CREATE TABLE IF NOT EXISTS userCommands (
                    user_id integer,
                    command text not null,
                    datetime text,
                    hotels text)'''
        user_id_idx = '''CREATE INDEX IF NOT EXISTS commandsIndex 
                        ON userCommands (user_id ASC)'''
        logger.info('Attempt to create tables for history')
        with self.connection:
            self.cursor.execute(tbl_stmt)
            self.cursor.execute(user_id_idx)

    def add_user_command(self, user_id: int, command: str,
                          datetime: str, hotels: str) -> None:
        stmt = '''INSERT INTO 
                userCommands (user_id, command, datetime, hotels) 
                VALUES (?, ?, ?, ?)'''
        args = (user_id, command, datetime, hotels)
        logger.info('Attempt to add user command to history')
        try:
            with self.connection:
                self.cursor.execute(stmt, args)
        except Exception as e:
            logger.error(f'DB error: {e}')

    # def delete_user(self, user_id: int) -> None:
    #     stmt = "DELETE FROM userCommands WHERE user_id = (?)"
    #     args = (user_id,)
    #     self.connection.execute(stmt, args)
    #     self.connection.commit()

    def get_commands_for_user(self, user_id: int) -> list:
        stmt = "SELECT * FROM userCommands WHERE user_id = (?)"
        args = (user_id,)
        logger.info('Attempt to get user commands from history')
        result = []
        try:
            with self.connection:
                result: list = self.cursor.execute(stmt, args).fetchall()
        except Exception as e:
            logger.error(f'DB error: {e}')
        finally:
            return result

