from flask import Flask, render_template, request, session, redirect, flash, send_from_directory, jsonify
import re, requests
from user import User
from frame import Frame

app = Flask(__name__)

with open('secret.txt', 'r') as secret_file:
    app.secret_key = secret_file.read().replace('\n', '')
with open('recaptcha_key.txt', 'r') as recaptcha_key_file:
    RECAPTCHA_KEY = recaptcha_key_file.read().replace('\n', '')

OTP_COOLDOWN = 120
# seconds

@app.route('/', methods=['GET'])
def home():
  return render_template('home.html')

@app.route('/photos', methods=['GET'])
def photos():
  if session.get('logged_in') is None:
    return redirect('/signin')
  phone_number = re.sub('[^0-9]', '', session['phone'])
  user = User(phone_number)
  photos = user.get_photos()
  return render_template('photos.html', photos=photos, active_tab='photos')

@app.route('/people', methods=['GET'])
def people():
  if session.get('logged_in') is None:
    return redirect('/signin')
  phone_number = re.sub('[^0-9]', '', session['phone'])
  user = User(phone_number)
  return render_template('people.html', active_tab='people', 
                                        friend_requests=user.get_requests(),
                                        pending_requests=user.get_pending(),
                                        friends=user.get_friends())

@app.route('/settings', methods=['GET'])
def settings():
  if session.get('logged_in') is None:
    return redirect('/signin')
  phone_number = re.sub('[^0-9]', '', session['phone'])
  user = User(phone_number)
  frames = user.get_frames()
  return render_template('settings.html', active_tab='settings', frames=frames)

@app.route('/discover', methods=['GET'])
def discover():
  if session.get('logged_in') is None:
    return redirect('/signin')
  return render_template('discover.html', active_tab='settings')

@app.route('/notlisted', methods=['GET'])
def not_listed():
  return render_template('notlisted.html', active_tab='settings')

@app.route('/addframe', methods=['GET'])
def add_frame():
  if session.get('logged_in') is None:
    return redirect('/signin')
  phone_number = re.sub('[^0-9]', '', session['phone'])
  user = User(phone_number)
  frameID = request.args.get('id')
  error = user.add_frame(frameID)
  return render_template('addframe.html', active_tab='settings', frameID=frameID)

@app.route('/gettingstarted', methods=['GET'])
def getting_started():
  return render_template('gettingstarted.html')

@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
  if request.method == 'GET':
    if session.get('logged_in') is not None:
      return redirect('/photos')
    else:
      return render_template('signin.html', page='phone')
  elif request.method == 'POST':
    phone_number = re.sub('[^0-9]', '', request.form['phone-number'])
    if len(phone_number) != 10:
      flash('Oops, that didn\'t look like a phone number.<br>Please try again.')
      return render_template('signin.html', page='phone')
    session['phone'] = request.form['phone-number']
    # make a new otp for the phone number and send to code input
    user = User(phone_number)
    otp_age = user.otp_age()
    #print(otp_age)
    if otp_age is None or otp_age > OTP_COOLDOWN:
      user.add_otp()
    return render_template('signin.html', page='code', phone_number=session['phone'])

@app.route('/resend_otp', methods=['GET', 'POST'])
def resend_otp():
  if request.method == 'GET':
    return render_template('resend.html', phone=session['phone'])
  if request.method == 'POST':
    phone_number = re.sub('[^0-9]', '', request.form['phone-number'])
    if len(phone_number) != 10:
      flash('Oops, that didn\'t look like a phone number.<br>Please try again.')
      return render_template('resend.html', phone=request.form['phone-number'])
    captcha_data = {
      'secret': RECAPTCHA_KEY,
      'response': request.form['g-recaptcha-response']
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=captcha_data)
    if r.json()['success']:
      session['phone'] = request.form['phone-number']
      user = User(phone_number)
      user.add_otp()
      flash('Another code has been sent to ' + request.form['phone-number'] + '.')
      return render_template('signin.html', page='code', phone_number=session['phone'])
    else:
      flash('Please complete the captcha.')
      return render_template('resend.html', phone=request.form['phone-number'])

@app.route('/auth', methods=['POST'])
def one_time_password():
  # validate before making user/querying
  otp = re.sub('[^0-9]', '', request.form['otp'])
  if len(otp) != 7:
    flash('Invalid or expired code.')
    return render_template('signin.html', page='code', phone_number=session['phone'])
  # make a User with the phone number and otp
  phone_number = re.sub('[^0-9]', '', session['phone'])
  user = User(phone_number)
  if user.authenticate(otp):
    session['logged_in'] = True
    session.permanent = True
    # if the user has no name, send them to name creation. Otherwise, to the photos page
    if user.name is None:
      return render_template('username.html', error=False)
    else:
      session['name'] = user.name
      return redirect('/photos')
  # all else failed, send the error message
  flash('Invalid or expired code.')
  return render_template('signin.html', page='code', error=True, phone_number=session['phone'])

@app.route('/username', methods=['POST'])
def set_username():
  if session.get('logged_in') is None:
      return redirect('/signin')
  phone_number = re.sub('[^0-9]', '', session['phone'])
  user = User(phone_number)
  username = request.form['username']
  # usernames must be between 3 and 20 characters, but not unique
  if len(username) > 20 or len(username) < 3:
    return render_template('username.html', error=True)
  user.set_name(username)
  # tour is next
  return redirect('/gettingstarted')
  
@app.route('/signout', methods=['GET'])
def sign_out():
  session.clear()
  return redirect('/')

@app.route('/addfriend', methods=['POST'])
def add_friend():
  if session.get('logged_in') is None:
    return redirect('/signin')
  phone_number = re.sub('[^0-9]', '', session['phone'])
  friend_phone = re.sub('[^0-9]', '', request.form['phone-number'])
  if len(friend_phone) != 10:
    return redirect('/people')
  user = User(phone_number)
  user.add_friend(friend_phone)
  return redirect('/people')

@app.route('/removefriend', methods=['POST'])
def remove_friend():
  if session.get('logged_in') is None:
    return redirect('/signin')
  phone_number = re.sub('[^0-9]', '', session['phone'])
  friend_phone = re.sub('[^0-9]', '', request.form['phone-number'])
  user = User(phone_number)
  user.remove_friend(friend_phone)
  return redirect('/people')
  
@app.route('/declinefriend', methods=['POST'])
def decline_friend():
  if session.get('logged_in') is None:
    return redirect('/signin')
  phone_number = re.sub('[^0-9]', '', session['phone'])
  friend_phone = re.sub('[^0-9]', '', request.form['phone-number'])
  user = User(phone_number)
  user.decline_friend(friend_phone)
  return redirect('/people')

@app.route('/addphotos', methods=['POST'])
def add_photos():
  if session.get('logged_in') is None:
    return redirect('/signin')
  phone_number = re.sub('[^0-9]', '', session['phone'])
  user = User(phone_number)
  error = False
  uploaded_files = request.files.getlist("files")
  for file in uploaded_files:
    if not user.add_photo(file):
      flash('There was a problem uploading ' + file.filename)
  return redirect('/photos')

@app.route('/deletephotos', methods=['POST'])
def delete_photos():
  if session.get('logged_in') is None:
    return redirect('/signin')
  filenames = request.form.getlist('name[]')
  phone_number = re.sub('[^0-9]', '', session['phone'])
  user = User(phone_number)
  for filename in filenames:
    #print(filename)
    if user.owns_image(filename):
      user.delete_photo(filename)
  return redirect('/photos')

@app.route('/getimg', methods=['GET'])
def get_image():
  if session.get('logged_in') is None:
    return redirect('/signin')
  phone_number = re.sub('[^0-9]', '', session['phone'])
  user = User(phone_number)
  filename = request.args.get('name')
  if user.owns_image(filename):
    return send_from_directory('uploads', filename)
  else:
    return ''

@app.route('/frame', methods=['GET'])
def photo_list():
  frameID = request.args.get('id')
  return render_template('frame.html', frameID=frameID)

@app.route('/framephotos', methods=['GET'])
def frame_photos():
  frameID = request.args.get('id')
  frame = Frame(frameID)
  photos = frame.get_photos()
  photos_list = [i[0] for i in photos]
  return jsonify(photos_list)

@app.route('/framegetphoto', methods=['GET'])
def frame_get_photo():
  frameID = request.args.get('id')
  filename = request.args.get('name')
  frame = Frame(frameID)
  if frame.owns_image(filename):
    return send_from_directory('uploads', filename)
  else:
    return ''

@app.route('/removeframe', methods=['POST'])
def remove_frame():
  if session.get('logged_in') is None:
    return redirect('/signin')
  phone_number = re.sub('[^0-9]', '', session['phone'])
  user = User(phone_number)
  user.remove_frame(request.form['frameID'])
  return redirect('/settings')