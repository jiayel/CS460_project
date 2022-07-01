######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for, flash, session
from flask_login import current_user
from flaskext.mysql import MySQL
import flask_login

#for image uploading
import os, base64

#for current date
from datetime import datetime
import time


mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '11111111'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	query = 'SELECT picture_id, imgdata, caption FROM Pictures ORDER BY picture_id DESC LIMIT 100'
	cursor.execute(query)
	all_photos = cursor.fetchall()
	return render_template('hello.html', message='Logged out',Photos=all_photos, base64=base64)

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')


@app.route("/register", methods=['POST'])
def register_user():
	try:
		First_name=request.form.get('First_name')
		Last_name = request.form.get('Last_name')
		email=request.form.get('email')
		password=request.form.get('password')
		Hometown = request.form.get('Hometown')
		Gender = request.form.get('Gender')
		Date_of_birth = request.form.get('Date_of_birth')

	except:
		print("couldn't find all tokens 1") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (First_name,Last_name, email, password,Hometown,Gender, Date_of_birth) VALUES ('{0}', '{1}','{2}','{3}','{4}','{5}','{6}')".format(First_name,Last_name, email, password,Hometown,Gender, Date_of_birth)))
		conn.commit()
		#log user in
		user = User()
		user.id = email

		flask_login.login_user(user)
		return render_template('profile.html', name=First_name, message='Account Created!')
	else:
		print("couldn't find all tokens 2")
		flash("Account has already been created, try another Email!", "info")
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getPhoto_by_Photoid(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE picture_id = '{0}'".format(photo_id))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('profile.html', name=flask_login.current_user.id, message="Here's your profile")


@app.route('/create_albums', methods =['GET', 'POST'])
@flask_login.login_required
def create_albums():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		Album_name = request.form.get('Album_name')
		date = datetime.now()
		cursor = conn.cursor()
		print(cursor.execute(
			"INSERT INTO Albums(Album_name,Date_of_creation, user_id) VALUES ('{0}','{1}','{2}')".format(Album_name, date, uid)))
		conn.commit()
		album_id = cursor.lastrowid
		return render_template('create_albums.html', album_id = album_id, uid =uid)
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('create_albums.html',uid =uid)

@app.route('/view_album', methods = ['GET', 'POST'])
@flask_login.login_required
def view_album():
		uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		cursor.execute("SELECT Album_id, Album_name, user_id FROM Albums WHERE user_id = '{0}'".format(uid))
		all_albums = cursor.fetchall()
		return render_template('view_album.html', all_albums = all_albums)

@app.route('/album_content/<album_id>', methods =['GET','POST'])
def album_content(album_id):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption,Album_id FROM Pictures WHERE  Album_id ='{0}'".format(album_id))
	all_photos = cursor.fetchall() # a list of tuples, [(imgdata, pid, caption), ...]
	# print(all_photos)
	return render_template('album_content.html', all_photos=all_photos, album_id=album_id,base64=base64)

from base64 import b64encode
@app.route('/view_photo/<photo_id>', methods = ['GET','POST'])
def view_photo(photo_id):
	#show photo
	cursor = conn.cursor()
	cursor.execute(
		"SELECT imgdata, picture_id, caption,Album_id FROM Pictures WHERE picture_id = '{0}'".format(
			photo_id))
	image = cursor.fetchone()[0]  # a list of tuples, [(imgdata, pid, caption), ...]

	#show comment
	cursor.execute(
		"SELECT C.text, U.First_name FROM Comments C, Users U WHERE C.user_id = U.user_id AND C.picture_id = '{0}'".format(photo_id)
	)
	all_comments = cursor.fetchall()

	# find all likes
	query = 'SELECT user_id, picture_id FROM Likes'
	cursor.execute(query)
	likers = []
	for item in cursor:
		if int(item[1]) == int(photo_id):
			likers.append(int(item[0]))

	# find names of all likers
	query = 'SELECT first_name, user_id FROM Users'
	cursor.execute(query)
	likedby = []
	for item in cursor:
		if int(item[1]) in likers:
			likedby.append([item[1], item[0]])


	#get tags
	cursor = conn.cursor()
	cursor.execute(
		"SELECT tag_name FROM Tags_and_pics WHERE picture_id = '{0}'".format(
			photo_id))
	tags= cursor.fetchall()

	# if logged in
	if session.get('loggedin'):
		uid = getUserIdFromEmail(flask_login.current_user.id)
		if uid in likers:
			likedby = True
		else:
			likedby = False

	return render_template('view_photo.html',photo_id=photo_id,image=image,base64=base64, all_comments= all_comments,tags=tags, likedby = likedby)

@app.route('/add_comment/<photo_id>', methods =["GET", "POST"])
def add_comment(photo_id):
	comment = request.form.get('Comment')
	date = datetime.now()
	cursor = conn.cursor()
	if current_user.is_authenticated:
		uid = flask_login.	uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor.execute("INSERT INTO Comments(text, Date, picture_id,user_id) VALUES ('{0}','{1}','{2}','{3}')".format(comment, date, photo_id, uid))
	else:

		uid = 4 #anaoymous userid =4
		cursor.execute("INSERT INTO Comments(text, Date, picture_id,user_id) VALUES ('{0}','{1}','{2}','{3}')".format(comment, date, photo_id,uid))
	conn.commit()
	return redirect(url_for('view_photo', photo_id=photo_id))

@app.route('/like/<photo_id>', methods=["GET", "POST"])
@flask_login.login_required
def like(photo_id):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor.execute("INSERT INTO Likes (user_id, picture_id) VALUES ('{0}','{1}')".format(uid, photo_id))
	conn.commit()
	return redirect(url_for('view_photo', photo_id=photo_id))


@app.route('/delete_photo/<photo_id>', methods=["GET", "POST"])
@flask_login.login_required
def delete_photo(photo_id):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Comments WHERE picture_id = '{0}'".format(photo_id))
	cursor.execute("DELETE FROM Likes WHERE picture_id = '{0}'".format(photo_id))
	cursor.execute("DELETE FROM Pictures WHERE picture_id = '{0}'".format(photo_id))
	conn.commit()
	return redirect(url_for('protected'))

@app.route('/delete_album/<album_id>', methods =["GET", "POST"])
@flask_login.login_required
def delete_album(album_id):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Pictures WHERE Album_id ='{0}'".format(album_id))
	cursor.execute("DELETE FROM Albums WHERE Album_id = '{0}'".format(album_id))
	conn.commit()
	return redirect(url_for('protected'))



#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload_photo/<album_id>', methods=['GET', 'POST'])
@flask_login.login_required
def upload_photo(album_id):
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		tags = request.form.get('tag').split(" ")
		photo_data =imgfile.read()
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Pictures (imgdata, user_id, caption,Album_id) VALUES (%s, %s, %s,%s)",(photo_data, uid, caption,album_id))
		conn.commit()
		#add tag into tag_and_pics
		query = 'select picture_id from Pictures ORDER BY picture_id DESC LIMIT 1'
		cursor.execute(query)
		photo_id = cursor.fetchall()
		print(photo_id)
	
		for i in range(len(tags)):
			cursor = conn.cursor()
			query = "SELECT * FROM Tags WHERE tag_name ='{0}'".format(tags[i])
			if not cursor.execute(query):
				cursor.execute("INSERT INTO Tags (tag_name) VALUES (%s)",(tags[i]))
				conn.commit()
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Tags_and_pics (tag_name, picture_id) VALUES (%s, %s)",(tags[i], photo_id))
			conn.commit()
		#get image data
		query = "SELECT imgdata, picture_id, caption,Album_id FROM Pictures WHERE Album_id ='{0}'".format(album_id)
		cursor.execute(query)
		all_photos = cursor.fetchall()
		return render_template('album_content.html',album_id=album_id, all_photos=all_photos,base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		cursor = conn.cursor()
		query = 'SELECT tag_name FROM Tags'
		cursor.execute(query)
		all_tags = cursor.fetchall()
		print(all_tags)
		return render_template('upload_photo.html',album_id=album_id,Tag=all_tags)


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Pictures (imgdata, caption) VALUES (%s, %s )''', (photo_data, caption))
		conn.commit()
		return render_template('profile.html', message='Photo uploaded!', base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code


#begin add friends and view friends page
@app.route('/friend', methods=['GET','POST'])
@flask_login.login_required
def friend():
	if request.method =='POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		f_email = request.form.get('Friend')
		fid = getUserIdFromEmail(f_email)
		user_email = flask_login.current_user.id
		cursor = conn.cursor()
		print(cursor.execute("INSERT INTO Friends(Friends_id, Friends_email,user_email, user_id) VALUES ('{0}','{1}','{2}','{3}')".format(fid,f_email,user_email,uid)))
		conn.commit()
		return render_template('friend.html', name=flask_login.current_user.id, message='Friend Added!')
	else:
		return render_template('friend.html')

@app.route('/view_friend', methods = ['GET','POST'])
@flask_login.login_required
def view_friend():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT Friends_email FROM Friends WHERE user_id = '{0}'".format(uid))
	Friends= cursor.fetchall()
	Friends = list(Friends)
	cursor=conn.cursor()
	cursor.execute("SELECT user_email FROM Friends WHERE Friends_id ='{0}'".format(uid))
	Friends.append(list(cursor.fetchall()))
	final = []
	for i in Friends:
		if i not in final:
			final.append(i)
	# if final == []:
	# 	return render_template('view_friend.html', friends = i)
	return render_template('view_friend.html', friends = i)
#end add and view friends page

@app.route('/tag', methods = ['GET','POST'])
def view_tag():
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Tags")
	tags = list(cursor.fetchall())
	cleaned_tags=[]
	for tag in tags:
		cleaned_tags.append(tag[0])
	return render_template('tag.html', tags = cleaned_tags)

@app.route('/create_tag', methods = ['GET','POST'])
def create_tag():
	if request.method == "POST":
		new_tag = request.form.get('tag')
		cursor = conn.cursor()
		if cursor.execute("SELECT * FROM Tags WHERE tag_name = '{0}'".format(new_tag)):
			return render_template('create_tag.html',message="Oops! this tag was already created. Try another one!")
		else:
			print(cursor.execute("INSERT INTO Tags(tag_name) VALUES ('{0}')".format(new_tag)))
			conn.commit()
			flash("new tag has been added!!!",'info')
			return flask.redirect(flask.url_for('view_tag'))
	else:
		return render_template('create_tag.html',message="Create a new tag!")

#for viewing tags
@app.route('/view_tag/<tag>', methods =["GET"])
def view_alltag(tag):
	cursor = conn.cursor()
	print(type(tag))
	query = "SELECT Pictures.picture_id, imgdata, caption FROM Tags_and_pics, Pictures where Tags_and_pics.tag_name='{0}' and Pictures.picture_id=Tags_and_pics.picture_id".format(tag)
	cursor.execute(query)
	all_photos = cursor.fetchall()
	return render_template('view_tags.html',Photos=all_photos,base64=base64)


#default page
@app.route("/", methods=['GET', 'POST'])
def hello():

	cursor = conn.cursor()
	query = 'SELECT picture_id, imgdata, caption FROM Pictures ORDER BY picture_id DESC LIMIT 100'
	cursor.execute(query)
	all_photos = cursor.fetchall()
	query ="SELECT Album_id, Album_name, user_id FROM Albums ORDER BY Album_id DESC LIMIT 100"
	cursor.execute(query)
	all_albums = cursor.fetchall()
	if current_user.is_authenticated:
		email = flask_login.current_user.id
	else:
		email = False
	print(email)
	return render_template('hello.html', message='Welecome to Photoshare',Photos=all_photos,base64=base64, all_albums=all_albums, email=email)


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
