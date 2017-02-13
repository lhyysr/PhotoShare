######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Craig Einstein <einstein@bu.edu>
# Edited by: Haoyuan Liu <lhyysr@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

# for image uploading
from werkzeug import secure_filename
import os, base64

# for creation date
import datetime

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'heresthedata!'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


## begin code used for login
############################
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
#################
## end login code

# /unauthorized
@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

## helper functions
###################
def getUserIdFromEmail(email):
	cursor = conn.cursor()
	print cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

def isAlbumNameUnique(name):
	print "is album name unique"
	user_email=flask_login.current_user.id
	user_id=getUserIdFromEmail(user_email)
	cursor = conn.cursor()
	if cursor.execute("SELECT name FROM Albums AS a WHERE a.user_id='{0}' AND a.name='{1}'".format(user_id, name)):
		return False
	else:
		return True

def get_user_name():
	print "get user name"
	user_email = flask_login.current_user.id
	cursor = conn.cursor()
	print cursor.execute("SELECT first_name  FROM Users WHERE email = '{0}'".format(user_email))
	return cursor.fetchone()[0]

def get_user_albums():
	print "get user albums"
	user_email = flask_login.current_user.id
	cursor = conn.cursor()
	print cursor.execute("SELECT a.name, a.album_id FROM Users AS u, Albums AS a WHERE u.email='{0}' AND a.user_id = u.user_id".format(user_email))
	return cursor.fetchall() # [(name, album_id),...]

def get_user_id():
	print 'get user id'
	return getUserIdFromEmail(flask_login.current_user.id)

def get_user_id_by(photo_id):
	print "get user id from photo id"
	cursor = conn.cursor()
	print cursor.execute("SELECT user_id FROM User_Photos WHERE photo_id = '{0}'".format(photo_id))
	return cursor.fetchone()[0]

def get_user_tags():
	print "get all user tags"
	user_id = get_user_id()
	cursor = conn.cursor()
	print cursor.execute("SELECT DISTINCT ac.word FROM Albums AS a, Photos AS p, Associate AS ac WHERE a.user_id = '{0}' AND p.album_id = a.album_id AND ac.photo_id = p.photo_id".format(user_id))
	return [w[0] for w in cursor.fetchall()]

def get_user_photos():
	print 'get all user photos'
	user_id = get_user_id()
	cursor = conn.cursor()
	print cursor.execute("SELECT p.data, p.photo_id, p.caption, p.album_id FROM Photos AS p, User_Photos AS up WHERE up.user_id = '{0}' AND p.photo_id = up.photo_id".format(user_id))
	return cursor.fetchall() # [(data, photo_id, caption, album_id), ...]

def get_user_tag_photos(tag):
	print "get user tag photos"
	user_id = get_user_id()
	cursor = conn.cursor()
	print cursor.execute("SELECT p.data, p.photo_id, p.caption, p.album_id FROM Photos AS p WHERE p.photo_id IN (SELECT up.photo_id FROM User_Photos AS up WHERE up.user_id = '{0}') AND p.photo_id IN (SELECT a.photo_id FROM Associate AS a WHERE a.word = '{1}')".format(user_id, tag))
	return cursor.fetchall() # [(data, photo_id, caption, album_id), ...]

def get_user_friends():
	print "get user friends"
	user_id = get_user_id()
	cursor = conn.cursor()
	print cursor.execute("SELECT u.user_id, u.first_name, u.last_name FROM Users AS u, Friends AS f WHERE f.user_id = '{0}' AND u.user_id = f.friend_id".format(user_id))
	return cursor.fetchall() # [(user_id, first_name, last_name)]

def get_album_id(albumName):
	print 'get album id'
	user_id = get_user_id()
	cursor = conn.cursor()
	print cursor.execute("SELECT album_id FROM Albums WHERE user_id = '{0}' AND name = '{1}'".format(user_id, albumName))
	return cursor.fetchone()[0]
	
def get_album_name(album_id):
	print 'get album name from album id'
	cursor = conn.cursor()
	print cursor.execute("SELECT name FROM Albums WHERE album_id = '{0}'".format(album_id))
	return cursor.fetchone()[0]

def get_album_photos(album_id):
	print 'get photos from album'
	cursor = conn.cursor()
	print cursor.execute("SELECT data, photo_id, caption, album_id FROM Photos WHERE album_id = '{0}'".format(album_id))
	return cursor.fetchall() #NOTE list of tuples, [(data, photo_id, caption, album_id), ...]

def get_all_photos():
	print "get all photos"
	cursor = conn.cursor()
	print cursor.execute("SELECT data, photo_id, caption, album_id FROM Photos")
	return cursor.fetchall() #NOTE list of tuples, [(data, photo_id, caption, album_id), ...]

def get_all_tags():
	print "get all tags"
	cursor = conn.cursor()
	print cursor.execute("SELECT DISTINCT word FROM Tags")
	return [w[0] for w in cursor.fetchall()]

def get_pop_tags():
	print "get the most popular tags"
	cursor = conn.cursor()
	print cursor.execute("SELECT word FROM Tags WHERE popularity = (SELECT MAX(popularity) FROM Tags)")
	return [w[0] for w in cursor.fetchall()]

def get_all_tag_photos(tag):
	print "get all tag photos"
	cursor = conn.cursor()
	print cursor.execute("SELECT p.data, p.photo_id, p.caption, p.album_id FROM Photos AS p, Associate AS a WHERE p.photo_id = a.photo_id AND a.word = '{0}'".format(tag))
	return cursor.fetchall() # [(data, photo_id, caption, album_id), ...]

def get_photo_tags(photo_id):
	print "get tags of chosen photo"
	cursor = conn.cursor()
	print cursor.execute("SELECT a.word FROM Associate AS a WHERE a.photo_id = '{0}'".format(photo_id))
	return [w[0] for w in cursor.fetchall()]

def get_photo_comments(photo_id):
	print "get comments of chosen photo"
	cursor = conn.cursor()
	print cursor.execute("SELECT u.first_name, c.txt, c.doc FROM Comment AS c, Users AS u WHERE c.photo_id = '{0}' AND u.user_id = c.user_id".format(photo_id))
	return cursor.fetchall()   # [(first_name, txt, doc),...]

def get_photo_likes(photo_id):
	print "get people who like the chosen photo"
	cursor = conn.cursor()
	print cursor.execute("SELECT u.first_name FROM Likes AS l, Users AS u WHERE l.photo_id = '{0}' AND u.user_id = l.user_id".format(photo_id))
	return [n[0] for n in cursor.fetchall()]

def get_photo(photo_id):
	print "get photo by photo id"
	cursor = conn.cursor()
	print cursor.execute("SELECT data, photo_id, caption, album_id FROM Photos AS p WHERE p.photo_id = '{0}'".format(photo_id))
	return cursor.fetchone() # [(data, photo_id, caption, album_id), ...]

def get_tag_popularity(tag):
	print "get tag popularity"
	cursor = conn.cursor()
	print cursor.execute("SELECT COUNT(*) FROM Associate AS a WHERE a.word = '{0}'".format(tag))
	return cursor.fetchone()[0]

def get_active_users():
	print "get active users"
	cursor = conn.cursor()
	print cursor.execute("SELECT first_name, contribution FROM Users WHERE user_id != 1 ORDER BY contribution DESC LIMIT 10")
	return cursor.fetchall() # [(name, contribution), ...]

def search_photos(tags_list):
	print "search photos with tags in the list"
	photos = set(get_all_photos())
	for tag in tags_list:
		photos = photos.intersection(get_all_tag_photos(tag))
	return list(photos)

def search_people(name):
	print "search peopel with name"
	cursor = conn.cursor()
	print cursor.execute("SELECT u.user_id, u.first_name, u.last_name FROM Users AS u WHERE u.first_name = '{0}' OR u.last_name = '{0}'".format(name))
	return cursor.fetchall() # [(user_id, first_name, last_name),...]
#######################
## end helper functions

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

# /    , home page  
@app.route("/", methods=['GET', 'POST'])
def hello():
	if flask.request.method == 'GET':
		tags = get_all_tags()
		poptags = get_pop_tags()
		all_photos = get_all_photos()
		active_users = get_active_users() #[(name, con)...]
		user_name = ''
		try:
			user_name = get_user_name()
		except:
			pass
		if user_name == '': # not logged in
			login = False
			return render_template('hello.html', login = login, active= active_users, tags = tags , poptags = poptags, photos = all_photos)
		else: # logged in
			login = True
			return render_template('hello.html', login = login, active= active_users, name = user_name, tags = tags, poptags = poptags, photos = all_photos)
	else: # POST
		tags = request.form.get("tags")
		tags_list = tags.split()
		print tags_list
		photos = search_photos(tags_list)
		return render_template('tag.html', tag=tags, name="All Users", private=False, photos=photos)

# /comment  
@app.route("/comment", methods=['GET', 'POST'])
def comment():
	if flask.request.method == 'POST':
		# direct from home page
		photo_id = request.form.get("submit") # [(data, photo_id, caption, album_id), ...]
		comments = get_photo_comments(photo_id) # [(first_name, txt, doc),...]
		likes = get_photo_likes(photo_id)
		number = len(likes)
		photo = get_photo(photo_id)
		# direct form comment page
		comment = request.form.get('comment')
		like = request.form.get('like')
		
		if comment != None:
			cursor = conn.cursor()
			doc = datetime.datetime.now()
			user_id = None
			try:
	 			user_id = get_user_id()
	 		except:
	 			pass
	 		print user_id
 	 		if user_id != None: # logged in
	 			# owner cannot comment his own photos
	 			owner_id = get_user_id_by(photo_id)
	 			if owner_id == user_id:
	 				return render_template('comment.html', comments=comments, photo=photo, likes=likes, number=number, message="Sorry! You cannot comment your own photo!")
	 			# else
	 			print cursor.execute("INSERT INTO Comment (user_id, photo_id, txt, doc) VALUES ('{0}', '{1}', '{2}', '{3}')".format(user_id, photo_id, comment, doc))		
				print cursor.execute("UPDATE Users SET contribution = contribution+1 WHERE user_id = '{0}'".format(user_id))
			else: # not logged in
				user_id = 1
				print cursor.execute("INSERT INTO Comment (user_id, photo_id, txt, doc) VALUES ('{0}', '{1}', '{2}', '{3}')".format(user_id, photo_id, comment, doc))
			conn.commit()
			# comments changed
			comments = get_photo_comments(photo_id) # [(first_name, txt, doc),...]

		if like != None:
			photo_id = like
			cursor = conn.cursor()
			user_id = None
			try:
	 			user_id = get_user_id()
	 		except:
	 			pass
	 		print user_id
 	 		if user_id != None: # logged in
 	 			print cursor.execute("INSERT INTO Likes (user_id, photo_id) VALUES ('{0}', '{1}')".format(user_id, photo_id))
 	 		else: # not logged in
 	 			comments = get_photo_comments(photo_id) # [(first_name, txt, doc),...]
				likes = get_photo_likes(photo_id)
				number = len(likes)
				photo = get_photo(photo_id)
 	 			return render_template('comment.html', comments=comments, photo=photo, likes=likes, number=number, message="Sorry! You need you login to like a photo!")
			conn.commit()
			# likes changed
			comments = get_photo_comments(photo_id) # [(first_name, txt, doc),...]
			likes = get_photo_likes(photo_id)
			number = len(likes)
			photo = get_photo(photo_id)

		return render_template('comment.html', comments=comments, photo=photo, likes=likes, number=number)

# /register
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html')  

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		first_name=request.form.get('first_name')
		last_name=request.form.get('last_name')
		dob=request.form.get('dob')
		hometown=request.form.get('hometown')
		gender=request.form.get('gender')
	except:
		print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		# insert a tuple into User with user's info
		print cursor.execute("INSERT INTO Users (email, password, first_name, last_name, dob, hometown, gender, contribution) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', 0)".format(email, password, first_name, last_name, dob, hometown, gender))
		conn.commit()
		# create a default album for newly registered user
		print cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
		user_id=cursor.fetchone()[0]
		name='default'
		doc=datetime.datetime.now()
		cursor.execute("INSERT INTO Albums (user_id, name, doc) VALUES ('{0}', '{1}', '{2}')".format(user_id, name, doc))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return flask.redirect(flask.url_for('hello'))
	else:
		print "the email has been registered"
		return render_template('register.html', message='Email already in use! Use another one or ')

# /login
@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
				<title>Login</title>
				<h1>Log in to your account:</h1>
				<form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   	</form></br>
			   	<ul>
			   		<li><a href='/register'>Register</a></li>
		   			<li><a href='/'>Home</a></li>
		   		</ul>
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
			return flask.redirect(flask.url_for('hello')) #protected is a function defined in this file
	#information did not match
	return '''
			<title>Login Fail</title>
			<h1>The email/password entered was wrong!</h1>
			<a href='/login'>Login again</a>
			</br><a href='/register'>or Register</a>
			'''

# /logout
@app.route('/logout')
def logout():
	flask_login.logout_user()
	return '''
			<title>Logout</title>
			<h1>You have successfully logged out!</h1>
			<ul>
				<li><a href="/register">Register</a>
				<li><a href="/login">Login</a></li>
				<li><a href='/'>Home</a></li>
			</ul>
		   '''

# /profile, login required
@app.route('/profile', methods=['GET', 'POST'])
@flask_login.login_required
def protected():
	user_name = get_user_name()
	friends = get_user_friends() # [(user_id, first_name, last_name),...]
	if flask.request.method == 'GET':
		return render_template('profile.html', name=user_name, friends=friends)
	else: # POST
		value = request.form.get("submit")
		if value == "search":
			name = request.form.get("name")
			people = search_people(name)
			if people == ():
				return render_template('profile.html', name=user_name, friends=friends, message="The person you searched doesn't exist!")
			return render_template('profile.html', name=user_name, friends=friends, people=people)
		else: # follow
			print "follow "+value
			user_id = get_user_id()
			cursor = conn.cursor()
			if cursor.execute("SELECT * FROM Friends AS f WHERE f.user_id = '{0}' AND f.friend_id = '{1}'".format(user_id, value)) != 0:
				message = "You have already followed him/her!"
				return render_template('profile.html', name=user_name, friends=friends, message=message)
			else: # add friend
				print cursor.execute("INSERT INTO Friends (user_id, friend_id) VALUES ('{0}','{1}')".format(user_id, value))
				conn.commit()
				friends = get_user_friends() # [(user_id, first_name, last_name),...]
				message = "You followed a new friend!"
				return render_template('profile.html', name=user_name, friends=friends, message=message)

# /albums, login required
@app.route('/albums', methods=['GET', 'POST'])
@flask_login.login_required
def edit_albums():
	user_name=get_user_name()
	user_albums=get_user_albums() # [(name, album_id),...]
	user_id=get_user_id()
	if flask.request.method == 'GET':
		return render_template('albums.html', name=user_name, albums=user_albums)
	else: # 'POST'
		edit = request.form.get('submit')
		print edit
		# create a new album
		if edit == 'create':
			name = request.form.get('name')
			test = isAlbumNameUnique(name)
			# new album does not exit --> create a new tuple in Albums
			if test:
				doc = datetime.datetime.now()
				cursor = conn.cursor()
				print cursor.execute("INSERT INTO Albums (user_id, name, doc) VALUES ('{0}', '{1}', '{2}')".format(user_id, name, doc))
				conn.commit()
				user_albums = get_user_albums()
				return render_template('albums.html', name=user_name, albums=user_albums, CreatedAlbum=name)
			# disallow the same album name to be used by the same user
			else:
				print "the album name has been used"
				return render_template('albums.html', name=user_name, albums=user_albums, message="The album name has been used!")
		# delete a existing album
		elif edit == 'delete':
			name = request.form.get('name')
			if name not in user_albums:
				return render_template('albums.html', name=user_name, albums=user_albums, message="The album you wanted to delete doesn't exit!")
			else:
				cursor = conn.cursor()
				print cursor.execute("DELETE FROM Albums WHERE name='{0}'".format(name))
				conn.commit()
				user_albums = get_user_albums()
				return render_template('albums.html', name=user_name, albums=user_albums, DeletedAlbum=name)
		# rename an existing album
		elif edit == 'rename':
			name = request.form.get('name')
			if name not in [a[0] for a in user_albums]: # [(name, album_id),...]
				return render_template('albums.html', name=user_name, albums=user_albums, message="The album you wanted to modify doesn't exit!")
			else:
				newName = request.form.get('newName')
				test = isAlbumNameUnique(newName)
				if test:
					cursor = conn.cursor()
					print cursor.execute("UPDATE Albums SET name='{0}' WHERE name='{1}'".format(newName, name))
					conn.commit()
					user_albums = get_user_albums()
					return render_template('albums.html', name=user_name, albums=user_albums, ModifiedAlbum=name, NewName=newName)
				else:
					print "the album name has been used"
					return render_template('albums.html', name=user_name, albums=user_albums, message="The album name has been used!")

# /album?album_id=, login required
@app.route('/album', methods=['GET','POST'])
@flask_login.login_required
def show_album():
	if flask.request.method == 'GET':
		user_name = get_user_name()
		album_id = request.args.get('album_id')
		album_name = get_album_name(album_id)
		album_photos = get_album_photos(album_id) #[(data, photo_id, caption, album_id), ...]
		return render_template('album.html', album=album_name, name=user_name, photos=album_photos)
	elif flask.request.method == 'POST':
		form_value = request.form.get('submit').split()
		form_value = map(str, form_value)
		print form_value
		edit = form_value[0]
		photo_id = form_value[1]
		album_id = form_value[2]
		if edit == '0': # edit caption
			print 'execute edit'
			caption = request.form.get('caption')
			cursor = conn.cursor()
			print cursor.execute("UPDATE Photos SET caption = '{1}' WHERE photo_id = '{0}'".format(photo_id, caption))
			conn.commit()
		elif edit == '1': # delete photo
			print "execute delete"
			related_tags = get_photo_tags(photo_id)
			cursor = conn.cursor()
			print cursor.execute("DELETE FROM Photos WHERE photo_id = '{0}'".format(photo_id))
			user_id = get_user_id()
	 		print cursor.execute("UPDATE Users SET contribution = contribution-1 WHERE user_id = '{0}'".format(user_id))
			print related_tags
			for t in related_tags:
				popularity = get_tag_popularity(t)
				print cursor.execute("UPDATE Tags SET popularity = '{1}' WHERE word = '{0}'".format(t, popularity))
			conn.commit()
		user_name = get_user_name()
		album_name = get_album_name(album_id)
		album_photos = get_album_photos(album_id) #[(data, photo_id, caption, album_id), ...]
		return render_template('album.html', album=album_name, name=user_name, photos=album_photos) 

# /tag?tag=, login required
@app.route('/tag', methods=['GET','POST'])
# @flask_login.login_required
def show_tag():
	if flask.request.method == 'GET':
		flagViewTag = request.args.get('tag')
		flag = flagViewTag[0]
		view = flagViewTag[1]
		tag = flagViewTag[2:]
		if flag == '0': # user photos
			tag_photos = get_user_tag_photos(tag) #[(data, photo_id, caption, album_id), ...]
		elif flag == '1': # all photos
			tag_photos = get_all_tag_photos(tag) #[(data, photo_id, caption, album_id), ...]
		if view == '0': # public
			private = False
			user_name = "All Users"
		elif view == '1': # private
			private = True
			if flask_login.current_user.is_authenticated():
				user_name = get_user_name()
		print private
		return render_template('tag.html',tag=tag, name=user_name, private=private, photos=tag_photos)
	elif flask.request.method == 'POST':
		form_value = request.form.get('submit').split()
	 	form_value = map(str, form_value)
	 	print form_value
	 	edit = form_value[0]
	 	photo_id = form_value[1]
	 	if edit == '0': # edit caption
	 		print 'execute edit'
	 		caption = request.form.get('caption')
	 		cursor = conn.cursor()
	 		print cursor.execute("UPDATE Photos SET caption = '{1}' WHERE photo_id = '{0}'".format(photo_id, caption))
	 		conn.commit()
	 	elif edit == '1': # delete photo
	 		print "execute delete"
	 		related_tags = get_photo_tags(photo_id)
	 		cursor = conn.cursor()
	 		print cursor.execute("DELETE FROM Photos WHERE photo_id = '{0}'".format(photo_id))
	 		user_id = get_user_id()
	 		print cursor.execute("UPDATE Users SET contribution = contribution-1 WHERE user_id = '{0}'".format(user_id))
	 		print related_tags
			for t in related_tags:
				popularity = get_tag_popularity(t)
				print cursor.execute("UPDATE Tags SET popularity = '{1}' WHERE word = '{0}'".format(t, popularity))
	 		conn.commit()
	 	user_name = get_user_name()
		return render_template('tag.html', name=user_name, message="The photo you modified has been updated!")	

# /photos, login required
@app.route('/photos', methods=['GET','POST'])
@flask_login.login_required
def edit_photos():
	user_name = get_user_name()
	user_albums = get_user_albums()
	user_id = get_user_id()
	user_tags = get_user_tags()
	if flask.request.method == 'GET':
		return render_template('photos.html', name=user_name, albums=user_albums, tags=user_tags)
	#elif flask.request.method == 'POST':

# /upload, login required
@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	user_name = get_user_name()
	user_albums = get_user_albums() # [(name, album_id),...]
	print user_albums
	user_id = get_user_id()
	if request.method == 'POST':
		# read input from form
		albumName = request.form.get('album')
		if albumName not in [a[0] for a in user_albums]:
			return render_template('upload.html', UploadAlbum = albumName, albums=user_albums)
		album_id = get_album_id(albumName)
		imgfile = request.files['photo']
		photo_data = base64.standard_b64encode(imgfile.read())
		caption = request.form.get('caption')
		tags = request.form.get('tags').split()
		print tags
		# insert photo
		cursor = conn.cursor()
		print cursor.execute("INSERT INTO Photos (album_id, data, caption) VALUES ('{0}', '{1}', '{2}' )".format(album_id, photo_data, caption))
		print cursor.execute("UPDATE Users SET contribution = contribution+1 WHERE user_id = '{0}'".format(user_id))
		conn.commit()
		# insert & associate tags
		if tags != []:
			print cursor.execute("SELECT MAX(photo_id) FROM Photos")
			photo_id = cursor.fetchone()[0]	
			all_tags = get_all_tags()
			for word in tags:
				test = word not in all_tags
				if test:
					print cursor.execute("INSERT INTO Tags (word, popularity) VALUES ('{0}', 1)".format(word))
				else:
					print cursor.execute("UPDATE Tags SET popularity = popularity + 1 WHERE word = '{0}'".format(word))
				print cursor.execute("INSERT INTO Associate (photo_id, word) VALUES ('{0}', '{1}')".format(photo_id, word))
				conn.commit()
		return render_template('upload.html', message='New Photo Uploaded!', albums=user_albums)
	#The method is GET so we return a HTML form to upload the a photo.
	elif flask.request.method == 'GET':
		return render_template('upload.html', albums=user_albums)

# python app.py 
if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	app.run(port=5000, debug=True)
