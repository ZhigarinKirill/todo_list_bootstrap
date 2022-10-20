from datetime import datetime
from turtle import title
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import LoginForm
from sqlalchemy_utils import database_exists
import os
from werkzeug.security import generate_password_hash,  check_password_hash


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))


app.config['SECRET_KEY'] = '7d8e1dca329fbf2dd56eeb68d77a684aaa05e2a3a147cd5a31c989bd80905f5981a009c85da3a35ac1369106d33d785f0d2ac8fce8c91a7d782a668eba319d57'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'flask_todo_list')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# manager = Manager(app)
# manager.add_command('db', MigrateCommand)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class Todo(db.Model):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<{self.id}:{self.completed}>'


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(
        db.DateTime(), default=datetime.utcnow,  onupdate=datetime.utcnow)

    titles = db.relationship('Todo', backref='users')

    def __repr__(self):
        return f'<{self.id}:{self.name}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,  password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


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
    return redirect(url_for("todo_list"))


@app.route('/update/<int:todo_id>')
def update(todo_id: int):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for('todo_list'))


@app.route('/delete/<int:todo_id>')
def delete(todo_id: int):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('todo_list'))


@app.route('/todo_list')
def todo_list():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    todo_list = Todo.query.all()
    with open('tmp.txt', 'w') as f:
        f.write(str(len(todo_list)))
    return render_template('todo_list.html', todo_list=todo_list, title='Todo List')


@app.route('/admin/')
@login_required
def admin():
    return render_template('admin.html', title='AdminPanel')


@app.route('/')
def home():
    return render_template('home.html', title='Home')


@app.route('/login/', methods=['POST',  'GET'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('admin'))
    # form = LoginForm()
    form = LoginForm(request.form)
    if form.validate_on_submit():

        user = db.session.query(User).filter(
            User.name == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('todo_list'))

        return redirect(url_for('login'))

    return render_template('login.html', form=form, title='Login')


if __name__ == '__main__':
    # if not database_exists(app.config.get('SQLALCHEMY_DATABASE_URI')):
    #     with app.app_context():
    #         db.create_all()
    app.run(debug=True)
