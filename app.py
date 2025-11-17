from flask import Flask, render_template
from models import db, Department, Officer, Request, PoliceStation, FireStation, EmergencyRequest, Hospital, Infrastructure
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin

app = Flask(__name__)
app.secret_key = "dev_secret_key"

import os

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:harikam%402007@localhost/smartcity_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db, migrate, bcrypt, login manager


db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'authority_bp.login'

from models import Officer

@login_manager.user_loader
def load_user(user_id):
    return Officer.query.get(int(user_id))

from citizen import citizen_bp
from authority import authority_bp
# Register blueprints
app.register_blueprint(citizen_bp)
app.register_blueprint(authority_bp, url_prefix='/authority')

# Home page route
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
