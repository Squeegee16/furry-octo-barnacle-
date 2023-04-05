import os

class Config:
    SECRET_KEY = '323b22caac41acbf'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///site.db'
    # second database
    SQLALCHEMY_BINDS ={
    'old' :'sqlite:///old.db'
    }
    SQLAlCHEMY_ECHO = True
    DEBUG = True
    FLASK_DEBUG=1
    FLASK_ENV='development'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


    # SECRET_KEY = os.environ.get('SECRET_KEY')
    # SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    # MAIL_SERVER = 'smtp.googlemail.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get('EMAIL_USER')
    # MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    # MAIL_USERNAME='radarerik@gmail.com'
    # MAIL_PASSWORD='U1trasonic23!'
    # https://flask-appbuilder.readthedocs.io/en/latest/multipledbs.html