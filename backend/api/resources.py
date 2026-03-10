from flask_restful import Resource, reqparse
from flask_security import hash_password, verify_password
from models import db, User, Role, StudentProfile, CompanyProfile, PlacementDrive, Application
from datetime import datetime
from flask import request
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

# --- AUTH RESOURCES ---
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
            db.session.add(StudentProfile(user_id=new_user.id, full_name=args['name'], cgpa=0.0, department="Computer Science"))
        else:
            db.session.add(CompanyProfile(user_id=new_user.id, name=args['name']))
        db.session.commit()
        return {"message": "Success"}, 201

class UserLogin(Resource):
    def post(self):
        args = login_parser.parse_args()
        user = User.query.filter_by(email=args['email']).first()
        if user and verify_password(args['password'], user.password):
            name = user.student_profile.full_name if user.student_profile else user.company_profile.name if user.company_profile else "Admin"
            return {
                "token": user.get_auth_token(),
                "role": user.roles[0].name,
                "id": user.id,
                "name": name
            }, 200
        return {"message": "Invalid credentials"}, 401

# --- ADMIN RESOURCES ---
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
        search = request.args.get('search', '').lower()
        if target == 'companies':
            items = CompanyProfile.query.all()
            data = [{"id": i.id, "name": i.name, "is_approved": i.is_approved, "is_blacklisted": i.is_blacklisted, "active": i.user.active, "email": i.user.email} for i in items]
        elif target == 'students':
            items = StudentProfile.query.all()
            data = [{"id": i.id, "name": i.full_name, "cgpa": i.cgpa, "is_blacklisted": i.is_blacklisted, "active": i.user.active, "email": i.user.email} for i in items]
        elif target == 'drives':
            items = PlacementDrive.query.all()
            data = [{"id": i.id, "company": i.company.name, "title": i.job_title, "status": i.status} for i in items]
        
        if search:
            data = [i for i in data if search in str(i).lower()]
        return data, 200

    def post(self, target):
        args = reqparse.RequestParser().add_argument('id', type=int, required=True).add_argument('action', type=str, required=True).parse_args()
        if target == 'companies': obj = CompanyProfile.query.get(args['id'])
        elif target == 'drives': obj = PlacementDrive.query.get(args['id'])
        else: obj = StudentProfile.query.get(args['id'])
        
        if args['action'] == 'approve':
            if target == 'drives': obj.status = 'Approved'
            else: obj.is_approved = True
        elif args['action'] == 'blacklist': 
            obj.is_blacklisted = not obj.is_blacklisted
            obj.user.active = not obj.is_blacklisted
        elif args['action'] == 'reject': obj.status = 'Rejected'
        db.session.commit()
        return {"message": "Success"}, 200

# --- COMPANY RESOURCES ---
class CompanyDriveResource(Resource):
    def get(self, company_user_id):
        company = CompanyProfile.query.filter_by(user_id=company_user_id).first()
        drives = PlacementDrive.query.filter_by(company_id=company.id).all() if company else []
        return [{"id": d.id, "title": d.job_title, "status": d.status, "deadline": str(d.deadline.date()), "min_cgpa": d.min_cgpa, "salary": d.salary, "location": d.location, "description": d.description} for d in drives], 200

    def post(self, company_user_id):
        args = reqparse.RequestParser().add_argument('job_title', required=True).add_argument('description', required=True).add_argument('min_cgpa', type=float, required=True).add_argument('salary', required=True).add_argument('location', required=True).add_argument('deadline', required=True).parse_args()
        deadline_date = datetime.strptime(args['deadline'], '%Y-%m-%d').date()
        if deadline_date < datetime.now().date(): return {"message": "Deadline cannot be in the past"}, 400
        company = CompanyProfile.query.filter_by(user_id=company_user_id).first()
        db.session.add(PlacementDrive(company_id=company.id, job_title=args['job_title'], description=args['description'], min_cgpa=args['min_cgpa'], salary=args['salary'], location=args['location'], deadline=deadline_date, status='Pending'))
        db.session.commit(); return {"message": "Success"}, 201

class CompanySingleDriveResource(Resource):
    def put(self, drive_id):
        args = reqparse.RequestParser().add_argument('job_title').add_argument('description').add_argument('min_cgpa', type=float).add_argument('salary').add_argument('location').add_argument('deadline').parse_args()
        d = PlacementDrive.query.get(drive_id)
        if args['job_title']: d.job_title = args['job_title']
        if args['description']: d.description = args['description']
        if args['min_cgpa'] is not None: d.min_cgpa = args['min_cgpa']
        if args['salary']: d.salary = args['salary']
        if args['location']: d.location = args['location']
        if args['deadline']: d.deadline = datetime.strptime(args['deadline'], '%Y-%m-%d')
        db.session.commit(); return {"message": "Updated"}, 200
    def delete(self, drive_id):
        d = PlacementDrive.query.get(drive_id); db.session.delete(d); db.session.commit(); return {"message": "Deleted"}, 200

class CompanyDriveStatusResource(Resource):
    def put(self, drive_id):
        args = reqparse.RequestParser().add_argument('status', required=True).parse_args()
        d = PlacementDrive.query.get(drive_id)
        d.status = args['status']
        db.session.commit(); return {"message": "Success"}, 200

class DriveApplicationsResource(Resource):
    def get(self, drive_id):
        apps = Application.query.filter_by(drive_id=drive_id).all()
        return [{"id": a.id, "student_name": a.student.full_name, "department": a.student.department, "cgpa": a.student.cgpa, "resume": a.student.resume_link, "status": a.status} for a in apps], 200

class ApplicationStatusResource(Resource):
    def post(self):
        args = reqparse.RequestParser().add_argument('application_id', type=int, required=True).add_argument('status', required=True).parse_args()
        app = Application.query.get(args['application_id'])
        if app: app.status = args['status']; db.session.commit()
        return {"message": "Updated"}, 200

# --- STUDENT RESOURCES ---
class StudentDriveResource(Resource):
    def get(self):
        drives = PlacementDrive.query.filter_by(status='Approved').all()
        now = datetime.now().date()
        return [{"id": d.id, "company_id": d.company_id, "company_name": d.company.name, "title": d.job_title, "min_cgpa": d.min_cgpa, "deadline": str(d.deadline.date()), "description": d.description, "salary": d.salary, "location": d.location, "is_expired": d.deadline.date() < now or d.status == 'Closed'} for d in drives], 200

class StudentProfileAction(Resource):
    def get(self, user_id):
        s = StudentProfile.query.filter_by(user_id=user_id).first()
        u = User.query.get(user_id)
        if not s: return {"message": "Not found"}, 404
        return {"name": s.full_name, "cgpa": s.cgpa, "resume": s.resume_link, "department": s.department, "active": u.active, "is_blacklisted": s.is_blacklisted}, 200
    def put(self, user_id):
        args = reqparse.RequestParser().add_argument('cgpa', type=float).add_argument('resume_link').add_argument('department').parse_args()
        s = StudentProfile.query.filter_by(user_id=user_id).first()
        if args['cgpa'] is not None: s.cgpa = args['cgpa']
        if args['resume_link']: s.resume_link = args['resume_link']
        if args['department']: s.department = args['department']
        db.session.commit(); return {"message": "Updated"}, 200

class StudentApplyResource(Resource):
    def post(self):
        args = reqparse.RequestParser().add_argument('user_id', type=int, required=True).add_argument('drive_id', type=int, required=True).parse_args()
        db.session.expire_all()
        student = StudentProfile.query.filter_by(user_id=args['user_id']).first()
        drive = PlacementDrive.query.get(args['drive_id'])
        if not student.user.active or student.is_blacklisted: return {"message": "Blacklisted profile. You cannot apply."}, 403
        if drive.status == 'Closed' or drive.deadline.date() < datetime.now().date(): return {"message": "Drive is closed for applications"}, 400
        if float(student.cgpa) < float(drive.min_cgpa): return {"message": "Ineligible due to low CGPA"}, 400
        if Application.query.filter_by(student_id=student.id, drive_id=drive.id).first(): return {"message": "Already Applied"}, 400
        db.session.add(Application(student_id=student.id, drive_id=drive.id, status='Applied'))
        db.session.commit(); return {"message": "Applied!"}, 201

class StudentHistoryResource(Resource):
    def get(self, user_id):
        student = StudentProfile.query.filter_by(user_id=user_id).first()
        if not student: return [], 200
        apps = Application.query.filter_by(student_id=student.id).all()
        result = []
        for a in apps:
            app_date = "N/A"
            if a.applied_on:
                try:
                    app_date = a.applied_on.strftime('%Y-%m-%d')
                except:
                    app_date = str(a.applied_on).split(' ')[0]
            result.append({"drive_id": a.drive_id, "drive_title": a.drive.job_title, "company": a.drive.company.name, "status": a.status, "date": app_date})
        return result, 200

class StudentCompanyList(Resource):
    def get(self):
        return [{"id": c.id, "name": c.name, "description": c.description} for c in CompanyProfile.query.filter_by(is_approved=True).all()], 200