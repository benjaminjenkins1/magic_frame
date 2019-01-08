import sqlite3

class Frame:

  def __init__(self, frameID):
    self.conn = sqlite3.connect('database.db')
    self.c = self.conn.cursor()
    self.frameID = frameID

  def __del__(self):
    self.conn.close()

  def get_photos(self):
    # get photos owned by the frame's owner or the frame owner's friends
    query = ("SELECT photos.filename FROM frames, photos "
             "WHERE (photos.owner=frames.owner "
             "AND frames.uuid=?) "
             "OR photos.owner IN ( "
             "SELECT friend_phone FROM frames, friends "
             "WHERE frames.uuid=? "
             "AND frames.owner=friends.self_phone)"
    )
    self.c.execute(query, (self.frameID, self.frameID))
    return self.c.fetchall()

  def owns_image(self, filename):
    # true if filename is owned by the frame's owner or the frame owner's friends
    query = ("SELECT 1 FROM frames, photos "
             "WHERE (photos.filename=? "
             "AND photos.owner=frames.owner "
             "AND frames.uuid=?) "
             "OR (photos.filename=? "
             "AND photos.owner IN ( "
             "SELECT friend_phone FROM frames, friends "
             "WHERE frames.uuid=? "
             "AND frames.owner=friends.self_phone))"
    )
    self.c.execute(query, (filename, self.frameID, filename, self.frameID))
    if self.c.fetchone() is not None:
      return True
    return False