import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from db import dbUtil

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=('POST'))
def login():
    username = request.form['username']
    password = request.form['password']

    dbUtil = dbUtil.get_db()
    error = None
    user = dbUtil.execute('select * from user where username=?',(username,)).fetchone()
    if user is None or not check_password_hash(user['password'], password):
        error = 'Incorrect username or password'
    if error is None:
        session.clear()
        session['user_id'] = user['id']
        return redirect(url_for('index'))
    flash(error)
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth/login.html'))

'''
在每个访问前都进行一次检查
'''
@auth_bp.before_app_request
def check_user():
    user_id = session.get('user_id')
    if user_id is None:
        print('Null user')
    else:
        print('User:'+user_id)

'''
创建登陆检查装饰器
'''
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view