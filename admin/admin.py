import sqlite3
from flask import Blueprint, render_template, request, redirect, session, url_for, flash, render_template, url_for, session, g

from FDataBase import FDataBase


admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')



def login_admin():
    session['admin_logged'] = 1

def isLogged():
    return True if session.get('admin_logged') else False

def logout_admin():
    session.pop('admin_logged', None)


menu = [
    { 'url': '.index', 'title': 'Panel'},
    { 'url': '.listpubs', 'title': 'Articles list'},
    { 'url': '.listusers', 'title': 'Users list'},
    { 'url': '.logout', 'title': 'Logout'},
]


db = None
@admin.before_request
def before_request():
    global db
    db = g.get('link_db')

@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request



@admin.route('/')
def index():
    if not isLogged():
        return redirect(url_for('.login'))
    return render_template('admin/index.html', menu=menu, title='Admin Panel')


@admin.route('/login', methods=['POST', 'GET'])
def login():
    if isLogged():
        return redirect(url_for('.index'))

    if request.method == 'POST':
        if request.form['user'] == 'admin' and request.form['psw'] == '12345':
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash('login/passwors are not correct', 'error')
    return render_template('admin/login.html', title='Admin Panel')


@admin.route('/logout', methods=['POST', 'GET'])
def logout():
    
    if not isLogged():
        return redirect(url_for('.login'))
    logout_admin()
    return redirect(url_for('.login')) 

@admin.route('/list-pubs', methods=['POST', 'GET'])
def listpubs():    
    if not isLogged():
        return redirect(url_for('.login'))
    
    list = []    
    if db:
        try:
            cur = db.cursor()            
            cur.execute(f'SELECT title, text, url FROM posts')
            list = cur.fetchall()
        except sqlite3.Error as e:
            print('DB getting article error ' +str(e))
    return render_template('admin/listpubs.html', title='Articles list', menu=menu, list=list)

     
@admin.route('/list-users', methods=['POST', 'GET'])
def listusers():    
    if not isLogged():
        return redirect(url_for('.login'))
    
    list = []    
    if db:
        try:
            cur = db.cursor()            
            cur.execute(f'SELECT name, email FROM users ORDER BY time DESC')
            list = cur.fetchall()            
        except sqlite3.Error as e:
            print('DB getting users error ' +str(e))
    return render_template('admin/listusers.html', title='Users list', menu=menu, list=list)