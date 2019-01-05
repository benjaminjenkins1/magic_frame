from flask import Flask, render_template, request, session, redirect
import re
from user import User

app = Flask(__name__)

with open('secret.txt', 'r') as secret_file:
    app.secret_key = secret_file.read().replace('\n', '')

@app.route('/', methods=['GET'])
def home():
  return render_template('home.html')

@app.route('/photos', methods=['GET'])
def photos():
  if session.get('logged_in') is None:
    return render_template('signin.html', page='phone')
  return render_template('photos.html', active_tab='photos')

@app.route('/people', methods=['GET'])
def people():
  if session.get('logged_in') is None:
    return render_template('signin.html', page='phone')
  return render_template('people.html', active_tab='people')

@app.route('/settings', methods=['GET'])
def settings():
  if session.get('logged_in') is None:
    return render_template('signin.html', page='phone')
  return render_template('settings.html', active_tab='settings')

@app.route('/discover', methods=['GET'])
def discover():
  if session.get('logged_in') is None:
    return render_template('signin.html', page='phone')
  return render_template('discover.html', active_tab='settings')

@app.route('/notlisted', methods=['GET'])
def not_listed():
  return render_template('notlisted.html', active_tab='settings')

@app.route('/addframe', methods=['GET'])
def add_frame():
  if session.get('logged_in') is None:
    return render_template('signin.html', page='phone')
  return render_template('addframe.html', active_tab='settings')

@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
  if request.method == 'GET':
    if session.get('logged_in') is not None:
      return redirect('/photos')
    else:
      return render_template('signin.html', page='phone')
  elif request.method == 'POST':
    #TODO: send code cooldown
    phone_number = re.sub('[^0-9]', '', request.form['phone-number'])
    if len(phone_number) != 10:
      return render_template('signin.html', page='phone', error=True)
    session['phone'] = request.form['phone-number']
    # make a new otp for the phone number and send to code input
    print(phone_number)
    user = User(phone_number)
    user.add_otp()
    return render_template('signin.html', page='code', phone_number=session['phone'])

@app.route('/otp', methods=['POST'])
def one_time_password():
  # validate before making user/querying
  otp = re.sub('[^0-9]', '', request.form['otp'])
  if len(otp) != 7:
    return render_template('signin.html', page='code', error=True, phone_number=session['phone'])
  # make a User with the phone number and otp
  phone_number = re.sub('[^0-9]', '', session['phone'])
  print(phone_number)
  user = User(phone_number)
  if user.authenticate(otp):
    session['logged_in'] = True
    session.permanent = True
    # if the user has no name, send them to name creation. Otherwise, to the photos page
    if user.name == False:
      return render_template('username.html')
    else:
      session['name'] = user.name
      return render_template('photos.html', active_tab='photos')
  # all else failed, send the error message
  return render_template('signin.html', page='code', error=True, phone_number=session['phone'])

@app.route('/username', methods=['POST'])
def set_username():
  if session.get('logged_in') is None:
      return render_template('signin.html', page='phone')
  phone_number = re.sub('[^0-9]', '', session['phone'])
  user = User(phone_number)
  username = request.form['username']
  user.set_name(username)
  # tour is next
  return render_template('gettingstarted.html')
  
@app.route('/signout', methods=['GET'])
def sign_out():
  session.clear()
  return redirect('/')