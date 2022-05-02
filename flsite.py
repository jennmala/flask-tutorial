import sqlite3
import os
from flask import Flask, flash, make_response, render_template, request, g, abort, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

from FDataBase import FDataBase
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm
from admin.admin import admin



# config
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'wyeuwqy72iulf,no,g>dsfhv'
MAX_CONTENT_LENGTH = 1024 *1024

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Login to access this page.'
login_manager.login_message_category = 'success'

@login_manager.user_loader
def load_user(user_id):
    # print('load_user')
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.errorhandler(404)
def pageNot(error):
    return ('Page not found', 404)



@app.route('/')
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostAnonce())



@app.route('/add-post', methods=['POST', 'GET'])    
def addPost():    
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('adding article error')
            else: 
                flash('article added successfully')
        else:
            flash('adding article error')

    return render_template('add_post.html', menu=dbase.getMenu(), title='adding an article')



@app.route('/post/<alias>')
@login_required
def showPost(alias):    
    title, post = dbase.getPost(alias)
    if not post:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post) 



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            user = dbase.getUserByEmail(form.email.data)
            if user and check_password_hash(user['psw'], form.psw.data):
                userLogin = UserLogin().create(user)
                rm = form.remember.data
                login_user(userLogin, remember=rm)
                return redirect(request.args.get('next') or url_for('profile'))
            flash('login/passwors are not correct', 'error')
        
    return render_template('login.html', menu=dbase.getMenu(), title='Authorization', form=form)

   

@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegisterForm()
    if form.validate_on_submit():

    # if request.method == 'POST':
        # if len(request.form['name']) > 4 and len(request.form['email']) >4 \
        #     and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(form.psw.data)
            res = dbase.addUser(form.name.data, form.email.data, hash)
            if res:
                flash('You registered successfully', 'success')
                return redirect(url_for('login'))
            else:
                flash('DB adding error', 'error') 
        # else:
        #     flash('Fields are fulfilled incorrect')
    return render_template('register.html', menu=dbase.getMenu(), title='Registration', form=form) 



@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', menu=dbase.getMenu(), title='Profile')



@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ''
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h



@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash('Update avatar error', 'error')
                flash('Avatar updated', 'success')
            except FileNotFoundError as e:
                flash('File reading error', 'error')
        else:
            flash('Update avatar error', 'error')
    return redirect(url_for('profile'))     



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out successfully', 'success')
    return redirect(url_for('login'))


# @app.route('/login-test')
# def logintest():    
#     log= ''
#     if request.cookies.get('logged'):
#         log = request.cookies.get('logged')
#     res = make_response(f'<h1>Authorization form</h1><p>logged: {log} </p>')
#     res.set_cookie('logged', 'yes', 30*24*3600)    
#     return res

# @app.route('/logout-test')
# def logouttest():        
#     res = make_response(f'<p>You are no longer loged in</p>')
#     res.set_cookie('logged', '', 0)    
#     return res


if __name__ == '__main__':
    app.run(debug=True)
