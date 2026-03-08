import os
from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore
from flask_cors import CORS
from flask_restful import Api

# 1. ADD THE MISSING IMPORTS HERE
from models import db, User, Role
from config import Config
from api.resources import (UserRegistration, UserLogin, AdminDashboardStats, 
                           AdminManagement, CompanyDriveResource, 
                           DriveApplicationsResource, ApplicationStatusResource,
                           StudentDriveResource, StudentProfileAction, StudentApplyResource,  StudentCompanyList)
def create_app():
    
    app = Flask(__name__)
    app.config.from_object(Config)

    # Allow Vue frontend to communicate with API
    CORS(app)
    
    # 2. SETUP API ROUTES
    api = Api(app)
# auth routes
    api.add_resource(UserRegistration, '/api/register')
    api.add_resource(UserLogin, '/api/login')
    # admin routes
    api.add_resource(AdminDashboardStats, '/api/admin/stats')
    api.add_resource(AdminManagement, '/api/admin/manage/<string:target>')
# company routes
    api.add_resource(CompanyDriveResource, '/api/company/drives/<int:company_user_id>')
    api.add_resource(DriveApplicationsResource, '/api/drive/<int:drive_id>/applications')
    api.add_resource(ApplicationStatusResource, '/api/application/status')
# student routes
    api.add_resource(StudentDriveResource, '/api/student/drives')
    api.add_resource(StudentProfileAction, '/api/student/profile/<int:user_id>')
    api.add_resource(StudentApplyResource, '/api/student/apply', '/api/student/history/<int:user_id>')
    api.add_resource(StudentCompanyList, '/api/student/companies') 
    # Initialize Database
    db.init_app(app)

    # Setup Flask-Security-Too
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, user_datastore)

    with app.app_context():
        instance_path = os.path.join(app.config['BASE_DIR'], 'instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
            
        db.create_all()

        if not Role.query.filter_by(name="admin").first():
            user_datastore.create_role(name="admin", description="Admin Role")
        if not Role.query.filter_by(name="company").first():
            user_datastore.create_role(name="company", description="Company Role")
        if not Role.query.filter_by(name="student").first():
            user_datastore.create_role(name="student", description="Student Role")

        if not user_datastore.find_user(email="admin@ppa.com"):
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