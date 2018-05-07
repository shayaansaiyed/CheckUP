from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql

application = Flask(__name__)

application.config['UPLOAD_FOLDER'] = "./static/Documents/"

conn = pymysql.connect(host='localhost',
						port = 3306,
						user='checkupdb',
						# password='Strauss4life',
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
def home():
	print (str(session))
	# if session["username"]:
	if session:
		if session["username"]:
			return redirect("/graphs")
		return redirect("/start")
	else:
		return redirect("/start")

@application.route('/start')
def start():
	session["username"] = None
	return render_template("index 2.html")

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
	userID = session["username"]
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
	userID = session["username"]

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
	cursor.execute(query, (str(userID), weight, 0))
	conn.commit()

	query = "INSERT INTO data (userID, data, TypeID) VALUES (%s,%s,%s)"
	cursor.execute(query, (str(userID), heightFT, 1))
	conn.commit()

	query = "INSERT INTO data (userID, data, TypeID) VALUES (%s,%s,%s)"
	cursor.execute(query, (str(userID), heartRate, 2))
	conn.commit()

	query = "INSERT INTO data (userID, data, TypeID) VALUES (%s,%s,%s)"
	cursor.execute(query, (str(userID), bloodPressure, 3))
	conn.commit()

	query = "INSERT INTO data (userID, data, TypeID) VALUES (%s,%s,%s)"
	cursor.execute(query, (str(userID), bloodSugar, 4))
	conn.commit()

	cursor.close()
	return render_template('upload.html')

@application.route('/account', methods=['GET', 'POST'])
def account():
	cursor = conn.cursor()
	userID = session["username"]
	query = "SELECT * FROM patient WHERE userID = %s"
	cursor.execute(query, (str(userID)))
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

@application.route('/login', methods=['GET', 'POST'])
def login():
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


@application.route('/displayGraph', methods=['GET', 'POST'])
def displayGraph():
	userID = session["username"]
	if request.method == 'POST':
		typeID = request.form['typeID'];
		if(typeID is None):
			return redirect('/graphs')
		cursor = conn.cursor()
		query = "SELECT data FROM data WHERE userID = %s AND typeID = %s"
		cursor.execute(query, (userID,typeID))
		data = cursor.fetchall()
		yValues = []
		for j in data:
			yValues.append(j['data'])
		print()
		cursor = conn.cursor()
		query = "SELECT * FROM data WHERE userID = %s AND typeID = %s"
		cursor.execute(query, (userID,typeID))
		if(typeID == "0"):
			title = "Height"
		elif(typeID ==  "1"):
			title = "Weight"
		elif(typeID == "2"):
			title = "Blood Pressure"
		elif(typeID == "3"):
			title = "Heart Rate"
		elif(typeID == "4"):
			title = "Blood Sugar"
		else:
			title = "ERROR"

		data = cursor.fetchall()
		xValues = []
		for j in data:
			date = str(j['date']).split()[0]
			xValues.append(date)
			print(j['date'])


		legend = 'Data'
		return render_template('graphs.html', values=yValues, labels=xValues, legend = legend, title = title)

@application.route('/graphs', methods=['GET', 'POST'])
def graphs(typeID=0):
	userID = session["username"]
	if request.method == 'GET':
		cursor = conn.cursor()
		query = "SELECT data FROM data WHERE userID = %s AND typeID = %s"
		cursor.execute(query, (userID,str(0)))
		data = cursor.fetchall()
		yValues = []
		for j in data:
			yValues.append(j['data'])
		print()
		cursor = conn.cursor()
		query = "SELECT * FROM data WHERE userID = %s AND typeID = %s"
		cursor.execute(query, (userID,str(0)))
		title = "Height"
		data = cursor.fetchall()
		xValues = []
		for j in data:
			date = str(j['date']).split()[0]
			xValues.append(date)
			print(j['date'])


		legend = 'Data'
		return render_template('graphs.html', values=yValues, labels=xValues, legend = legend, title = title)

@application.route('/signup', methods=['GET', 'POST'])
def signup():
	print ("signup()")
	return render_template('signup.html')

@application.route('/handle_signup', methods=['GET', 'POST'])
def handle_signup():
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
	if (data):
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
	userID = session["username"]
	cur = conn.cursor()
	query = "SELECT * FROM documents WHERE userID = %s"
	cur.execute(query, (userID))
	data = cur.fetchall()
	# print ("Data" + data)
	return render_template('files.html', data=data)


@application.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        return render_template('settings.html')

#Log out
# @application.route('/logout', methods = ['GET', 'POST'])
# def logout():
#     if request.method == 'GET':
#         return redirect(url_for('home'))

@application.route('/logout', methods = ['GET', 'POST'])
def logout():
    session.clear()
    # session['username'] = None
    return redirect("/start")


application.secret_key = 'Yekaterina Petrovna Zamolodchikova, but you can call me Katya!'

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
