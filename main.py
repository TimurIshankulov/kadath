import datetime
import json
import sys
import uuid

from flask import (Flask, Response, flash, redirect, render_template, request,
                   url_for, make_response, session)
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
db_session = DBSession_kadath()


def to_json(data):
    return json.dumps(data) + "\n"


def resp(code, data):
    return Response(
        status=code,
        mimetype="application/json",
        response=to_json(data)
    )


def authenticate_user(user_id):
    auth = Authentication({'auth_key': uuid.uuid1().hex})
    auth.user_id = user_id
    try:
        db_session.add(auth)
        db_session.commit()
        db_session.refresh(auth)
        return auth.to_dict()
    except Exception:
        print(sys.exc_info()[1])
        db_session.rollback()
    finally:
        db_session.close()
    return None


def get_user_id_by_auth_key(auth_key):
    try:
        auth = db_session.query(Authentication).filter_by(auth_key=auth_key).first()
    except Exception:
        print(sys.exc_info()[1])
        db_session.rollback()
    else:
        if auth is not None:
            return auth.user_id
    finally:
        db_session.close()
    return None


@app.route('/')
def index():
    return render_template(home_template, title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_session.query(User).filter_by(email=form.email.data).first()
        if user is None:
            flash('Incorrect credentials', 'danger')
            return redirect(url_for('login'))
        else:
            user_dict = user.to_dict()
            if user_dict['password'] == form.password.data:  # Successful Sign In
                try:
                    auth = db_session.query(Authentication).filter_by(user_id=user_dict['id']).first()
                    if auth is None:
                        auth_dict = authenticate_user(user_dict['id'])
                        if auth_dict is not None:
                            session['auth_key'] = auth_dict['auth_key']
                            return redirect(url_for('kadath'))
                        else:
                            flash('Something goes wrong', 'danger')
                            return redirect(url_for('login'))
                    else:
                        auth_dict = auth.to_dict()
                        if auth_dict['auth_key'] == session.get('auth_key', ''):
                            return redirect(url_for('kadath'))
                        else:
                            db_session.delete(auth)
                            db_session.commit()
                            auth_dict = authenticate_user(user_dict['id'])
                            session['auth_key'] = auth_dict['auth_key']
                            return redirect(url_for('kadath'))
                except Exception:
                    print(sys.exc_info()[1])
                    db_session.rollback()
                finally:
                    db_session.close()
    if request.method == 'GET':
        auth_key = session.get('auth_key', '')
        user_id = get_user_id_by_auth_key(auth_key)
        if user_id:
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
                    user = db_session.query(User).filter_by(email=user_dict['email']).first()
                    if user is None:
                        user = User(user_dict)
                        db_session.add(user)
                        db_session.commit()
                        db_session.refresh(user)
                    else:
                        db_session.close()
                        flash('User already exists', 'danger')
                        return redirect(url_for('signup'))
                except Exception:
                    print(sys.exc_info()[1])
                    db_session.rollback()
                else:
                    flash('Registration successful', 'success')
                    return redirect(url_for('index'))
                finally:
                    db_session.close()
            else:
                flash('Passwords did not match', 'danger')
                return redirect(url_for('signup'))
        else:
            flash('Invalid Registration Secret', 'danger')
            return redirect(url_for('signup'))
    return render_template(signup_template, title='Sign Up', form=form)


@app.route('/logout', methods=['POST'])
def logout():
    auth_key = session.get('auth_key', '')
    user_id = get_user_id_by_auth_key(auth_key)
    if user_id:
        try:
            auth = db_session.query(Authentication).filter_by(user_id=user_id).first()
            db_session.delete(auth)
            db_session.commit()
        except Exception:
            print(sys.exc_info()[1])
            db_session.rollback()
        else:
            session['auth_key'] = ''
            flash('Successfully logged out', 'success')
            return redirect(url_for('index'))
        finally:
            db_session.close()
    else:
        flash('You must be logged in for that action', 'danger')
        return redirect(url_for('login'))


@app.route('/kadath', methods=['GET', 'POST'])
def kadath():
    auth_key = session.get('auth_key', '')
    user_id = get_user_id_by_auth_key(auth_key)
    if user_id:
        return render_template(kadath_template)
    else:
        flash('You must be logged in for that action', 'danger')
        return redirect(url_for('login'))


@app.route('/kadath/notes', methods=['GET'])
def get_notes():
    auth_key = session.get('auth_key', '')
    user_id = get_user_id_by_auth_key(auth_key)
    if user_id:
        notes = db_session.query(KadathNote).filter_by(user_id=user_id).all()
        notes = [note.to_dict() for note in notes]
        return resp(200, notes)
    else:
        flash('You must be logged in for that action', 'danger')
        return redirect(url_for('login'))


@app.route('/kadath/note/<int:note_id>', methods=['GET'])
def get_note(note_id):
    auth_key = session.get('auth_key', '')
    user_id = get_user_id_by_auth_key(auth_key)
    if user_id:
        note = db_session.query(KadathNote).filter_by(user_id=user_id).filter_by(id=note_id).first()
        if note is not None:
            return note.to_dict()
    return {}


@app.route('/kadath/note/delete/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    auth_key = session.get('auth_key', '')
    user_id = get_user_id_by_auth_key(auth_key)
    if user_id:
        try:
            note = db_session.query(KadathNote).filter_by(user_id=user_id).filter_by(id=note_id).first()
            if note is not None:
                db_session.delete(note)
                db_session.commit()
                return resp(200, {'message': f'Note with id {note_id} was successfully deleted.'})
            else:
                return resp(400, {'message': f'Note with id {note_id} was not found.'})
        except Exception:
            print(sys.exc_info()[1])
            db_session.rollback()
        finally:
            db_session.close()
    return resp(400, {'message': f'A problem occured with note id {note_id}.'})


@app.route('/kadath/note/save', methods=['POST'])
def save_note():
    note_dict = request.get_json()
    auth_key = session.get('auth_key', '')
    user_id = get_user_id_by_auth_key(auth_key)
    if user_id:
        try:
            if note_dict.get('id', None) is None:
                note = KadathNote(note_dict)
                note.user_id = user_id
                db_session.add(note)
                db_session.commit()
                db_session.refresh(note)
                note_dict['id'] = note.id
                note_dict['user_id'] = note.user_id
            else:
                note = db_session.query(KadathNote).filter_by(user_id=user_id).filter_by(id=note_dict['id']).first()
                note.title = note_dict['title']
                note.text = note_dict['text']
                note.modified = note_dict['modified']
                db_session.commit()
        except Exception:
            print(sys.exc_info()[1])
            db_session.rollback()
        else:
            return resp(200, note_dict)
        finally:
            db_session.close()
    else:
        flash('You must be logged in for that action', 'danger')
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.debug = True
    app.run()
