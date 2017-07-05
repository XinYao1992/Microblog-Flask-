#!flask/bin/python

#Note how this script is completely generic. All the application specific pathnames are imported from the config file. When you start your own 
#project you can just copy the script to the new app's directory and it will work right away.

from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from myapp import db

import os.path

db.create_all()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
	api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
	api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
	api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))

#After you run the command you will have a new myapp.db file. This is an empty sqlite database, created from the start to support migrations. 
#You will also have a db_repository directory with some files inside. This is the place where SQLAlchemy-migrate stores its data files. Note 
#that we do not regenerate the repository if it already exists. This will allow us to recreate the database while leaving the existing 
#repository if we need to.