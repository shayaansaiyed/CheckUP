from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql

application = Flask(__name__)

conn = pymysql.connect(host='dbinstance.clvo2ema2nfj.us-east-2.rds.amazonaws.com',
					   port = 3306,
                       user='checkupdb',
                       password='Strauss4life',
                       db='checkupdb',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor
                       )

@application.route('/')
def start():
	cursor = conn.cursor()
	query = "SELECT * FROM login_credentials"
	cursor.execute(query)
	data = cursor.fetchall()
	print (data)
	cursor.close()
	return render_template("index.html", data = data)

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

@application.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')

@application.route('/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

@application.route('/graphs', methods=['GET', 'POST'])
def graphs():
    if request.method == 'GET':
        return render_template('graphs.html')

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


	username = request.form["username"]
	DOB = request.form["DOB"]
	sex = request.form["sex"]
	gender = "default"
	password_match = True

	
	if (password != pass_conf):
		password_match = False
		#TODO: show an error if the passwords do not match

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
    if request.method == 'GET':
        return render_template('files.html')

@application.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        return render_template('settings.html')
            
#Log out
@application.route('/logout', methods = ['GET', 'POST'])
def logout():
    if request.method == 'GET':
        return redirect(url_for('home'))




# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
