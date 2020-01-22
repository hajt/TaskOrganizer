"""app.py"""
import os
from datetime import date, timedelta
from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+DATABASE_DIR
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    created_date = db.Column(db.Date, default=date.today())
    expired_date = db.Column(db.Date, default=date.today()+timedelta(days=1))
    is_done = db.Column(db.Boolean, default=False)
    is_expired = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<Task(title='%s', created_date='%s', expired_date='%s')>" % (self.title, self.created_date, self.expired_date)

db.create_all()

def update_tasks(task_object, current_date):
    tasks = task_object.query.all()
    for task in tasks:
        check_expired(task, current_date)

def check_expired(task, current_date):
    time_left = task.expired_date.day - current_date.day
    if time_left < 0 and not task.is_expired:
        task.is_expired = True
        db.session.commit()

@app.route('/')
def index():
    current_date = date.today() # + timedelta(days=2)
    update_tasks(Task, current_date)
    # tasks = Task.query.all()
    completed_tasks = Task.query.filter_by(is_done=True)
    incompleted_tasks = Task.query.filter_by(is_done=False)
    return render_template('index.html', completed_tasks=completed_tasks, incompleted_tasks=incompleted_tasks, current_date=current_date)

@app.route('/add', methods=['POST'])
def add():
    title = request.form['task']
    task = Task(title=title)
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
    task.is_done = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/undone/<id>')
def undone(id):
    task = Task.query.filter_by(id=int(id)).first()
    task.is_done = False
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
    