"""app.py"""
import os
from datetime import date, datetime, timedelta
from flask import Flask, render_template, redirect, request, url_for
from flask_mail import Mail, Message
from models import db, mail, User, Task

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database.db")

def create_app():

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

    db.init_app(app)
    mail.init_app(app)

    return app

app = create_app()

def update_tasks(task_object, user, current_date):
    tasks = task_object.query.all()
    for task in tasks:
        task.send_reminder_email(user, current_date)
        task.check_expired(current_date)

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
    
    with app.app_context():
        db.create_all()
    app.run(debug=True)

    