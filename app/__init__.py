from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__,static_url_path="/static", static_folder='/home/itsuprun/IASA/Web/test_flask/course_work/app/templates/static')
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)
#app.config['SECRET_KEY'] = 'you-will-never-guess'
# ... add more variables here as needed
from app import routes, models
