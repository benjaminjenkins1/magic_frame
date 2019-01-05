import uuid

frameID = uuid.uuid4()

with open('hello', 'w') as f:
  f.write('jmphoto@' +  str(frameID) )
