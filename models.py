"""models.py"""
from datetime import date
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
mail = Mail()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(20))
    # tasks = db.relationshit('Task')
    
    def __repr__(self):
        return "<User(username='%s', email='%s')>" % (self.username, self.email)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    created_date = db.Column(db.Date, default=date.today())
    done_date = db.Column(db.Date)
    expired_date = db.Column(db.DateTime)
    is_done = db.Column(db.Boolean, default=False)
    is_expired = db.Column(db.Boolean, default=False)
    reminder = db.Column(db.Boolean, default=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "<Task(title='%s', created_date='%s', done_date='%s', expired_date='%s')>" % (self.title, self.created_date, self.done_date, self.expired_date)

    def check_expired(self, current_date):
        time_left = self.expired_date.day - current_date.day
        if time_left <= 0 and not self.is_expired:
            self.is_expired = True
            db.session.commit()

    def send_reminder_email(self, user, current_date):
        time_left = self.expired_date.day - current_date.day
        if time_left == 1 and self.reminder:
            subject = "ToDo App Reminder!"
            recipients = [f"{user.email}"]
            body = f"""Hi {user.username}! Just one day left due to expire your task: {self.title}."""
            message = Message(subject=subject, recipients=recipients, body=body)
            mail.send(message)
            self.reminder = False
            db.session.commit()


