"""app.py"""
import os
from datetime import date, datetime, timedelta
from flask import Flask, render_template, redirect, request, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+DATABASE_DIR
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = os.environ.get('DEV_EMAIL_USER')
app.config["MAIL_PASSWORD"] = os.environ.get('DEV_EMAIL_PASSWORD')
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get('DEV_EMAIL_USER')

db = SQLAlchemy(app)
mail = Mail(app)


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

db.create_all()

def update_tasks(task_object, user, current_date):
    tasks = task_object.query.all()
    for task in tasks:
        send_reminder_email(task, user, current_date)
        check_expired(task, current_date)


def check_expired(task, current_date):
    time_left = task.expired_date.day - current_date.day
    if time_left <= 0 and not task.is_expired:
        task.is_expired = True
        db.session.commit()


def send_reminder_email(task, user, current_date):
    time_left = task.expired_date.day - current_date.day
    if time_left == 1 and task.reminder:
        subject = "ToDo App Reminder!"
        recipients = [f"{user.email}"]
        body = f"""Hi {user.username}! Just one day left due to expire your task: {task.title}."""
        message = Message(subject=subject, recipients=recipients, body=body)
        mail.send(message)
        task.reminder = False
        db.session.commit()


@app.route('/config')
def config():
    user = User.query.get(1)
    return render_template('config.html', user=user)

@app.route('/config/edit', methods=['POST'])
def edit():
    username = request.form['username']
    email = request.form['email']
    user = User.query.get(1)

    if not user:
        user = User(username=username, email=email)
        db.session.add(user)
    else:
        user.username = username
        user.email = email
        
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/')
def index():
    user = User.query.get(1)

    if not user:
        return redirect(url_for('config'))
    else:
        current_date = datetime.now() #+ timedelta(days=2)
        update_tasks(Task, user, current_date)
        completed_tasks = Task.query.filter_by(is_done=True)
        incompleted_tasks = Task.query.filter_by(is_done=False)
        return render_template('index.html', completed_tasks=completed_tasks, incompleted_tasks=incompleted_tasks, current_date=current_date, user=user)

@app.route('/add', methods=['POST'])
def add():
    title = request.form['task']
    days = int(request.form['days'])
    task = Task(title=title, expired_date=datetime.now()+timedelta(days=days))
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<id>')
def delete(id):
    task = Task.query.filter_by(id=int(id)).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/done/<id>')
def done(id):
    task = Task.query.filter_by(id=int(id)).first()
    task.done_date = date.today()
    task.is_done = True
    task.reminder = False
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/undone/<id>')
def undone(id):
    task = Task.query.filter_by(id=int(id)).first()
    task.done_date = None
    task.is_done = False
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
    