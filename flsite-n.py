import datetime
from flask import Flask, make_response, render_template, session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'f5cd037d5b9f0a1b37dd67e37b3a62742445525f'
app.permanent_session_lifetime = datetime.timedelta(days=10)


@app.route('/')
def index():
    if 'visits' in session:
        session['visits'] = session.get('visits') + 1
    else:
        session['visits'] = 1
    return f"<h1>Main page</h1><p>Views quantity: {session['visits']}</p>"


data = [1,2,3,4]
@app.route('/session')
def session_data():
    # session.permanent = True
    # session.permanent = False // not save session
    if 'data' not in session:
        session['data'] = data
    else:
        session['data'][1] += 1
        session.modified = True
    return f"<p>Session data: {session['data']}</p>"


if __name__ == '__main__':
    app.run(debug=True)