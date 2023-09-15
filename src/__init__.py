from flask import Flask, config, redirect
from flask.json import jsonify
import os

from flask_jwt_extended import JWTManager
from flask_cors import CORS
from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK
from flask_executor import Executor

from src.restapi import api

executor = None

def create_app(test_config=None):
    app = Flask(__name__, 
                instance_relative_config=True)
    global executor
    executor = Executor(app)

    CORS(app, resources={r"*": {"origins": "*"}})
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DB_URI'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),
            MAIL_SERVER=os.environ.get('MAIL_SERVER'),
            MAIL_PORT=os.environ.get('MAIL_PORT'),
            MAIL_USE_SSL=True,
            MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
            MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
        )
    else:
        app.config.from_mapping(test_config)
    

    JWTManager(app)

    app.register_blueprint(api)


    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR

    @app.route('/')
    def root():
        return jsonify({'result': 'hello world'}), HTTP_200_OK

    return app
