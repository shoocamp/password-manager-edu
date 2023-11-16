import uuid
import sqlite3
from pswd_mngr.models import PasswordItemBase, PaaswordItemDB, PasswordItemOut


class PasswordStorage:
    def __init__(self):
        self.conn = sqlite3.connect("passwords.db", check_same_thread=False)

    def save_password(self, item: PasswordItemBase):
        password_id = str(uuid.uuid4())
        item.id = password_id

        cur = self.conn.cursor()
        cur.execute(f"""
            INSERT INTO password VALUES (
            '{password_id}',
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

        return PasswordItemBase.from_db(res)

    def get_passwords(self) -> list[PasswordItemBase]:
        cur = self.conn.cursor()
        res = cur.execute("SELECT * FROM password").fetchall()

        return [PasswordItemBase.from_db(item) for item in res]
