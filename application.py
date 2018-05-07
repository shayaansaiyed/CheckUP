from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql

application = Flask(__name__)

application.config['UPLOAD_FOLDER'] = "./static/Documents/"

conn = pymysql.connect(host='dbinstance.clvo2ema2nfj.us-east-2.rds.amazonaws.com',
						port = 3306,
						user='checkupdb',
						password='Strauss4life',
						db='checkupdb',
						charset='utf8mb4',
						cursorclass=pymysql.cursors.DictCursor
						)

# @application.route('/')
# def start():
# 	cursor = conn.cursor()
# 	query = "SELECT * FROM login_credentials"
# 	cursor.execute(query)
# 	data = cursor.fetchall()
# 	print (data)
# 	cursor.close()
# 	return render_template("index.html", data = data)

@application.route('/')
def start():
	return render_template("template.html")

@application.route('/home')
def home():
	return render_template("index.html")

@application.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	# grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	user_id = request.form['user_id']

	# cursor used to send queries
	cursor = conn.cursor()
	# executes query
	query = "INSERT INTO login_credentials VALUES (%s,%s,%s)"
	cursor.execute(query, (username, password, user_id))
	conn.commit()

	cursor.close()
	return redirect("/")

@application.route('/handle_file_upload', methods = ['GET', 'POST'])
def handle_file_upload():
	userID = 1
	filedesc = request.form["FileName"]

	document = request.files["inputFile"]
	filename = document.filename
	print (application.config['UPLOAD_FOLDER'] + filename)

	document.save(application.config['UPLOAD_FOLDER'] + filename)

	cursor = conn.cursor()
	query = "INSERT INTO documents (userID, docTitle, docName) VALUES (%s, %s, %s)"
	cursor.execute(query, (str(userID), filedesc, filename))
	conn.commit()

	cursor.close()
	return redirect("/upload")


@application.route('/handle_data_upload', methods=['GET', 'POST'])
def handle_data_upload():
	# print("upload()")
	userID = 1

	#TODO: implement correct user ID

	heightFT = request.form["height-ft"]
	heightIN = request.form["height-in"]
	weight = request.form["weight"]
	bloodPressure = request.form["bloodPressure"]
	heartRate = request.form["heartRate"]
	bloodSugar = request.form["bloodSugar"]

	#TODO: fix height

	#temp values for until the front end is fixed
	# weight = "0.00"
	# heightFT = "0.00"
	# heightIN = "0.00"
	# bloodSugar= "0.00"
	# bloodPressure = "0.00"
	# heartRate = "0.00"

	#temp values for until the front end is fixe
	cursor = conn.cursor()

	query = "INSERT INTO data (userID, data, TypeID) VALUES (%s,%s,%s)"
	cursor.execute(query, (userID, weight, 0))
	conn.commit()

	query = "INSERT INTO data (userID, data, TypeID) VALUES (%s,%s,%s)"
	cursor.execute(query, (userID, heightFT, 1))
	conn.commit()

	query = "INSERT INTO data (userID, data, TypeID) VALUES (%s,%s,%s)"
	cursor.execute(query, (userID, heartRate, 2))
	conn.commit()

	query = "INSERT INTO data (userID, data, TypeID) VALUES (%s,%s,%s)"
	cursor.execute(query, (userID, bloodPressure, 3))
	conn.commit()

	query = "INSERT INTO data (userID, data, TypeID) VALUES (%s,%s,%s)"
	cursor.execute(query, (userID, bloodSugar, 4))
	conn.commit()

	cursor.close()
	return render_template('upload.html')

@application.route('/account', methods=['GET', 'POST'])
def account():
	cursor = conn.cursor()
	query = "SELECT * FROM patient WHERE userID = 1"
	cursor.execute(query)
	data = cursor.fetchall()
	firstName = data[0]['firstName']
	lastName = data[0]['lastName']
	email = data[0]['email']
	dob = data[0]['dob']
	sex = data[0]['sex']
	gender = data[0]['gender']
	hcpID = data[0]['hcpID']
	return render_template('accounts.html', firstName = firstName, lastName = lastName, email = email, dob = dob, sex = sex, gender = gender, hcpID = hcpID)

@application.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method == 'GET':
		return render_template('upload.html')

@application.route('/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

@application.route('/processSignIn', methods=['GET', 'POST'])
def processSignIn():
	email = request.form["inputEmail"]
	password = request.form["inputPassword"]

	cursor = conn.cursor()
	query = "SELECT * FROM accounts WHERE userName = %s and userPass = %s"
	cursor.execute(query, (email, password))
	data = cursor.fetchone()
	cursor.close()

	error = None
	if (data):
		cursor = conn.cursor()
		query = "SELECT userID FROM accounts WHERE userName=%s"
		cursor.execute(query, (email))
		data = cursor.fetchone()
		session["username"] = data['userID']
		return redirect(url_for("graphs"))
	else:
		error = "The username and password are incorrect. Please try again."
		return render_template('login.html', error = error)

@application.route('/graphs', methods=['GET', 'POST'])
def graphs():
	if request.method == 'GET':
		cursor = conn.cursor()
		query = "SELECT data FROM data WHERE userID = 1 AND typeID = 3"
		cursor.execute(query)
		data = cursor.fetchall()
		yValues = []
		for j in data:
			print(j['data'])
			yValues.append(j['data'])
		print()
		cursor = conn.cursor()
		query = "SELECT * FROM data WHERE userID = 1 AND typeID = 3"
		cursor.execute(query)
		data = cursor.fetchall()
		xValues = []
		for j in data:
			xValues.append(j['‘date’'])
			print(j['‘date’'])


		legend = 'Data'
		return render_template('graphs.html', values=yValues, labels=xValues, legend = legend)

@application.route('/signup')
def signup():
	print ("signup()")
	return render_template('signup.html')

@application.route('/handle_signup', methods=['GET', 'POST'])
def handle_signup():
	print ("handle_signup()")
	firstname = request.form["first_name"]
	lastname = request.form["last_name"]
	email = request.form["email"]

	#TODO: add hashing to password
	password = request.form["password"]
	pass_conf = request.form["password_confirmation"]


	username = email
	DOB = request.form["DOB"]
	sex = request.form["sex"]
	gender = "default"
	password_match = True

	if (password != pass_conf):
		password_match = False
		error = "Passwords do not match."
		return render_template('signup.html', error = error)

	cursor = conn.cursor()
	query = "SELECT * FROM accounts WHERE userName = %s"
	cursor.execute(query, (email))
	data = cursor.fetchone()
	cursor.close()

	error = None
	if (not data):
		return redirect(url_for("login"))
	else:
		error = "An account for this email is already active."
		return render_template('signup.html', error = error)

	cursor = conn.cursor()
	query = "INSERT INTO patient (firstName, lastName, email, dob, sex, gender) VALUES (%s,%s,%s,%s,%s,%s)"
	cursor.execute(query, (firstname, lastname, email, DOB, sex, gender))
	conn.commit()

	query = "INSERT INTO accounts (paid, userName, userPass, userType) VALUES (0,%s,%s,0)"
	cursor.execute(query, (username, password))
	conn.commit()

	cursor.close()
	return render_template('login.html', password_match = password_match)

@application.route('/files', methods=['GET', 'POST'])
def files():
	cur = conn.cursor()
	cur.execute("SELECT docName FROM documents")
	data = cur.fetchall()
	# print ("Data" + data)
	return render_template('files.html', data=data)


@application.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        return render_template('settings.html')

#Log out
@application.route('/logout', methods = ['GET', 'POST'])
def logout():
    if request.method == 'GET':
        return redirect(url_for('home'))


application.secret_key = 'Yekaterina Petrovna Zamolodchikova, but you can call me Katya!'

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
