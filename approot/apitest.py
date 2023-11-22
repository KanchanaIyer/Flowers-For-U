from functools import wraps

from flask import Flask, render_template, request, Blueprint
from flask_cors import CORS
from config import get_flask_config

from pages import webpages
from product_api import product_api as p_api


flask_config = get_flask_config()
app = Flask(__name__,
            static_url_path='',
            static_folder='../webroot/static',
            template_folder='../webroot/templates')

app.register_blueprint(webpages)
app.register_blueprint(p_api)

CORS(app, supports_credentials=True) # Allow cross-origin requests
if __name__ == '__main__':
    app.run(debug=flask_config['debug'] == "ENABLED", host=flask_config['host'], port=flask_config['port'])
