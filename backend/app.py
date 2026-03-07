import os
from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore
from flask_cors import CORS
from models import db, User, Role
from config import Config
from flask_restful import Api
from api.resources import UserRegistration, UserLogin

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Allow Vue frontend to communicate with API
    CORS(app)
    api = Api(app)
    api.add_resource(UserRegistration, '/api/register')
    api.add_resource(UserLogin, '/api/login')
    # Initialize Database
    db.init_app(app)

    # Setup Flask-Security-Too
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, user_datastore)

    with app.app_context():
        # 1. Create instance folder if missing
        instance_path = os.path.join(app.config['BASE_DIR'], 'instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
            
        # 2. Programmatically create all database tables
        db.create_all()

        # 3. Create Roles
        if not Role.query.filter_by(name="admin").first():
            user_datastore.create_role(name="admin", description="Admin Role")
        if not Role.query.filter_by(name="company").first():
            user_datastore.create_role(name="company", description="Company Role")
        if not Role.query.filter_by(name="student").first():
            user_datastore.create_role(name="student", description="Student Role")

        # 4. Create Pre-existing Admin (Superuser)
        if not user_datastore.find_user(email="admin@ppa.com"):
            # Note: Flask-Security hashes the password automatically
            user_datastore.create_user(
                email="admin@ppa.com",
                password="admin123",
                roles=["admin"]
            )
        
        db.session.commit()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)