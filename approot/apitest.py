import logging
import sys

from flask import Flask
from flask_cors import CORS
from approot.database.database import init_app

from approot.routes.pages import webpages
from approot.routes.product_api import product_api as p_api
from approot.routes.user_api import user_api as u_api

# Add config to the app
sys.path.append('../')

from config.config import get_flask_config
flask_config = get_flask_config()
app = Flask(__name__,
            static_url_path='',
            static_folder='../webroot/static',
            template_folder='../webroot/templates')
app.config['SECRET_KEY'] = flask_config['secretKey']
app.config['max_content_length'] = int(flask_config['maxContentLength'])
app.permanent_session_lifetime = int(flask_config['sessionLifetime'])


app.register_blueprint(webpages)
app.register_blueprint(p_api)
app.register_blueprint(u_api)
init_app(app)

CORS(app, supports_credentials=True)  # Allow cross-origin requests
if __name__ == '__main__':
    # This is all testing configuration. This is not used in production.
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=flask_config['debug'] == "ENABLED", host=flask_config['host'], port=flask_config['port'])
