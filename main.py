from flask import Flask, render_template, request, make_response, session, flash, redirect, url_for
from flask_bootstrap import Bootstrap
import datetime
import os
from shutil import copyfile
import config
from forms import LoginForm

base_template = 'base.html'
login_template = 'login.html'
kadath_template = 'kadath.html'

app = Flask(__name__)
app.secret_key = config.flask_secret_key
app.permanent_session_lifetime = datetime.timedelta(days=365)
Bootstrap(app)


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

if __name__ == "__main__":
    app.debug = True
    app.run()