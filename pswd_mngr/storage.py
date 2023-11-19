import uuid
import sqlite3
from pswd_mngr.models import PasswordItemBase, PasswordItemDB, PasswordItemOut
from datetime import datetime as dt


class PasswordStorage:
    def __init__(self):
        self.conn = sqlite3.connect("passwords.db", check_same_thread=False)

    def save_password(self, item: PasswordItemBase):
        item = PasswordItemDB.to_db(item)

        cur = self.conn.cursor()
        cur.execute(f"""
            INSERT INTO password VALUES (
            '{item.id}',
            NULL,
            '{item.name}',
            '{item.site}',
            '{item.password}',
            {int(item.created_at.timestamp())},
            {int(item.updated_at.timestamp())})
            """)
        self.conn.commit()

    def get_password(self, password_id: str) -> PasswordItemOut:
        cur = self.conn.cursor()
        res = cur.execute(f"SELECT * FROM password WHERE id='{password_id}'").fetchone()

        return PasswordItemOut.from_db(res)

    def get_passwords(self) -> list[PasswordItemBase]:
        cur = self.conn.cursor()
        res = cur.execute("SELECT * FROM password").fetchall()

        return [PasswordItemOut.from_db(item) for item in res]

    def update_password(self, password_id: str, new_password: str) -> PasswordItemOut | dict:
        cur = self.conn.cursor()
        cur.execute(f'''
            UPDATE password SET
            password = '{new_password}',
            updated_at = {int(dt.now().timestamp())}
            WHERE id='{password_id}'
            ''')
        self.conn.commit()

        if cur.rowcount == 1:
            return self.get_password(password_id)
        else:
            return {"error": "Password updated failed"}

    def del_password(self, password_id: str) -> dict:
        cur = self.conn.cursor()
        cur.execute(f"DELETE FROM password WHERE id='{password_id}'")
        self.conn.commit()

        if cur.rowcount == 1:
            return {"message": "Password removed successfully"}
        else:
            return {"error": "Password deletion failed"}
