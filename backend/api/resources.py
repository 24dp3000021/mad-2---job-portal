from flask_restful import Resource, reqparse
from flask_security import hash_password, verify_password
from models import db, User, Role, StudentProfile, CompanyProfile, PlacementDrive, Application
from datetime import datetime
import uuid

# --- PARSERS ---

reg_parser = reqparse.RequestParser()
reg_parser.add_argument('email', type=str, required=True)
reg_parser.add_argument('password', type=str, required=True)
reg_parser.add_argument('role', type=str, required=True)
reg_parser.add_argument('name', type=str, required=True)

login_parser = reqparse.RequestParser()
login_parser.add_argument('email', type=str, required=True)
login_parser.add_argument('password', type=str, required=True)

# --- AUTH ---

class UserRegistration(Resource):
    def post(self):
        args = reg_parser.parse_args()
        if User.query.filter_by(email=args['email']).first():
            return {"message": "User already exists"}, 400
        role = Role.query.filter_by(name=args['role']).first()
        new_user = User(email=args['email'], password=hash_password(args['password']), active=True, fs_uniquifier=str(uuid.uuid4()))
        new_user.roles.append(role)
        db.session.add(new_user)
        db.session.flush()
        if args['role'] == 'student':
            db.session.add(StudentProfile(user_id=new_user.id, full_name=args['name'], cgpa=0.0))
        else:
            db.session.add(CompanyProfile(user_id=new_user.id, name=args['name']))
        db.session.commit()
        return {"message": "Success"}, 201

class UserLogin(Resource):
    def post(self):
        args = login_parser.parse_args()
        user = User.query.filter_by(email=args['email']).first()
        if user and verify_password(args['password'], user.password):
            return {
                "token": user.get_auth_token(),
                "role": user.roles[0].name,
                "id": user.id,
                "name": user.student_profile.full_name if user.student_profile else user.company_profile.name if user.company_profile else "Admin"
            }, 200
        return {"message": "Invalid credentials"}, 401

# --- ADMIN ---

class AdminDashboardStats(Resource):
    def get(self):
        return {
            "total_students": StudentProfile.query.count(),
            "total_companies": CompanyProfile.query.count(),
            "total_drives": PlacementDrive.query.count(),
            "pending_companies": CompanyProfile.query.filter_by(is_approved=False).count(),
            "pending_drives": PlacementDrive.query.filter_by(status='Pending').count()
        }, 200

class AdminManagement(Resource):
    def get(self, target):
        if target == 'companies':
            items = CompanyProfile.query.all()
            return[{"id": i.id, "name": i.name, "is_approved": i.is_approved, "is_blacklisted": i.is_blacklisted, "email": i.user.email} for i in items], 200
        elif target == 'students':
            items = StudentProfile.query.all()
            return[{"id": i.id, "name": i.full_name, "cgpa": i.cgpa, "is_blacklisted": i.is_blacklisted, "email": i.user.email} for i in items], 200
        elif target == 'drives':
            items = PlacementDrive.query.all()
            return[{"id": i.id, "company": i.company.name, "title": i.job_title, "status": i.status} for i in items], 200

    def post(self, target):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        parser.add_argument('action', type=str, required=True)
        args = parser.parse_args()
        obj = None
        if target == 'companies':
            obj = CompanyProfile.query.get(args['id'])
            if args['action'] == 'approve': obj.is_approved = True
            elif args['action'] == 'blacklist': obj.is_blacklisted = not obj.is_blacklisted
        elif target == 'drives':
            obj = PlacementDrive.query.get(args['id'])
            if args['action'] == 'approve': obj.status = 'Approved'
            elif args['action'] == 'reject': obj.status = 'Rejected'
        elif target == 'students':
            obj = StudentProfile.query.get(args['id'])
            if args['action'] == 'blacklist': obj.is_blacklisted = not obj.is_blacklisted
        db.session.commit()
        return {"message": "Action successful"}, 200

# --- COMPANY ---

class CompanyDriveResource(Resource):
    def get(self, company_user_id):
        company = CompanyProfile.query.filter_by(user_id=company_user_id).first()
        if not company: return {"message": "Company not found"}, 404
        drives = PlacementDrive.query.filter_by(company_id=company.id).all()
        return[{
            "id": d.id,
            "title": d.job_title,
            "status": d.status,
            "deadline": str(d.deadline.date()),
            "min_cgpa": d.min_cgpa,
            "salary": d.salary,
            "location": d.location
        } for d in drives], 200

    def post(self, company_user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('job_title', type=str, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('min_cgpa', type=float, required=True)
        parser.add_argument('salary', type=str)
        parser.add_argument('location', type=str)
        parser.add_argument('deadline', type=str, required=True)
        args = parser.parse_args()

        company = CompanyProfile.query.filter_by(user_id=company_user_id).first()
        if not company.is_approved:
            return {"message": "Account pending admin approval"}, 403

        new_drive = PlacementDrive(
            company_id=company.id,
            job_title=args['job_title'],
            description=args['description'],
            salary=args.get('salary', 'Not Mentioned'),
            location=args.get('location', 'Remote'),
            min_cgpa=args['min_cgpa'],
            deadline=datetime.strptime(args['deadline'], '%Y-%m-%d'),
            status='Pending'
        )
        db.session.add(new_drive)
        db.session.commit()
        return {"message": "Drive created! Awaiting admin approval."}, 201

class DriveApplicationsResource(Resource):
    def get(self, drive_id):
        apps = Application.query.filter_by(drive_id=drive_id).all()
        return[{"id": a.id, "student_name": a.student.full_name, "cgpa": a.student.cgpa, "status": a.status} for a in apps], 200

class ApplicationStatusResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('application_id', type=int, required=True)
        parser.add_argument('status', type=str, required=True)
        args = parser.parse_args()
        app = Application.query.get(args['application_id'])
        if app:
            app.status = args['status']
            db.session.commit()
            return {"message": "Status Updated"}, 200

# --- STUDENT ---

class StudentDriveResource(Resource):
    def get(self):
        # Allow students to see all approved drives so they can see deadlines
        drives = PlacementDrive.query.filter(PlacementDrive.status == 'Approved').all()
        return[{"id": d.id, "company_name": d.company.name, "title": d.job_title, "min_cgpa": d.min_cgpa, "deadline": str(d.deadline.date()), "description": d.description, "salary": d.salary, "location": d.location} for d in drives], 200

class StudentProfileAction(Resource):
    def get(self, user_id):
        s = StudentProfile.query.filter_by(user_id=user_id).first()
        return {
            "name": s.full_name, "cgpa": s.cgpa, "resume": s.resume_link,
            "department": s.department, "is_blacklisted": s.is_blacklisted
        }, 200

    def put(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('cgpa', type=float)
        parser.add_argument('resume_link', type=str)
        parser.add_argument('department', type=str)
        args = parser.parse_args()
        s = StudentProfile.query.filter_by(user_id=user_id).first()
        if args['cgpa'] is not None: s.cgpa = args['cgpa']
        if args['resume_link']: s.resume_link = args['resume_link']
        if args['department']: s.department = args['department']
        db.session.commit()
        return {"message": "Profile Updated"}, 200

class StudentCompanyList(Resource):
    def get(self):
        companies = CompanyProfile.query.filter_by(is_approved=True).all()
        return[{"id": c.id, "name": c.name, "description": c.description} for c in companies], 200

class StudentApplyResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('drive_id', type=int, required=True)
        args = parser.parse_args()

        # CRITICAL FIX: Ensure session has latest CGPA from DB
        db.session.expire_all()
        student = StudentProfile.query.filter_by(user_id=args['user_id']).first()
        drive = PlacementDrive.query.get(args['drive_id'])

        if float(student.cgpa) < float(drive.min_cgpa):
            return {"message": f"Eligibility failed. Your CGPA: {student.cgpa}, Required: {drive.min_cgpa}"}, 400
        
        if Application.query.filter_by(student_id=student.id, drive_id=drive.id).first():
            return {"message": "Already applied to this drive"}, 400

        db.session.add(Application(student_id=student.id, drive_id=drive.id, status='Applied'))
        db.session.commit()
        return {"message": "Application submitted successfully!"}, 201

    def get(self, user_id):
        student = StudentProfile.query.filter_by(user_id=user_id).first()
        apps = Application.query.filter_by(student_id=student.id).all()
        return[{"drive_title": a.drive.job_title, "company": a.drive.company.name, "status": a.status, "date": str(a.applied_on.date())} for a in apps], 200