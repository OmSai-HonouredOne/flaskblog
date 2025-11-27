import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import query_all, query_one, execute


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif query_one(
            'SELECT id FROM "user" WHERE username = %s', (username,)
        ) is not None:
            error = f"User {username} is already registered."

        if error is None:
            execute(
                'INSERT INTO "user" (username, password) VALUES (%s, %s)',
                (username, generate_password_hash(password))
            )
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = query_one(
            'SELECT * FROM "user" WHERE username = %s', (username,)
        )

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = query_one(
            'SELECT * FROM "user" WHERE id = %s', (user_id,)
        )


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/profile')
@login_required
def profile():
    mypost = query_all(
        'SELECT * FROM post WHERE author_id = %s ORDER BY created DESC', (g.user['id'],)
    )
    return render_template('auth/profile.html', user=g.user, mypost=mypost)