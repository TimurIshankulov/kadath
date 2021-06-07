import datetime
import json
import sys

from flask import (Flask, Response, flash, redirect, render_template, request,
                   url_for)
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import conn_string, flask_secret_key, registration_secret
from forms import LoginForm, SignUpForm
from models.kadath_model import Base, KadathNote, User, Authentication

base_template = 'base.html'
home_template = 'home.html'
login_template = 'login.html'
signup_template = 'signup.html'
kadath_template = 'kadath.html'

app = Flask(__name__)
app.secret_key = flask_secret_key
app.permanent_session_lifetime = datetime.timedelta(days=365)
Bootstrap(app)

engine_kadath = create_engine(conn_string)
Base.metadata.bind = engine_kadath
DBSession_kadath = sessionmaker(bind=engine_kadath)
session = DBSession_kadath()


def to_json(data):
    return json.dumps(data) + "\n"


def resp(code, data):
    return Response(
        status=code,
        mimetype="application/json",
        response=to_json(data)
    )


@app.route('/')
def index():
    return render_template(home_template, title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = session.query(User).filter_by(email=form.email.data).first()
        if user is None:
            flash('Incorrect credentials', 'danger')
            return redirect(url_for('login'))
        else:
            user_dict = user.to_dict()
            if user_dict['password'] == form.password.data:
                flash('Sign in successful', 'success')
                return redirect(url_for('kadath'))
    return render_template(login_template, title='Sign In', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        if form.registration_secret.data == registration_secret:
            if form.repeat_password.data == form.password.data:
                user_dict = {'email': form.email.data,
                             'password': form.password.data,
                             'firstname': form.firstname.data,
                             'lastname': form.lastname.data}
                try:
                    user = session.query(User).filter_by(email=user_dict['email']).first()
                    if user is None:
                        user = User(user_dict)
                        session.add(user)
                        session.commit()
                        session.refresh(user)
                    else:
                        session.close()
                        flash('User already exists', 'danger')
                        return redirect(url_for('signup'))
                except Exception:
                    print(sys.exc_info()[1])
                    session.rollback()
                else:
                    flash('Registration successful', 'success')
                    return redirect(url_for('kadath'))
                finally:
                    session.close()
            else:
                flash('Passwords did not match', 'danger')
                return redirect(url_for('signup'))
        else:
            flash('Invalid Registration Secret', 'danger')
            return redirect(url_for('signup'))
    return render_template(signup_template, title='Sign Up', form=form)


@app.route('/kadath', methods=['GET', 'POST'])
def kadath():
    return render_template(kadath_template)


@app.route('/kadath/notes', methods=['GET'])
def get_notes():
    notes = session.query(KadathNote).all()
    notes = [note.to_dict() for note in notes]
    return resp(200, notes)


@app.route('/kadath/note/<int:note_id>', methods=['GET'])
def get_note(note_id):
    note = session.query(KadathNote).filter_by(id=note_id).first()
    return note.to_dict()


@app.route('/kadath/note/delete/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = session.query(KadathNote).filter_by(id=note_id).first()
    if note is not None:
        session.delete(note)
        session.commit()
    else:
        session.close()
    return resp(200, {'message': f'Note with id {note_id} was successfully deleted.'})


@app.route('/kadath/note/save', methods=['POST'])
def save_note():
    note_dict = request.get_json()
    try:
        if note_dict.get('id', None) is None:
            note = KadathNote(note_dict)
            session.add(note)
            session.commit()
            session.refresh(note)
            note_dict['id'] = note.id
        else:
            note = session.query(KadathNote).filter_by(id=note_dict['id']).first()
            note.title = note_dict['title']
            note.text = note_dict['text']
            note.modified = note_dict['modified']
            session.commit()
    except Exception:
        print(sys.exc_info()[1])
        session.rollback()
    finally:
        session.close()
    return resp(200, note_dict)


if __name__ == "__main__":
    app.debug = True
    app.run()
