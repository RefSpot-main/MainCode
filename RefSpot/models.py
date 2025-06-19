from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Profile information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    headline = db.Column(db.String(200))
    location = db.Column(db.String(100))
    about = db.Column(db.Text)
    current_company = db.Column(db.String(100))
    current_position = db.Column(db.String(100))
    job_status = db.Column(db.String(50), default='employed')  # employed, seeking, open
    open_for_referrals = db.Column(db.Boolean, default=True)  # Whether user accepts referral requests
    profile_image = db.Column(db.String(200))  # Store filename/path
    resume_file = db.Column(db.String(200))  # Store resume filename/path
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skills = db.relationship('UserSkill', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    experiences = db.relationship('Experience', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    educations = db.relationship('Education', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # Connections (relationships defined in Connection model to avoid conflicts)
    
    # Messages (relationships defined in Message model to avoid conflicts)
    
    # Job referrals (removed to avoid backref conflicts - access via JobReferral model)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def is_connected_to(self, user):
        return Connection.query.filter(
            ((Connection.sender_id == self.id) & (Connection.receiver_id == user.id)) |
            ((Connection.sender_id == user.id) & (Connection.receiver_id == self.id))
        ).filter(Connection.status == 'accepted').first() is not None
    
    def has_pending_connection_with(self, user):
        return Connection.query.filter(
            ((Connection.sender_id == self.id) & (Connection.receiver_id == user.id)) |
            ((Connection.sender_id == user.id) & (Connection.receiver_id == self.id))
        ).filter(Connection.status == 'pending').first() is not None


class UserSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    proficiency = db.Column(db.String(20), default='intermediate')  # beginner, intermediate, advanced, expert


class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    current = db.Column(db.Boolean, default=False)
    employment_type = db.Column(db.String(20), default='full-time')  # full-time, part-time, intern, contract
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    company_logo = db.Column(db.String(200))  # Store company logo filename/path


class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    institution = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(100))
    field_of_study = db.Column(db.String(100))
    start_year = db.Column(db.Integer)
    end_year = db.Column(db.Integer)
    current = db.Column(db.Boolean, default=False)


class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_connections', lazy='dynamic'))
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref=db.backref('received_connections', lazy='dynamic'))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    message_request_status = db.Column(db.String(20), default='approved')  # pending, approved, declined
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_messages', lazy='dynamic'))
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref=db.backref('received_messages', lazy='dynamic'))


# Job Referral Request - when someone wants a recommendation for a specific role
class ReferralRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_company = db.Column(db.String(100), nullable=False)
    target_role = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)  # Why they want this role/company
    status = db.Column(db.String(20), default='open')  # open, fulfilled, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Optional expiration date
    
    job_seeker = db.relationship('User', backref='referral_requests')


# Job Referral - when someone recommends a candidate for a role
class JobReferral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Company employee
    candidate_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Job seeker
    referral_request_id = db.Column(db.Integer, db.ForeignKey('referral_request.id'), nullable=True)  # If responding to request
    
    company = db.Column(db.String(100), nullable=False)
    role_title = db.Column(db.String(200), nullable=False)
    role_description = db.Column(db.Text)
    recommendation_text = db.Column(db.Text, nullable=False)  # Why they recommend this person
    referral_type = db.Column(db.String(20), default='direct')  # direct, response
    
    # Contact information for follow-up
    hr_contact = db.Column(db.String(200))  # HR email or contact info
    application_link = db.Column(db.String(500))  # Direct application link
    
    status = db.Column(db.String(20), default='active')  # active, applied, hired, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    referrer = db.relationship('User', foreign_keys=[referrer_id], backref='given_referrals')
    candidate = db.relationship('User', foreign_keys=[candidate_id], backref='received_referrals')
    referral_request = db.relationship('ReferralRequest', backref='referrals')


class JobPosting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    salary_range = db.Column(db.String(100))
    employment_type = db.Column(db.String(50))  # full-time, part-time, contract, etc.
    posted_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    posted_by = db.relationship('User', backref='job_postings')
