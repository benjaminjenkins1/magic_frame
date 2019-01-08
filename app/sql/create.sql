CREATE TABLE users (
  phone INTEGER NOT NULL,
  username TEXT,
  otp_hash TEXT,
  otp_created DATETIME,
  PRIMARY KEY (phone)
);

CREATE TABLE photos (
  filename TEXT NOT NULL,
  thumb_filename TEXT NOT NULL,
  owner INTEGER NOT NULL,
  date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (filename)
  FOREIGN KEY (owner) REFERENCES users(phone)
);

CREATE TABLE friends (
  self_phone INTEGER NOT NULL,
  friend_phone INTEGER NOT NULL,
  PRIMARY KEY(self_phone, friend_phone),
  FOREIGN KEY (self_phone) REFERENCES users(phone),
  FOREIGN KEY (friend_phone) REFERENCES users(phone)
);

CREATE TABLE frames (
  uuid TEXT NOT NULL,
  owner INTEGER NOT NULL,
  PRIMARY KEY (uuid, owner),
  FOREIGN KEY (owner) REFERENCES users(phone)
);

CREATE TRIGGER new_otp
AFTER UPDATE OF otp ON users
FOR EACH ROW
BEGIN
  UPDATE users SET otp_created=CURRENT_TIMESTAMP WHERE phone=old.phone;
END;