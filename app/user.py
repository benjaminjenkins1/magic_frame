import sqlite3, secrets, string
from passlib.hash import pbkdf2_sha256
from PIL import Image
from twilio.rest import Client
import os

with open('twilio_key.txt', 'r') as keyfile:
  twilio_key = keyfile.read().replace('\n', '')
with open('twilio_id.txt', 'r') as idfile:
  twilio_id = idfile.read().replace('\n', '')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

IMAGE_SIZE = 1920, 1920
THUMBNAIL_SIZE = 120, 120
# pixels

OTP_LIFETIME = 1800
# seconds

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
    self.c.execute('SELECT username FROM users WHERE phone=?', (self.phone,))
    return self.c.fetchone()[0]

  def authenticate(self, otp):
    if self.otp_age() > OTP_LIFETIME:
      return False
    self.c.execute('SELECT otp_hash FROM users WHERE phone=?', (self.phone,))
    otp_hash = self.c.fetchone()[0]
    return pbkdf2_sha256.verify(otp, otp_hash)

  def set_name(self, username):
    self.c.execute('UPDATE users SET username=? WHERE phone=?', (username, self.phone))
    self.conn.commit()

  def add_otp(self):
    otp = ''.join(secrets.choice(string.digits) for i in range(7))
    print('OTP for ' + self.phone + ': ' + otp)
    client = Client(twilio_id, twilio_key)
    message_body = "Your Magic Frame sign-in code is " + otp
    message = client.messages.create(
        to=self.phone, 
        from_="+19142299502",
        body=message_body)
    #print(message.sid)
    otp_hash = pbkdf2_sha256.hash(otp)
    self.c.execute('UPDATE users SET otp_hash=? WHERE phone=?', (otp_hash, self.phone))
    self.conn.commit()

  # Get otp age in seconds
  def otp_age(self):
    query = ("SELECT (julianday(CURRENT_TIMESTAMP)-julianday(otp_created))*(86400)"
             "FROM users "
             "WHERE phone=?"
    )
    self.c.execute(query, (self.phone,))
    result = self.c.fetchone()
    if result is None:
      return None
    return result[0]

  def add_friend(self, friend_phone):
    self.c.execute('INSERT OR IGNORE INTO friends VALUES (?, ?)', (self.phone, friend_phone))
    self.conn.commit()

  def decline_friend(self, friend_phone):
    self.c.execute('DELETE FROM friends WHERE friend_phone=? AND self_phone=?', (self.phone, friend_phone))
    self.conn.commit()

  def remove_friend(self, friend_phone):
    self.c.execute('DELETE FROM friends WHERE self_phone=? AND friend_phone=?', (self.phone, friend_phone))
    self.c.execute('DELETE FROM friends WHERE self_phone=? AND friend_phone=?', (friend_phone, self.phone))
    self.conn.commit()

  def get_requests(self):
    query = ("SELECT users.username, a.self_phone FROM friends AS a, users "
             "WHERE a.friend_phone=? "
             "AND users.phone=a.self_phone "
             "AND ? NOT IN ("
             "SELECT self_phone FROM friends "
             "WHERE self_phone=? "
             "AND friend_phone=a.self_phone)"
    )
    self.c.execute(query, (self.phone, self.phone, self.phone))
    requests = self.c.fetchall()
    requests_formatted = list(map(format_phone2, requests))
    return requests_formatted

  def get_pending(self):
    query = ("SELECT a.friend_phone FROM friends AS a "
             "WHERE a.self_phone=? "
             "AND NOT EXISTS ("
             "SELECT 1 FROM friends AS b "
             "WHERE b.friend_phone=? AND "
             "b.self_phone=a.friend_phone)"
    )
    self.c.execute(query, (self.phone, self.phone))
    pending = self.c.fetchall()
    pending_formatted = list(map(format_phone, pending))
    return pending_formatted

  def get_friends(self):
    query = ("SELECT users.username, a.friend_phone FROM friends AS a, users "
             "WHERE a.self_phone=? "
             "AND users.phone=a.friend_phone "
             "AND a.friend_phone IN ("
             "SELECT self_phone FROM friends "
             "WHERE friend_phone=?)"
    )
    self.c.execute(query, (self.phone, self.phone))
    friends = self.c.fetchall()
    friends_formatted = list(map(format_phone2, friends))
    return friends_formatted

  def add_frame(self, frameID):
    query = "INSERT OR IGNORE INTO frames (uuid, owner) VALUES (?, ?)"
    self.c.execute(query, (frameID, self.phone))
    self.conn.commit()

  def remove_frame(self, frameID):
    query = "DELETE FROM frames WHERE uuid=? AND owner=?"
    self.c.execute(query, (frameID, self.phone))
    self.conn.commit()

  def get_frames(self):
    query = "SELECT * FROM frames WHERE owner=?"
    self.c.execute(query, (self.phone,))
    return self.c.fetchall()

  def add_photo(self, file):
    if allowed_file(file.filename):
      image_filename = ''.join(secrets.choice(string.digits + string.ascii_letters) for i in range(20)) + '.png'
      thumb_filename = ''.join(secrets.choice(string.digits + string.ascii_letters) for i in range(20)) + '.png'
      # resize and save 1920px image
      image = Image.open(file)
      image.thumbnail(IMAGE_SIZE, Image.ANTIALIAS)
      image.convert('RGB').save(os.path.join(UPLOAD_FOLDER, image_filename), "PNG", optimize=True)
      # resize and save 120px image
      thumb = Image.open(file)
      thumb.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
      thumb.convert('RGB').save(os.path.join(UPLOAD_FOLDER, thumb_filename), "PNG", optimize=True)
      # insert db record
      query = "INSERT INTO photos (filename, thumb_filename, owner) VALUES (?, ?,?)"
      self.c.execute(query, (image_filename, thumb_filename, self.phone))
      self.conn.commit()
      return True
    return False

  def delete_photo(self, filename):
    # delete from db
    query = "DELETE FROM photos WHERE (filename=? AND owner=?) or (thumb_filename=? AND owner=?)"
    self.c.execute(query, (filename, self.phone, filename, self.phone))
    self.conn.commit()
    # delete from fs
    os.remove(os.path.join(UPLOAD_FOLDER, filename))

  def get_photos(self):
    query = "SELECT filename, thumb_filename FROM photos WHERE owner=?"
    self.c.execute(query, (self.phone,))
    photos = self.c.fetchall()
    return photos

  def owns_image(self, filename):
    query = "SELECT 1 FROM photos WHERE (filename=? AND owner=?) OR (thumb_filename=? AND owner=?)"
    self.c.execute(query, (filename, self.phone, filename, self.phone))
    if self.c.fetchone() is not None:
      return True
    return False



# some utilities that should probably have their own file

def format_phone(phone):
  phone_str = str(phone[0])
  formatted = '(' + phone_str[0:3] + ') ' + phone_str[3:6] + ' - ' + phone_str[6:]
  return formatted

def format_phone2(user):
  phone_str = str(user[1])
  formatted = '(' + phone_str[0:3] + ') ' + phone_str[3:6] + ' - ' + phone_str[6:]
  return (user[0], formatted)

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
