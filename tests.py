#!flask/bin/python
import os
import unittest

from config import basedir
from myapp import app_obj, db
from myapp.models import User

class TestCase(unittest.TestCase):
	def setUp(self):
		app_obj.config['TESTING'] = True
		app_obj.config['WTF_CSRF_ENABLED'] = False
		app_obj.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
		self.app_obj = app_obj.test_client()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_avatar(self):
		u = User(nickname='john', email='john@example.com')
		avatar = u.avatar(128)
		expected = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
		assert avatar[0:len(expected)] == expected

	def test_make_unique_nickname(self):
		u = User(nickname='john', email='john@example.com')
		db.session.add(u)
		db.session.commit()
		nickname = User.make_unique_nickname('john')
		assert nickname != 'john'
		u = User(nickname=nickname, email='susan@example.com')
		db.session.add(u)
		db.session.commit()
		nickname2 = User.make_unique_nickname('john')
		assert nickname2 != 'john'
		assert nickname2 != nickname


if __name__ == '__main__':
	unittest.main()