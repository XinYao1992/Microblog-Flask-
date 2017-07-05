from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from flask_openid import OpenID
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

app_obj = Flask(__name__)
app_obj.config.from_object("config")
db = SQLAlchemy(app_obj)


if not app_obj.debug:
	import logging
	from logging.handlers import SMTPHandler
	credentials = None
	if MAIL_USERNAME or MAIL_PASSWORD:
		credentials = (MAIL_USERNAME, MAIL_PASSWORD)
	mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure', credentials)
	mail_handler.setLevel(logging.ERROR)
	app_obj.logger.addHandler(mail_handler)

#Testing this on a development PC that does not have an email server is easy, thanks to Python's SMTP debugging server. Just open a 
#new console window (command prompt for Windows users) and run the following to start a fake email server:
#.      python -m smtpd -n -c DebuggingServer localhost:25.
#When this is running, the emails sent by the application will be received and displayed in the console window.


#The log file will go to our tmp directory, with name microblog.log. We are using the RotatingFileHandler so that there is a limit to the amount 
#of logs that are generated. In this case we are limiting the size of a log file to one megabyte, and we will keep the last ten log files 
#as backups.
if not app_obj.debug:
	import logging
	from logging.handlers import RotatingFileHandler
	file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 2014 * 1024, 10)
	file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
	app_obj.logger.setLevel(logging.INFO)
	file_handler.setLevel(logging.INFO)
	app_obj.logger.addHandler(file_handler)
	app_obj.logger.info('microblog startup')

lm = LoginManager()
lm.init_app(app_obj)
#Flask-Login needs to know what view logs users in.
lm.login_view = "login"
oid = OpenID(app_obj, os.path.join(basedir, 'tmp'))

from myapp import views, models