CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess-haha'

#OpenID is an open technology standard that solves all of these problems. The OpenID technology will allow you to use your 
#Yahoo account to sign in to hundreds of websites! And this list is growing every day...
OPENID_PROVIDERS=[
	{'name': 'Yahoo', 'url':'https://me.yahoo.com'},
	{'name': 'AOL', 'url':'http://openid.aol.com/<username>'},
	{'name': 'Flickr', 'url':'http://www.flickr.com/<username>'},
	{'name': 'MyOpenID', 'url':'https://www.myopenid.com'}
]

#SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.
import os
basedir = os.path.abspath(os.path.dirname(__file__))

#The SQLALCHEMY_DATABASE_URI is required by the Flask-SQLAlchemy extension. This is the path of our database file.
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'myapp.db')
#The SQLALCHEMY_MIGRATE_REPO is the folder where we will store the SQLAlchemy-migrate data files.
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['you@example.com']