"""models.py"""
from datetime import date, datetime
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
mail = Mail()


class User(db.Model):
    """ Database 'users' table model class. """ 

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(20))


    def __repr__(self) -> str:
        return f"<User(username={self.username}, email={self.email})>"


class Task(db.Model):
    """ Database 'tasks' table model class. """ 

    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    created_date = db.Column(db.Date, default=date.today())
    done_date = db.Column(db.Date)
    expired_date = db.Column(db.DateTime)
    is_done = db.Column(db.Boolean, default=False)
    is_expired = db.Column(db.Boolean, default=False)
    reminder = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('tasks'))
  

    def __repr__(self):
        return f"<Task(title={self.title}, created_date={self.created_date}, done_date={self.done_date}, expired_date={self.expired_date})>"

  
    def update_expired_status(self, current_date: datetime) -> None:
        """ Function which updates expited status, when difference
        between expired date and current date is less or equal 0. """
        time_left = self.expired_date.day - current_date.day
        if time_left <= 0 and not self.is_expired:
            self.is_expired = True
            db.session.commit()


    def send_reminder_email(self, user: User, current_date: datetime) -> None:
        """ Function which sends reminder email and updates 
        task in database. """
        time_left = self.expired_date.day - current_date.day
        if time_left == 1 and self.reminder:
            subject = "ToDo App Reminder!"
            recipients = [f"{user.email}"]
            body = f"""Hi {user.username}! Just one day left due to expire your task: {self.title}."""
            message = Message(subject=subject, recipients=recipients, body=body)
            mail.send(message)
            self.reminder = False
            db.session.commit()


