import datetime
import json
import os
from shutil import copyfile

from flask import (Flask, Response, flash, make_response, redirect,
                   render_template, request, session, url_for)
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import conn_string, flask_secret_key
from forms import LoginForm
from models.kadath_model import Base, KadathNote

base_template = 'base.html'
login_template = 'login.html'
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
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'test' and form.password.data == 'test':
            flash('Выполнен вход пользователя test', 'success')
            return redirect(url_for('kadath'))
        else:
            flash('Неверное имя пользователя и пароль', 'danger')
            return redirect(url_for('login'))
    return render_template(login_template, title='Sign In', form=form)


@app.route('/kadath', methods=['GET', 'POST'])
def kadath():
    return render_template(kadath_template)


@app.route('/kadath/notes', methods=['GET'])
def get_notes():
    notes = session.query(KadathNote).all()
    return resp(200, notes)


@app.route('/kadath/note/<int:note_id>', methods=['GET'])
def get_note(note_id):
    note = session.query(KadathNote).filter_by(id=note_id).first()
    return note


@app.route('/kadath/note/save', methods=['POST'])
def save_note():
    note_dict = {}
    #note_dict['id'] = request.args.get('note_id')
    note_dict['title'] = request.args.get('title')
    note_dict['text'] = request.args.get('text')
    try:
        note = KadathNote(note_dict)
        session.add(note)
        session.commit()
    except Exception:
        session.rollback()
    return resp(200, note_dict)


if __name__ == "__main__":
    app.debug = True
    app.run()
