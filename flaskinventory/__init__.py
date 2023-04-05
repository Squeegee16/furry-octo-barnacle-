from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from os import path
from flaskinventory.config import Config

db = SQLAlchemy()
mail = Mail()


def garden_app(config_class=Config):
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    mail.init_app(app)


    from flaskinventory.errors.handlers import errors
    from flaskinventory.main.main import main

    app.register_blueprint(errors)#, url_prefix='/')
    app.register_blueprint(main)#, url_prefix='/')

    from flaskinventory.models import Location, Product, Movement, Balance
    create_database(app)

    return app

def create_database(app):
    if not path.exists('flaskinventory/' + 'site.db'):
        db.create_all(app=app)
        print('Created Database!')
    if not path.exists('flaskinventory/' + 'old.db'):
        db.create_all(app=app)
        print('Created Archive Database!')


