from flask import Blueprint, render_template

webpages = Blueprint('webpages', __name__, template_folder='../webroot/templates', static_folder='../webroot/static')


@webpages.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@webpages.route('/flowers/', methods=['GET'])
def flowers():
    return render_template('flowers.html')
