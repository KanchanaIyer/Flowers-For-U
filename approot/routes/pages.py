from functools import wraps

from flask import Blueprint, render_template, request, url_for, redirect, session

from approot.sessions import create_session, get_session, delete_session
from approot.data_managers.user_manager import UserManager

webpages = Blueprint('webpages', __name__, template_folder='../webroot/templates', static_folder='../webroot/static')


def reguire_login(f):
    @wraps(f)
    def func(*args, **kwargs):
        print(f"Sesssion: {session}")
        if get_session().get('user'):
            print(get_session().get('user'))
            return f(*args, **kwargs)
        else:
            print(request.url)
            return render_template('login.html',
                                   redirect_url=request.url,
                                   error="You must be logged in to view this page!")

    return func


def check_admin(f):
    @wraps(f)
    def func(*args, **kwargs):
        print(f"Sesssion: {session}")
        if get_session().get('admin'):
            print(get_session().get('admin'))
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
        data = dict(request.form.items())

        if not request.args.get('redirect_url') and data.get('redirect_url'):  # If redirect_url is in form data but not in the url use the form data
            redirect_url = data['redirect_url']

        data.pop('redirect_url')
        print(data)
        try:
            user = UserManager.login(**data)
        except Exception as e:
            return render_template('login.html', redirect_url=redirect_url, error=str(e))
        print(user)

        if user:  # Create a session for the user since it exists
            create_session(user)

            # Redirect to the desired page after a successful login
            print("Redirecting to: {}".format(redirect_url))
            print("Session: {}".format(session))

            # Verify the redirect url is valid and points to the same domain to prevent redirecting to any site
            # I can add some explicit exceptions if needed
            if not redirect_url.startswith(request.host_url):
                redirect_url = url_for('webpages.home')

            res = redirect(redirect_url)
            res.set_cookie('key', get_session().get('key'), expires=3600)  #Key expires in an hour
            return res
        else:
            return render_template('login.html', redirect_url=redirect_url, error="Invalid username or password!")
    return render_template('login.html', redirect_url=redirect_url)


@webpages.route('/register/', methods=['GET'])
def register():
    return render_template('register.html')


@webpages.route('/logout/', methods=['GET'])
def logout():
    delete_session()
    return redirect(url_for('webpages.home'))


@webpages.route('/admin/', methods=['GET'])
@reguire_login
@check_admin
def admin():
    # Check is user is logged in
    print(session)
    return render_template('admin.html')


@webpages.route('/admin/products/', methods=['GET'])
@reguire_login
@check_admin
def admin_products():
    # Check is user is logged in
    print(session)
    print(request.cookies)
    return render_template('admin-products.html')
