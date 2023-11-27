import sqlite3
from datetime import datetime as dt
from sqlite3 import IntegrityError

from fastapi.security import OAuth2PasswordRequestForm

from pswd_mngr.models import PasswordItemDB, PasswordItemOut, UserDB, UserOut, UserIn


class StorageError(Exception):
    pass


class DuplicateError(StorageError):
    pass


class PasswordStorage:
    def __init__(self):
        self.conn = sqlite3.connect("passwords.db", check_same_thread=False)

    def save_password(self, item: PasswordItemDB):
        cur = self.conn.cursor()
        try:
            cur.execute(f"""
                INSERT INTO password VALUES (
                '{item.uuid}',
                {item.user_id},
                '{item.name}',
                '{item.site}',
                '{item.password}',
                {int(item.created_at.timestamp())},
                {int(item.updated_at.timestamp())})
                """)
        except IntegrityError:
            raise DuplicateError(f"Password for '{item.name}' already exists. User ID {item.user_id}")

        self.conn.commit()
        return self.get_password(item.uuid, item.user_id)

    def get_password(self, password_id: str, user_id: int) -> PasswordItemOut:
        cur = self.conn.cursor()
        res = cur.execute(f"SELECT * FROM password WHERE id='{password_id}' AND user_id={user_id}").fetchone()

        if res is None:
            raise Exception(f"Record with password id={password_id} and user_id={user_id} not found.")

        return PasswordItemOut.from_db(res)

    def get_passwords(self, user_id: int) -> list[PasswordItemOut]:
        cur = self.conn.cursor()
        res = cur.execute(f"SELECT * FROM password WHERE user_id={user_id}").fetchall()

        return [PasswordItemOut.from_db(item) for item in res]

    def update_password(self, password_id: str, new_password: str, user_id: int) -> PasswordItemOut | None:
        cur = self.conn.cursor()

        cur.execute(f'''
            UPDATE password SET
            password = '{new_password}',
            updated_at = {int(dt.now().timestamp())}
            WHERE id='{password_id}' AND user_id={user_id}
            ''')
        self.conn.commit()

        return self.get_password(password_id, user_id) if cur.rowcount == 1 else None

    def del_password(self, password_id: str, user_id: int) -> int:
        cur = self.conn.cursor()
        cur.execute(f"DELETE FROM password WHERE id='{password_id}' AND user_id={user_id}")
        self.conn.commit()
        return cur.rowcount

    def create_user(self, user: UserIn) -> UserDB:
        cur = self.conn.cursor()

        try:
            cur.execute(f"""
                INSERT INTO users (name, password) VALUES (
                '{user.name}',
                '{user.password}')
                """)
        except IntegrityError:
            raise DuplicateError(f"Username: {user.name} already exists.")

        self.conn.commit()

        res = cur.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1").fetchone()

        return UserDB.from_db(res)

    def get_user_by_name(self, user_name) -> UserDB:
        cur = self.conn.cursor()
        res = cur.execute(f'''
            SELECT * FROM users WHERE
            name='{user_name}'
            ''').fetchone()

        return UserDB.from_db(res) if res else None
