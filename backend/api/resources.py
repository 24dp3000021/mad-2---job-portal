from flask_restful import Resource, reqparse
from flask_security import hash_password, verify_password
from models import db, User, Role, StudentProfile, CompanyProfile
import uuid

# --- REGISTRATION ---
reg_parser = reqparse.RequestParser()
reg_parser.add_argument('email', type=str, required=True)
reg_parser.add_argument('password', type=str, required=True)
reg_parser.add_argument('role', type=str, required=True) # 'student' or 'company'
reg_parser.add_argument('name', type=str, required=True) # Full Name or Company Name

class UserRegistration(Resource):
    def post(self):
        args = reg_parser.parse_args()
        if User.query.filter_by(email=args['email']).first():
            return {"message": "User already exists"}, 400

        role = Role.query.filter_by(name=args['role']).first()
        new_user = User(
            email=args['email'],
            password=hash_password(args['password']),
            active=True,
            fs_uniquifier=str(uuid.uuid4())
        )
        new_user.roles.append(role)
        db.session.add(new_user)
        db.session.flush()

        if args['role'] == 'student':
            db.session.add(StudentProfile(user_id=new_user.id, full_name=args['name']))
        else:
            db.session.add(CompanyProfile(user_id=new_user.id, name=args['name']))

        db.session.commit()
        return {"message": "Success"}, 201

# --- LOGIN ---
login_parser = reqparse.RequestParser()
login_parser.add_argument('email', type=str, required=True)
login_parser.add_argument('password', type=str, required=True)

class UserLogin(Resource):
    def post(self):
        args = login_parser.parse_args()
        user = User.query.filter_by(email=args['email']).first()
        if user and verify_password(args['password'], user.password):
            return {
                "token": user.get_auth_token(),
                "role": user.roles[0].name,
                "id": user.id,
                "message": "Logged in"
            }, 200
        return {"message": "Invalid credentials"}, 401