from functools import wraps

from flask import Blueprint, render_template, request, url_for, redirect, session

from approot.sessions import create_session, get_session
from approot.data_managers.user_manager import UserManager

webpages = Blueprint('webpages', __name__, template_folder='../webroot/templates', static_folder='../webroot/static')


def check_admin(f):
    @wraps(f)
    def func(*args, **kwargs):
        if session.get('admin'):
            return f(*args, **kwargs)
        else:
            return render_template('401.html', error="You are not an admin!")

    return func


@webpages.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@webpages.route('/flowers/', methods=['GET'])
def flowers():
    return render_template('flowers.html')


@webpages.route('/login/', methods=['GET', 'POST'])
def login():
    redirect_url = request.args.get('redirect_url', url_for('webpages.home'))  # Default to homepage

    if request.method == 'POST':
        # Handle login logic
        data = dict(request.form.items())  # Assuming form fields match the expected data for login
        print(data)
        (resp, status), user = UserManager.login(**data)
        print(user, status)
        if user and status == 200:
            create_session(user['user_id'])
            session['key'] = get_session()['key']
            session['admin'] = user['is_admin']
            session['user'] = user['username']

            # Redirect to the desired page after a successful login
            print("Redirecting to: {}".format(redirect_url))
            print("Session: {}".format(session))
            res = redirect(redirect_url)
            res.set_cookie('key', session['key'])
            return res
        else:
            return render_template('login.html', redirect_url=redirect_url, error=resp.json['message'])
    return render_template('login.html', redirect_url=redirect_url)


@webpages.route('/register/', methods=['GET'])
def register():
    return render_template('register.html')

@check_admin
@webpages.route('/admin/', methods=['GET'])
def admin():
    # Check is user is logged in
    print(session)
    return render_template('admin.html')

@check_admin
@webpages.route('/admin/products/', methods=['GET'])
def admin_products():
    # Check is user is logged in
    print(session)
    print(request.cookies)
    return render_template('admin-products.html')
