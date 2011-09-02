import user
import util

import sha, time

import flask
from flask import request, make_response, session, redirect
import decorator

app = flask.Flask('Football Pool Webserver')
app.secret_key = '# set the secret key.  keep this really secret:'

def do_login(requested_user, web_email, web_password):
    if not requested_user:
        return False

    if requested_user.password_hash != sha.sha(web_password).hexdigest():
        return False

    session['email'] = web_email
    return True


def _logged_in():
    if 'email' not in session:
        return None

    email = session['email']
    return user.User.from_email(email)


@decorator.decorator
def login_required(func, *args, **kwargs):
    """Require a logged in user."""
    user_obj = _logged_in()
    if not user_obj:
        return redirect("/login")

    flask.g.user_obj = user_obj
    return func(*args, **kwargs)


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('images/favicon.ico')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        requested_user = user.User.from_email(email)

        if do_login(requested_user, email, password):
            return redirect('/homepage')
        else:
            return flask.render_template('login.html', error_msg='Could not login as %s' % (email))

    return flask.render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('email', None)
    return redirect('/login')


@app.route('/homepage')
@login_required
def homepage():
    user_obj = flask.g.user_obj
    return flask.render_template('homepage.html', username=user_obj.name, week=util.get_week())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirmation = request.form['confirmation_password']
        league_password = request.form['league_password']

        if password != confirmation:
            return flask.render_template('register.html', error_msg='Your password did not match the confirmation')

        if league_password != settings.league_password:
            return flask.render_template('register.html', error_msg='Bad league password')

        db.new_user(email, sha.sha(password).hexdigest(), email)
        if db.num_users() == 1:
            fiesta.create_group(settings.list_name)

        
    return flask.render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
