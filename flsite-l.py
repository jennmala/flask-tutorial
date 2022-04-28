from flask import Flask, render_template, url_for, flash, request, get_flashed_messages, session, redirect, abort


app=Flask(__name__)
app.config['SECRET_KEY'] = 'jhbdwdaiwjjowfrjwoijfwoiejfwa'

menu= [ {'name': 'install', 'url': 'install-flask'},
    {'name': 'first', 'url': 'first-app'},
    {'name': 'feedback', 'url': 'contact'} ]


@app.route('/index')
@app.route('/')
def index():
    print(url_for('index'))
    return render_template('index.html', menu=menu)

@app.route('/about')
def about():
    print(url_for('about'))
    return render_template('about.html', title='about', menu=menu)

@app.route('/contact', methods=['POST', 'GET'])
def contact(): 
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('sent')
        else:
            flash('error')    
    return render_template('contact.html', title='feedback', menu=menu)

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title='Page not found', menu=menu), 404

@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == 'selfedu' and request.form['psw'] == '123':
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template ('login.html', title='Authorization', menu=menu)

@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'Users profile: {username}' 

if __name__ == '__main__':
    app.run(debug=True)