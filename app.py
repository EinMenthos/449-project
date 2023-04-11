from flask import Flask, render_template, request, redirect, url_for, session, abort
import pymysql
from flask_sqlalchemy import SQLAlchemy
import uuid #For public id
from flask_cors import CORS
import re
"""
<<<<<<< HEAD
#needed for JWT
import jwt
from functools import wraps
#needed for uploading files?
=======

#needed for uploading files
>>>>>>> c024af125d0bf323250065367bfc34b391958ffb
"""
import os
from werkzeug.utils import secure_filename
from hashlib import pbkdf2_hmac

def generate_salt():
	salt = os.urandom(16)
	return salt.hex()

def generate_hash(plain_password, password_salt):
	password_hash = pbkdf2_hmac(
		"sha256",
		b"%b" % bytes(plain_password, "utf-8"),
		b"%b" % bytes(password_salt, "utf-8"),
		10000,
	)
	return password_hash.hex()

#needed for JWT
import jwt
from flask import jsonify, make_response
#to make sure the token expire after a while
import datetime
from functools import wraps


app = Flask(__name__)
# CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config["DEBUG"] = True

app.secret_key = 'happykey'

# app.config['MYSQL_HOST'] = '127.0.0.1'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = '1234'
# app.config['MYSQL_DB'] = 'test'
# To connect MySQL database

#password = "1234567890"	#professor DB pw
#password = My20SQL21		#Daniel pw
#password = "Sql1121990",

def generate_jwt_token(content):
	encoded_content = jwt.encode(content, app.secret_key, algorithm="HS256")
	token = str(encoded_content).split(" ")[0]
	return token



conn = pymysql.connect(
        host='localhost',
        user='root', 
        password = "Oddworld13759",
        db='449_db',
		cursorclass=pymysql.cursors.DictCursor
        )
cur = conn.cursor()

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cur.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
		conn.commit()
		account = cur.fetchone()
		if account:
            
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			session['password_hash'] = account['password_hash']
			session['password_salt'] = account['password_salt']
			session['admin'] = account['admin']
			session['jwt_token'] = None
			password_hash = generate_hash(password, session['password_salt'])				

			#if account is an admin and the hashes match a token will be generated and saved to the session until a new person logs in
			if password_hash == account['password_hash']:
				user_id = session['id']
				user_admin = session['admin']
				user_name = session['username']
				jwt_token = generate_jwt_token({"id": user_id,"user_name": user_name, "admin": user_admin})
				session['jwt_token'] = jwt_token
				print(jwt_token)
			
			msg = 'Logged in successfully !'	
			return render_template('index.html', msg = msg)

		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'city' in request.form and 'country' in request.form and 'postalcode' in request.form and 'organisation' in request.form:
		print('reached')
		username = request.form['username']
		password = request.form['password']
		password_salt = generate_salt()
		password_hash = generate_hash(password, password_salt)
		email = request.form['email']
		organisation = request.form['organisation']
		address = request.form['address']
		city = request.form['city']
		state = request.form['state']
		country = request.form['country']
		postalcode = request.form['postalcode']
		cur.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cur.fetchone()
		print(account)
		conn.commit()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'name must contain only characters and numbers !'
		else:
			cur.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, 0)', (username, password, email, organisation, address, city, state, country, postalcode, password_salt, password_hash ))
			conn.commit()

			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)


@app.route("/index")
def index():
	if 'loggedin' in session:
		return render_template("index.html")
	return redirect(url_for('login'))


@app.route("/display")
def display():
	if 'loggedin' in session:
		cur.execute('SELECT * FROM accounts WHERE id = % s', (session['id'], ))
		account = cur.fetchone()
		return render_template("display.html", account = account)
	return redirect(url_for('login'))

#only accessable by 'admins' who are marked as such in the database
#anyone who tries to access this who isnt an admin with a token will be booted into the login page
@app.route("/protected")
def protected():
	if 'loggedin' in session:
		jwt_token = session.get('jwt_token')
		if jwt_token == None:
			return redirect(url_for('login'))
		try:
			payload = jwt.decode(jwt_token, app.config['SECRET_KEY'], algorithms=['HS256'])
		except (jwt.InvalidTokenError, KeyError):
			return render_template('error.html', error_message = no_permission(403))
		if payload['admin'] == 1:
			return render_template('test.html')
		else:
			return render_template('error.html', error_message = no_permission(403))
		
		
		
		


@app.route("/update", methods =['GET', 'POST'])
def update():
	msg = ''
	if 'loggedin' in session:
		if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'city' in request.form and 'country' in request.form and 'postalcode' in request.form and 'organisation' in request.form:
			username = request.form['username']
			password = request.form['password']
			email = request.form['email']
			organisation = request.form['organisation']
			address = request.form['address']
			city = request.form['city']
			state = request.form['state']
			country = request.form['country']
			postalcode = request.form['postalcode']
			cur.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
			account = cur.fetchone()
			if account:
				msg = 'Account already exists !'
			elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
				msg = 'Invalid email address !'
			elif not re.match(r'[A-Za-z0-9]+', username):
				msg = 'name must contain only characters and numbers !'
			else:
				cur.execute('UPDATE accounts SET username =% s, password =% s, email =% s, organisation =% s, address =% s, city =% s, state =% s, country =% s, postalcode =% s WHERE id =% s', (username, password, email, organisation, address, city, state, country, postalcode, (session['id'], ), ))
				conn.commit()
				msg = 'You have successfully updated !'
		elif request.method == 'POST':
			msg = 'Please fill out the form !'
		return render_template("update.html", msg = msg)
	return redirect(url_for('login'))

@app.route('/user')
def user():
	if 'username' in session:
		name = session['username']
		return '<h1>welcome '+ name +'</h1>'
	else:
		return render_template('login.html', msg = "need to log in first!") 

@app.route('/admin')
def admin():
	if 'username' in session:
		name = session['username']
		if name == "admin":
			return render_template('admin.html') 
			#return '<h1>This is a special page for '+ name +'</h1>'
		else:
			#return '<h1>Current user do not have enough permission to access this page.</h1>'
			abort(401)
	else:
		return render_template('login.html', msg = "need to log in first!") 

#task2: error handling
@app.errorhandler(400)
def bad_request(e):
	return '<h1>400 - Bad Request</h1>'

@app.errorhandler(401)
def no_permission(e):
	return '<h1>401 - Unauthorized</h1>'

@app.errorhandler(403)
def no_permission(e):
	return '<h1>403 - Forbidden</h1>'

@app.errorhandler(404)
def page_not_found(e):
	return '<h1>404 - Page Not Found</h1>'

@app.errorhandler(500)
def unexpected_error(e):
	return '<h1>500 - Server encountered an unexpected error</h1>'

@app.errorhandler(501)
def not_implemented(e):
	return '<h1>501 - Server does not recognize the request method</h1>'

@app.errorhandler(502)
def bad_gateway(e):
	return '<h1>502 - Bad Gateway</h1>'

@app.errorhandler(505)
def http_not_supported(e):
	return '<h1>505 - Server does not support the HTTP version used in the request</h1>'

#task4 - uploading files
#original source https://www.youtube.com/watch?v=6WruncSoCdI
#app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024			#this name is a global which overwrite my error handling.
app.config['MAX_IMAGE_FILESIZE'] = 1024 * 1024
#app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
#app.config['UPLOAD_PATH'] = 'uploads'
app.config['IMAGE_UPLOADS'] = '/Users/danielwu/Projects/449/midterm/449-project/upload'
app.config['ALLOWED_IMAGE_EXTENSIONS'] = ['.jpg', '.png', '.gif', '.jpeg']

@app.route('/upload-image', methods =['GET', 'POST'])
def upload_image():
	if request.method == "POST":
		if request.files:
			print (request.cookies.get("filesize"))
			if not allowed_image_filesize(request.cookies.get("filesize")):
				print("File exceeded maximum size")
				abort(400)
			image = request.files["image"]
			#print(image)    #terminal shows <FileStorage: 'image.jpg' ('image/svg+xml')>
			filename = secure_filename(image.filename)
			#print(image.filename)		#terminal shows the filename
			if filename != "":
				file_ext = os.path.splitext(filename)[1]
				if file_ext not in app.config['ALLOWED_IMAGE_EXTENSIONS']:
					abort(400)
				image.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))
				print("image saved")    #just a msg on terminal to keep track
				return redirect(request.url)
			else:
				print("image must have a filename")
				return redirect(request.url)
	return render_template('upload_image.html')
#23:09
def allowed_image_filesize(filesize):
	if int(filesize) <= app.config['MAX_IMAGE_FILESIZE']:
		print("true")
		return True
	else:
		print("false")
		return False

# task 5 - public route
@app.route("/public-info", methods =['GET'])
def public_info():
	cur.execute('SELECT username, country FROM accounts')
	accounts = cur.fetchall()
	return render_template("public-info.html", accounts = accounts)
	
#task3
#using this website as a reference: https://www.youtube.com/watch?v=J5bIPtEbS0Q
#secret key generated by running pyhton in terminal
#then running the following commands at pyhton terminal:
#imports secrets
#secrets.token_hex(16)
app.config['SECRET_KEY']='d192b2b5ea9181024fc95913e27a20c5'
#app.config['SECRET_KEY']='thisisthesecretkey'

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = request.args.get('token') #http://localhost:5000/route?token=token_generated_at_loginpwt
		#print(token)
		if not token:
			return jsonify({'message' : 'Token is missing'}), 403

		try:
			#print('trying to decode token:')
			#print(token)
			data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
			#data = token
		except:
			return jsonify({'message' : 'Token is invalid'}), 403

		return f(*args, **kwargs)
	return decorated

@app.route('/unprotected')
def unprotected():
	return jsonify({'message' : 'Anyone can view this!', 'not_secret_ingredient' : 'ketchup'})

"""
@app.route('/protected')
@token_required
def protected():
	return jsonify({'message':'This is only available for people with valid tokens.', 'secret_ingredient' : 'MSG'})
"""

@app.route('/loginpwt')
def loginpwt():
	auth = request.authorization
	
	#accept any username, but password must be 123
	if auth and auth.password == '1234':
		#token will expire after 30 seconds for test purpose
		#this is also the payload information
		token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = 1)}, app.config['SECRET_KEY'], algorithm='HS256')
		#print('encoded token:')
		#print(token)
		return jsonify ({'token' : token})
		#return jsonify ({'token' : token.decode('UTF-8')})

	return make_response('Cannot verify!', 401, {'WWW-authenticate' : 'Basic realm="Login Required"'})


if __name__ == "__main__":
	app.run(host ="localhost", port = int("5000"))
