from email.policy import default
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists
from flask_migrate import Migrate
import os


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'todos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    titles = db.relationship('Todo', backref='user')


@app.route("/add", methods=["POST"])
def add():

    if request.is_json:
        data = request.get_json()
        todo = Todo(title=data.get('title'), completed=data.get(
            'completed'), user_id=data.get('user_id'))
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for("home"))

    title = request.form.get("title")
    todo = Todo(title=title, completed=False, user_id=0)
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/update/<int:todo_id>')
def update(todo_id: int):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete/<int:todo_id>')
def delete(todo_id: int):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/')
def home():
    todo_list = Todo.query.all()
    with open('tmp.txt', 'w') as f:
        f.write(str(len(todo_list)))
    return render_template('base.html', todo_list=todo_list)


if __name__ == '__main__':
    if not database_exists(app.config.get('SQLALCHEMY_DATABASE_URI')):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
