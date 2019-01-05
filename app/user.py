import sqlite3, secrets, string
from passlib.hash import pbkdf2_sha256
from PIL import Image

class User:

  def __init__(self, phone):
    self.conn = sqlite3.connect('database.db')
    self.c = self.conn.cursor()
    # create uer if not exists
    self.c.execute('INSERT OR IGNORE INTO users (phone) VALUES (?)', (phone,))
    self.conn.commit()
    self.phone = phone
    self.name = self.get_name()

  def __del__(self):
    self.conn.close()

  def get_name(self):
    return False

  def authenticate(self, otp):
    self.c.execute('SELECT otp_hash FROM users WHERE phone=?', (self.phone,))
    otp_hash = self.c.fetchone()[0]
    return pbkdf2_sha256.verify(otp, otp_hash)

  def set_name(self, username):
    self.c.execute('UPDATE users SET username=? WHERE phone=?', (username, self.phone))
    self.conn.commit()

  def add_otp(self):
    otp = ''.join(secrets.choice(string.digits) for i in range(7))
    print(otp)
    otp_hash = pbkdf2_sha256.hash(otp)
    self.c.execute('UPDATE users SET otp_hash=? WHERE phone=?', (otp_hash, self.phone))
    self.conn.commit()