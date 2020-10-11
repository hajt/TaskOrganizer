from flask import Flask
from flask_testing import TestCase
from models import db, User, Task
import unittest
from app import app
from datetime import datetime, timedelta

class AppTest(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        db.init_app(app)
        return app


    def setUp(self):   
        db.create_all()
        

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class ModelsTest(AppTest):

    def test_create_user(self):
        user = User(username="Adam", email="adam.kowalski@mail.com")
        db.session.add(user)
        db.session.commit()
        users = User.query.all()
        assert user in users
        assert user in db.session
    

    def test_delete_user(self):
        user = User(username="Adam", email="adam.kowalski@mail.com")
        db.session.add(user)
        db.session.commit()
        user_ = User.query.get(1)
        db.session.delete(user_)
        db.session.commit()
        users = User.query.all()
        assert user_ not in users
        assert user not in db.session


    def test_add_task(self):
        user = User(username="Adam", email="adam.kowalski@mail.com")
        task = Task(title='title', expired_date=datetime.now(), user=user)
        db.session.add(user)
        db.session.add(task)
        db.session.commit()
        tasks = Task.query.all()
        assert task in tasks
        assert task in db.session
        

    def test_delete_task(self):
        user = User(username="Adam", email="adam.kowalski@mail.com")
        task = Task(title='title', expired_date=datetime.now(), user=user)
        db.session.add(user)
        db.session.add(task)
        db.session.commit()
        task_ = Task.query.get(1)
        db.session.delete(task_)
        db.session.commit()
        tasks = Task.query.all()
        assert task_ not in tasks
        assert task not in db.session


    def test_update_expired_status_long_expired_date(self):
        user = User(username="Adam", email="adam.kowalski@mail.com")
        db.session.add(user)
        db.session.commit()
        task = Task(title='title', expired_date=datetime.now()+timedelta(days=5), user=user)
        db.session.add(task)
        db.session.commit()
        task.update_expired_status(datetime.now())
        assert task.is_expired is False

    
    def test_update_expired_status_short_expired_date(self):
        user = User(username="Adam", email="adam.kowalski@mail.com")
        db.session.add(user)
        db.session.commit()
        task = Task(title='title', expired_date=datetime.now(), user=user)
        db.session.add(task)
        db.session.commit()
        task.update_expired_status(datetime.now())
        assert task.is_expired is True


    def test_send_reminder_email_long_time_left(self):
        user = User(username="Adam", email="adam.kowalski@mail.com")
        db.session.add(user)
        db.session.commit()
        task = Task(title='title', expired_date=datetime.now()+timedelta(days=5), user=user)
        db.session.add(task)
        db.session.commit()
        task.send_reminder_email(user, datetime.now())
        assert task.reminder is True


    def test_send_reminder_email_long_time_left(self):
        user = User(username="Adam", email="adam.kowalski@mail.com")
        db.session.add(user)
        db.session.commit()
        task = Task(title='title', expired_date=datetime.now()+timedelta(days=1), user=user)
        db.session.add(task)
        db.session.commit()
        task.send_reminder_email(user, datetime.now())
        assert task.reminder is False


if __name__ == '__main__':
    unittest.main()