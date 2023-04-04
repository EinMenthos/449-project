from flask import Flask, render_template, request, redirect, url_for, session, abort
import pymysql
from flask_cors import CORS
import re
#needed for JWT
import jwt
#needed for uploading files
import os
from werkzeug.utils import secure_filename

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

conn = pymysql.connect(
        host='localhost',
        user='root', 
        password = "My20SQL21",
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
			cur.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s, % s, % s, % s, % s, % s)', (username, password, email, organisation, address, city, state, country, postalcode, ))
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
		


if __name__ == "__main__":
	app.run(host ="localhost", port = int("5000"))
