from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from myapp import app_obj, db, lm, oid
from .forms import LoginForm, EditForm
from .models import User
from datetime import datetime

# render_template uses Jinja2, and Jinja2 is a part of flask framework

@app_obj.before_request#Any functions that are decorated with before_request will run before the view function each time a request is received
def before_request():
	g.user = current_user#The current_user global is set by Flask-Login
	if g.user.is_authenticated:
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()




@app_obj.route('/login', methods=['GET', 'POST'])#This tells Flask that this view function accepts GET and POST requests.  Without this the view will only accept GET requests. We will want to receive the POST requests, these are the ones that will bring in the form data entered by the user.
@oid.loginhandler# it tells Flask-OpenID that this is our login view function
def login():
	#At the top of the function body we check if g.user is set to an authenticated user, and in that case we redirect to the index page. 
	#The idea here is that if there is a logged in user already we will not do a second login on top.
	#The g global is setup by Flask as a place to store and share data during the life of a request. 
	#The url_for function that we used in the redirect call is defined by Flask as a clean way to obtain the URL for a given view function. 
	#If you want to redirect to the index page you may very well use redirect('/index'), but there are very good reasons to let Flask build 
	#URLs for you.
	if g.user is not None and g.user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	#The validate_on_submit method does all the form processing work.
	#If you call it when the form is being presented to the user (i.e. before the
	# user got a chance to enter data on it) then it will return False, so in that case you know that you have to render the template.
	#When validate_on_submit is called as part of a form submission request, it will gather all the data, 
	#run all the validators attached to fields, and if everything is all right it will return True, indicating that the data is valid 
	#and can be processed. This is your indication that this data is safe to incorporate into the application.
	if form.validate_on_submit():
		#The flash function is a quick way to show a message on the next page presented to the user. In this case we will use it for debugging, 
		#since we don't have all the infrastructure necessary to log in users yet, we will instead just display a message that shows the submitted 
		#data. The flash function is also extremely useful on production servers to provide feedback to the user regarding an action.
		#flash('Login requested for OpenID="%s", remember_me=%s' %
			#(form.openid.data, str(form.remember_me.data)))

		#it runs when we get a data back from the login form
		#First we store the value of the remember_me boolean in the flask session, not to be confused with the db.session from Flask-SQLAlchemy. 
		#We've seen that the flask.g object stores and shares data though the life of a request. The flask.session provides a much more complex 
		#service along those lines. Once data is stored in the session object it will be available during that request and any future requests 
		#made by the same client. Data remains in the session until explicitly removed. To be able to do this, Flask keeps a different session 
		#container for each client of our application.
		#The oid.try_login call in the following line is the call that triggers the user authentication through Flask-OpenID. The function takes 
		#two arguments, the openid given by the user in the web form and a list of data items that we want from the OpenID provider. Since we 
		#defined our User class to include nickname and email, those are the items we are going to ask for.
		session["remember_me"] = form.remember_me.data
		return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])

		# #This function tells the client web browser to navigate to a different page instead of the one requested
		# return redirect("/index")
	return render_template("login.html",
			title = "Sign In",
			form = form,
			providers=app_obj.config['OPENID_PROVIDERS']
		)




#First, we have to write a function that loads a user from the database.
#Note how this function is registered with Flask-Login through the lm.user_loader decorator. Also remember that user ids in Flask-Login are 
#always unicode strings, so a conversion to an integer is necessary before we can send the id to Flask-SQLAlchemy.
@lm.user_loader
def load_user(id):
	return User.query.get(int(id))






@oid.after_login
#The resp argument passed to the after_login function contains information returned by the OpenID provider.
def after_login(resp):
	#The first if statement is just for validation. We require a valid email, so if an email was not provided we cannot log the user in.
	if resp.email is None or resp.email == "":
		flash("Invalid login, Please try again.")
		return redirect(url_for('login'))
	#Next, we search our database for the email provided. If the email is not found we consider this a new user, so we add a new user 
	#to our database, pretty much as we have learned in the previous chapter. Note that we handle the case of a missing nickname, since 
	#some OpenID providers may not have that information.
	user = User.query.filter_by(email=resp.email).first()
	if user is None:
		nickname = resp.nickname
		if nickname is None or nickname == "":
			nickname = resp.email.split('@')[0]
		nickname = User.make_unique_nickname(nickname)
		user = User(nickname=nickname, email=resp.email)
		db.session.add(user)
		db.session.commit()
	#After that we load the remember_me value from the Flask session, this is the boolean that we stored in the login view function, if it is available.
	remember_me = False
	if 'remember_me' in session:
		remember_me = session["remember_me"]
		session.pop("remember_me", None)
	#Then we call Flask-Login's login_user function, to register this is a valid login.
	login_user(user, remember = remember_me)
	#Finally, in the last line we redirect to the next page, or the index page if a next page was not provided in the request.
	#The concept of the next page is simple. Let's say you navigate to a page that requires you to be logged in, but you aren't just yet. 
	#In Flask-Login you can protect views against non logged in users by adding the login_required decorator. If the user tries to access 
	#one of the affected URLs then it will be redirected to the login page automatically. Flask-Login will store the original URL as the next 
	#page, and it is up to us to return the user to this page once the login process completed.
	return redirect(request.args.get("next") or url_for('index'))







@app_obj.route("/")
@app_obj.route('/index')
@login_required# First, we have added the login_required decorator. This will ensure that this page is only seen by logged in users.
def index():
	user = g.user#we pass g.user down to the template, instead of the fake object we used in the past.
	posts = [
		{
			'author' : {'nickname' : 'John'},
			'body' : 'Beautiful day in Portland!'
		}, 
		{
			'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!' 
		}
	]
	return render_template('index.html', title='Home', user=user, posts=posts)

@app_obj.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))







#In this case we have an argument in it, which is indicated as <nickname>. This translates into an argument of the same name added to the view 
#function. When the client requests, say, URL /user/miguel the view function will be invoked with nickname set to 'miguel'.
@app_obj.route('/user/<nickname>')
@login_required
def user(nickname):
	#First we try to load the user from the database, using the nickname that we received as argument.
	user = User.query.filter_by(nickname=nickname).first()
	#If that doesn't work then we just redirect to the main page with an error message
	if user == None:
		flash('User %s not found.' %nickname)
		return redirect(url_for('index'))
	#some fake posts
	posts = [
		{'author' : user, 'body' : 'Test post #1'},
		{'author' : user, 'body' : 'Test post #2'}
	]
	return render_template('user.html', user=user, posts=posts)







@app_obj.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
	form = EditForm(g.user.nickname)
	if form.validate_on_submit():
		g.user.nickname = form.nickname.data
		g.user.about_me = form.about_me.data
		db.session.add(g.user)
		db.session.commit()
		flash("Your changes have been saved!")
		return redirect(url_for('edit'))
	else:
		form.nickname.data = g.user.nickname
		form.about_me.data = g.user.about_me
	return render_template('edit.html', form=form)






#To declare a custom error handler the errorhandler decorator is used
@app_obj.errorhandler(404)
def not_found_error(error):
	return render_template('404.html'), 404

@app_obj.errorhandler(500)
def internal_error(error):
	#If the exception was triggered by a database error then the database session is going to arrive in an invalid state, so we have to 
	#roll it back in case a working session is needed for the rendering of the template for the 500 error.
	db.session.rollback()
	return render_template('500.html'), 500































