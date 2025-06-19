from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, cache
from functools import wraps
from models import User, UserSkill, Experience, Education, Connection, Message, ReferralRequest, JobReferral, JobPosting
from forms import (LoginForm, RegistrationForm, ProfileForm, ExperienceForm, 
                   EducationForm, SkillForm, ConnectionRequestForm, MessageForm,
                   ReferralRequestForm, JobReferralForm, JobPostingForm, SearchForm, ProfilePhotoForm, ResumeUploadForm)
from logo_fetcher import fetch_company_logo, delete_company_logo
from datetime import datetime
from sqlalchemy import or_, and_, desc
from werkzeug.utils import secure_filename
import os
import uuid

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads/profile_photos'
RESUME_UPLOAD_FOLDER = 'static/uploads/resumes'
COMPANY_LOGO_FOLDER = 'static/uploads/company_logos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_RESUME_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_resume_file(filename):
    """Check if the resume file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_RESUME_EXTENSIONS

def save_profile_photo(file):
    """Save uploaded profile photo and return filename"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{file_ext}"
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        return filename
    return None

def save_resume_file(file):
    """Save uploaded resume file and return filename"""
    if file and allowed_resume_file(file.filename):
        # Create upload directory if it doesn't exist
        os.makedirs(RESUME_UPLOAD_FOLDER, exist_ok=True)
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = str(uuid.uuid4()) + '_' + filename
        file_path = os.path.join(RESUME_UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        return unique_filename
    return None

def delete_profile_photo(filename):
    """Delete profile photo from filesystem"""
    if filename:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

def delete_resume_file(filename):
    """Delete resume file from filesystem"""
    if filename:
        file_path = os.path.join(RESUME_UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)



# Performance optimization helpers
def cache_key_for_user(user_id, suffix=""):
    """Generate cache key for user-specific data"""
    return f"user_{user_id}_{suffix}"

def invalidate_user_cache(user_id):
    """Invalidate all cache entries for a user"""
    try:
        cache.delete(cache_key_for_user(user_id, "connections"))
        cache.delete(cache_key_for_user(user_id, "messages"))
        cache.delete(cache_key_for_user(user_id, "profile"))
    except Exception:
        # Cache is not available, continue without caching
        pass

@cache.memoize(timeout=300)
def get_user_connections_cached(user_id):
    """Get user connections with caching"""
    return db.session.query(User).join(
        Connection, 
        or_(
            and_(Connection.sender_id == user_id, Connection.receiver_id == User.id),
            and_(Connection.receiver_id == user_id, Connection.sender_id == User.id)
        )
    ).filter(
        Connection.status == 'accepted',
        User.id != user_id
    ).all()

@cache.memoize(timeout=60)
def get_message_counts(user_id):
    """Get message counts with caching"""
    unread_count = Message.query.filter_by(
        receiver_id=user_id, 
        read=False,
        message_request_status='approved'
    ).count()
    
    pending_requests = Message.query.filter_by(
        receiver_id=user_id,
        message_request_status='pending'
    ).count()
    
    return unread_count, pending_requests


@app.route('/')
def index():
    if current_user.is_authenticated:
        # Show dashboard for logged-in users
        recent_connections = Connection.query.filter(
            or_(Connection.sender_id == current_user.id, 
                Connection.receiver_id == current_user.id)
        ).filter(Connection.status == 'accepted').order_by(Connection.updated_at.desc()).limit(5).all()
        
        unread_messages = Message.query.filter_by(
            receiver_id=current_user.id, read=False
        ).count()
        
        pending_requests = Connection.query.filter_by(
            receiver_id=current_user.id, status='pending'
        ).count()
        
        recent_referrals = JobReferral.query.filter_by(
            candidate_id=current_user.id
        ).order_by(JobReferral.created_at.desc()).limit(3).all()
        
        return render_template('index.html', 
                             recent_connections=recent_connections,
                             unread_messages=unread_messages,
                             pending_requests=pending_requests,
                             recent_referrals=recent_referrals)
    else:
        return render_template('index.html')


# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
            return render_template('auth/register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return render_template('auth/register.html', form=form)
        
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


# Profile routes
@app.route('/profile/<username>')
@login_required
def view_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    skills = UserSkill.query.filter_by(user_id=user.id).all()
    experiences = Experience.query.filter_by(user_id=user.id).order_by(Experience.start_date.desc()).all()
    educations = Education.query.filter_by(user_id=user.id).order_by(Education.start_year.desc()).all()
    referrals = JobReferral.query.filter_by(candidate_id=user.id).order_by(JobReferral.created_at.desc()).all()
    
    is_own_profile = current_user.id == user.id
    is_connected = current_user.is_connected_to(user) if not is_own_profile else False
    has_pending_request = current_user.has_pending_connection_with(user) if not is_own_profile else False
    
    return render_template('profile/view.html', user=user, skills=skills, 
                         experiences=experiences, educations=educations,
                         referrals=referrals, is_own_profile=is_own_profile,
                         is_connected=is_connected, has_pending_request=has_pending_request)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.headline = form.headline.data
        current_user.location = form.location.data
        current_user.about = form.about.data
        current_user.current_company = form.current_company.data
        current_user.current_position = form.current_position.data
        current_user.job_status = form.job_status.data
        current_user.open_for_referrals = form.open_for_referrals.data
        current_user.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('view_profile', username=current_user.username))
    
    # Pre-populate form with current data
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.headline.data = current_user.headline
    form.location.data = current_user.location
    form.about.data = current_user.about
    form.current_company.data = current_user.current_company
    form.current_position.data = current_user.current_position
    form.job_status.data = current_user.job_status
    form.open_for_referrals.data = current_user.open_for_referrals
    
    resume_form = ResumeUploadForm()
    return render_template('profile/edit.html', form=form, ResumeUploadForm=ResumeUploadForm)


# Skills routes
@app.route('/profile/skills/add', methods=['POST'])
@login_required
def add_skill():
    skill_name = request.form.get('skill_name')
    proficiency = request.form.get('proficiency', 'intermediate')
    
    if skill_name:
        # Check if skill already exists for user
        existing_skill = UserSkill.query.filter_by(
            user_id=current_user.id, 
            skill_name=skill_name
        ).first()
        
        if not existing_skill:
            skill = UserSkill(
                user_id=current_user.id,
                skill_name=skill_name,
                proficiency=proficiency
            )
            db.session.add(skill)
            db.session.commit()
            flash('Skill added successfully!', 'success')
        else:
            flash('You already have this skill listed', 'warning')
    else:
        flash('Please enter a skill name', 'error')
    
    return redirect(url_for('edit_profile'))


@app.route('/profile/skills/<int:skill_id>/delete', methods=['POST'])
@login_required
def delete_skill(skill_id):
    skill = UserSkill.query.get_or_404(skill_id)
    if skill.user_id != current_user.id:
        abort(403)
    
    db.session.delete(skill)
    db.session.commit()
    flash('Skill removed successfully!', 'success')
    return redirect(url_for('edit_profile'))


# Experience routes
@app.route('/profile/experience/add', methods=['GET', 'POST'])
@login_required
def add_experience():
    form = ExperienceForm()
    if form.validate_on_submit():
        # Automatically fetch company logo
        company_logo_filename = fetch_company_logo(form.company.data)
        
        experience = Experience(
            user_id=current_user.id,
            company=form.company.data,
            position=form.position.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data if not form.current.data else None,
            current=form.current.data,
            employment_type=form.employment_type.data,
            description=form.description.data,
            location=form.location.data,
            company_logo=company_logo_filename
        )
        db.session.add(experience)
        db.session.commit()
        flash('Work experience added successfully!', 'success')
        return redirect(url_for('view_profile', username=current_user.username))
    
    return render_template('profile/add_experience.html', form=form)


@app.route('/profile/experience/<int:experience_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_experience(experience_id):
    experience = Experience.query.get_or_404(experience_id)
    if experience.user_id != current_user.id:
        abort(403)
    
    form = ExperienceForm(obj=experience)
    if form.validate_on_submit():
        # Check if company name changed
        if experience.company != form.company.data:
            # Delete old logo if exists
            if experience.company_logo:
                delete_company_logo(experience.company_logo)
            # Fetch new logo for the new company
            experience.company_logo = fetch_company_logo(form.company.data)
        
        experience.company = form.company.data
        experience.position = form.position.data
        experience.start_date = form.start_date.data
        experience.end_date = form.end_date.data if not form.current.data else None
        experience.current = form.current.data
        experience.employment_type = form.employment_type.data
        experience.description = form.description.data
        experience.location = form.location.data
        
        db.session.commit()
        flash('Work experience updated successfully!', 'success')
        return redirect(url_for('view_profile', username=current_user.username))
    
    return render_template('profile/edit_experience.html', form=form, experience=experience)


@app.route('/profile/experience/<int:experience_id>/delete')
@login_required
def delete_experience(experience_id):
    experience = Experience.query.get_or_404(experience_id)
    if experience.user_id != current_user.id:
        abort(403)
    
    # Delete company logo if exists
    if experience.company_logo:
        delete_company_logo(experience.company_logo)
    
    db.session.delete(experience)
    db.session.commit()
    flash('Work experience deleted successfully!', 'success')
    return redirect(url_for('view_profile', username=current_user.username))


# Profile Photo routes
@app.route('/profile/photo/upload', methods=['POST'])
@login_required
def upload_profile_photo():
    if 'photo' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('edit_profile'))
    
    file = request.files['photo']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('edit_profile'))
    
    if file and allowed_file(file.filename):
        # Delete old photo if exists
        if current_user.profile_image:
            delete_profile_photo(current_user.profile_image)
        
        # Save new photo
        filename = save_profile_photo(file)
        if filename:
            current_user.profile_image = filename
            db.session.commit()
            flash('Profile photo updated successfully!', 'success')
        else:
            flash('Error uploading photo', 'error')
    else:
        flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.', 'error')
    
    return redirect(url_for('edit_profile'))

@app.route('/profile/photo/camera', methods=['POST'])
@login_required
def upload_camera_photo():
    """Handle photo captured from camera"""
    if 'photo' not in request.files:
        flash('No photo captured', 'error')
        return redirect(url_for('edit_profile'))
    
    file = request.files['photo']
    if file and file.filename:
        # Delete old photo if exists
        if current_user.profile_image:
            delete_profile_photo(current_user.profile_image)
        
        # Save new photo
        filename = save_profile_photo(file)
        if filename:
            current_user.profile_image = filename
            db.session.commit()
            flash('Profile photo updated successfully!', 'success')
        else:
            flash('Error saving photo', 'error')
    else:
        flash('No photo data received', 'error')
    
    return redirect(url_for('edit_profile'))

@app.route('/profile/photo/remove', methods=['POST'])
@login_required
def remove_profile_photo():
    if current_user.profile_image:
        delete_profile_photo(current_user.profile_image)
        current_user.profile_image = None
        db.session.commit()
        flash('Profile photo removed successfully!', 'success')
    else:
        flash('No profile photo to remove', 'warning')
    
    return redirect(url_for('edit_profile'))

@app.route('/profile/resume/upload', methods=['POST'])
@login_required
def upload_resume():
    form = ResumeUploadForm()
    
    if form.validate_on_submit():
        file = form.resume.data
        
        if file and allowed_resume_file(file.filename):
            # Delete old resume if exists
            if current_user.resume_file:
                delete_resume_file(current_user.resume_file)
            
            # Save new resume
            filename = save_resume_file(file)
            if filename:
                current_user.resume_file = filename
                db.session.commit()
                flash('Resume uploaded successfully!', 'success')
            else:
                flash('Error uploading resume', 'error')
        else:
            flash('Invalid file type. Please upload PDF files only.', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('edit_profile'))

@app.route('/profile/resume/download/<filename>')
@login_required
def download_resume(filename):
    from flask import send_from_directory
    
    # Security check - only allow users to download their own resume or if they're viewing someone else's profile
    user = User.query.filter_by(resume_file=filename).first()
    if not user:
        abort(404)
    
    try:
        return send_from_directory(RESUME_UPLOAD_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/profile/resume/remove', methods=['POST'])
@login_required
def remove_resume():
    if current_user.resume_file:
        delete_resume_file(current_user.resume_file)
        current_user.resume_file = None
        db.session.commit()
        flash('Resume removed successfully!', 'success')
    else:
        flash('No resume to remove', 'warning')
    
    return redirect(url_for('edit_profile'))


# Connections routes
@app.route('/connections')
@login_required
def connections():
    accepted_connections = db.session.query(Connection).filter(
        or_(
            and_(Connection.sender_id == current_user.id, Connection.status == 'accepted'),
            and_(Connection.receiver_id == current_user.id, Connection.status == 'accepted')
        )
    ).all()
    
    # Get the actual connected users
    connected_users = []
    for conn in accepted_connections:
        if conn.sender_id == current_user.id:
            connected_users.append(conn.receiver)
        else:
            connected_users.append(conn.sender)
    
    return render_template('connections/index.html', connected_users=connected_users)


@app.route('/connections/requests')
@login_required
def connection_requests():
    # Get connection requests where current user is the receiver (incoming requests)
    incoming_requests = db.session.query(Connection, User).join(
        User, Connection.sender_id == User.id
    ).filter(
        Connection.receiver_id == current_user.id,
        Connection.status == 'pending'
    ).order_by(Connection.created_at.desc()).all()
    
    # Get connection requests where current user is the sender (outgoing requests)
    outgoing_requests = db.session.query(Connection, User).join(
        User, Connection.receiver_id == User.id
    ).filter(
        Connection.sender_id == current_user.id,
        Connection.status == 'pending'
    ).order_by(Connection.created_at.desc()).all()
    
    return render_template('connections/requests.html', 
                         incoming_requests=incoming_requests,
                         outgoing_requests=outgoing_requests)


@app.route('/connect/<username>', methods=['GET', 'POST'])
@login_required
def send_connection_request(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    if user.id == current_user.id:
        flash('You cannot connect to yourself', 'error')
        return redirect(url_for('view_profile', username=username))
    
    # Check if already connected or request pending
    existing_connection = Connection.query.filter(
        or_(
            and_(Connection.sender_id == current_user.id, Connection.receiver_id == user.id),
            and_(Connection.sender_id == user.id, Connection.receiver_id == current_user.id)
        )
    ).first()
    
    if existing_connection:
        if existing_connection.status == 'accepted':
            flash('You are already connected to this user', 'info')
        else:
            flash('Connection request already pending', 'info')
        return redirect(url_for('view_profile', username=username))
    
    # If it's a POST request with no form (direct connect button)
    if request.method == 'POST' and not request.form.get('message'):
        connection = Connection(
            sender_id=current_user.id,
            receiver_id=user.id,
            message=""
        )
        db.session.add(connection)
        db.session.commit()
        flash('Connection request sent!', 'success')
        return redirect(url_for('view_profile', username=username))
    
    # Handle form submission
    form = ConnectionRequestForm()
    if form.validate_on_submit():
        connection = Connection(
            sender_id=current_user.id,
            receiver_id=user.id,
            message=form.message.data
        )
        db.session.add(connection)
        db.session.commit()
        flash('Connection request sent!', 'success')
        return redirect(url_for('view_profile', username=username))
    
    return render_template('connections/send_request.html', form=form, user=user)


@app.route('/connections/<int:request_id>/accept', methods=['POST'])
@login_required
def accept_connection(request_id):
    connection = Connection.query.get_or_404(request_id)
    
    if connection.receiver_id != current_user.id:
        abort(403)
    
    connection.status = 'accepted'
    connection.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Connection accepted!', 'success')
    return redirect(url_for('connection_requests'))


@app.route('/connections/<int:request_id>/decline', methods=['POST'])
@login_required
def decline_connection(request_id):
    connection = Connection.query.get_or_404(request_id)
    
    if connection.receiver_id != current_user.id:
        abort(403)
    
    connection.status = 'declined'
    connection.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Connection declined', 'info')
    return redirect(url_for('connection_requests'))

@app.route('/connections/<int:request_id>/cancel', methods=['POST'])
@login_required
def cancel_connection_request(request_id):
    connection = Connection.query.get_or_404(request_id)
    
    # Only the sender can cancel their own request
    if connection.sender_id != current_user.id:
        abort(403)
    
    # Only allow canceling pending requests
    if connection.status != 'pending':
        flash('Cannot cancel this connection request', 'error')
        return redirect(url_for('connection_requests'))
    
    # Delete the connection request
    db.session.delete(connection)
    db.session.commit()
    
    flash('Connection request canceled', 'info')
    return redirect(url_for('connection_requests'))


@app.route('/connections/<int:connection_id>/remove', methods=['POST'])
@login_required
def remove_connection(connection_id):
    connection = Connection.query.get_or_404(connection_id)
    
    # Check if current user is part of this connection
    if connection.sender_id != current_user.id and connection.receiver_id != current_user.id:
        abort(403)
    
    # Only allow removal of accepted connections
    if connection.status != 'accepted':
        flash('Connection not found or already removed', 'error')
        return redirect(url_for('connections'))
    
    db.session.delete(connection)
    db.session.commit()
    flash('Connection removed successfully', 'success')
    return redirect(url_for('connections'))


@app.route('/connections/remove/<username>', methods=['POST'])
@login_required
def remove_connection_by_username(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Find the connection between current user and the target user
    connection = Connection.query.filter(
        or_(
            and_(Connection.sender_id == current_user.id, Connection.receiver_id == user.id),
            and_(Connection.sender_id == user.id, Connection.receiver_id == current_user.id)
        ),
        Connection.status == 'accepted'
    ).first()
    
    if not connection:
        flash('Connection not found', 'error')
        return redirect(url_for('connections'))
    
    db.session.delete(connection)
    db.session.commit()
    flash(f'Removed connection with {user.get_full_name()}', 'success')
    return redirect(url_for('connections'))


# Messages routes
@app.route('/messages')
@login_required
def messages():
    # Get approved conversations only
    conversations = db.session.query(Message).filter(
        or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id),
        Message.message_request_status == 'approved'
    ).order_by(Message.created_at.desc()).all()
    
    # Group by conversation partner
    conversation_partners = {}
    for message in conversations:
        partner_id = message.sender_id if message.receiver_id == current_user.id else message.receiver_id
        if partner_id not in conversation_partners:
            partner = User.query.get(partner_id)
            conversation_partners[partner_id] = {
                'user': partner,
                'last_message': message,
                'unread_count': Message.query.filter_by(
                    sender_id=partner_id, receiver_id=current_user.id, read=False,
                    message_request_status='approved'
                ).count()
            }
    
    return render_template('messages/index.html', conversations=conversation_partners.values())


@app.route('/messages/requests')
@login_required
def message_requests():
    # Get pending message requests
    pending_requests = Message.query.filter_by(
        receiver_id=current_user.id, 
        message_request_status='pending'
    ).order_by(Message.created_at.desc()).all()
    
    return render_template('messages/requests.html', pending_requests=pending_requests)


@app.route('/messages/requests/<int:message_id>/approve', methods=['POST'])
@login_required
def approve_message_request(message_id):
    message = Message.query.get_or_404(message_id)
    
    if message.receiver_id != current_user.id:
        abort(403)
    
    message.message_request_status = 'approved'
    db.session.commit()
    
    flash('Message request approved', 'success')
    return redirect(url_for('message_requests'))


@app.route('/messages/requests/<int:message_id>/decline', methods=['POST'])
@login_required
def decline_message_request(message_id):
    message = Message.query.get_or_404(message_id)
    
    if message.receiver_id != current_user.id:
        abort(403)
    
    message.message_request_status = 'declined'
    db.session.commit()
    
    flash('Message request declined', 'info')
    return redirect(url_for('message_requests'))


@app.route('/messages/<username>', methods=['GET', 'POST'])
@login_required
def conversation(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Check if there's an existing approved conversation
    existing_conversation = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == user.id),
            and_(Message.sender_id == user.id, Message.receiver_id == current_user.id)
        ),
        Message.message_request_status == 'approved'
    ).first()
    
    # If no approved conversation exists, create a message request
    if not existing_conversation:
        flash('This will send a message request to the user', 'info')
    
    # Mark approved messages as read
    Message.query.filter_by(
        sender_id=user.id, receiver_id=current_user.id, read=False,
        message_request_status='approved'
    ).update({'read': True})
    db.session.commit()
    
    form = MessageForm()
    if form.validate_on_submit():
        # Determine message status based on existing conversation or connection
        is_connected = current_user.is_connected_to(user)
        message_status = 'approved' if (is_connected or existing_conversation) else 'pending'
        
        message = Message(
            sender_id=current_user.id,
            receiver_id=user.id,
            content=form.content.data,
            message_request_status=message_status
        )
        db.session.add(message)
        db.session.commit()
        
        # Clear form after successful submission for traditional form
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form.content.data = ''
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON response for AJAX
            from datetime import datetime
            return jsonify({
                'success': True,
                'message': {
                    'content': message.content,
                    'time': message.created_at.strftime('%I:%M %p'),
                    'status': message_status
                },
                'flash_message': 'Message request sent! The user will need to approve it first.' if message_status == 'pending' else 'Message sent!'
            })
        else:
            # Traditional form submission - redirect with flash message
            if message_status == 'pending':
                flash('Message request sent! The user will need to approve it first.', 'success')
            else:
                flash('Message sent!', 'success')
            return redirect(url_for('conversation', username=username))
    elif request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Handle AJAX form validation errors
        errors = []
        for field, field_errors in form.errors.items():
            for error in field_errors:
                errors.append(f"{field}: {error}")
        
        return jsonify({
            'success': False,
            'error': '; '.join(errors) if errors else 'Please fill in all required fields'
        })
    
    # Get all conversation history (approved messages)
    # Force a fresh query by clearing any cached results
    db.session.expire_all()
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == user.id),
            and_(Message.sender_id == user.id, Message.receiver_id == current_user.id)
        ),
        Message.message_request_status == 'approved'
    ).order_by(Message.created_at.asc()).all()
    
    return render_template('messages/conversation.html', user=user, messages=messages, form=form)

@app.route('/messages/<username>/delete', methods=['POST'])
@login_required
def delete_conversation(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Delete all messages between current user and target user
    Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == user.id),
            and_(Message.sender_id == user.id, Message.receiver_id == current_user.id)
        )
    ).delete()
    db.session.commit()
    
    flash(f'Conversation with {user.get_full_name()} has been deleted.', 'success')
    return redirect(url_for('messages'))

@app.route('/api/messages/send', methods=['POST'])
@login_required
def send_message_api():
    """API endpoint for sending messages via AJAX"""
    try:
        data = request.get_json()
        username = data.get('username')
        content = data.get('content')
        
        if not username or not content:
            return jsonify({'success': False, 'error': 'Missing username or content'}), 400
            
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
            
        # Check if users are connected or have existing conversation
        is_connected = current_user.is_connected_to(user)
        existing_conversation = Message.query.filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == user.id),
                and_(Message.sender_id == user.id, Message.receiver_id == current_user.id)
            ),
            Message.message_request_status == 'approved'
        ).first()
        
        message_status = 'approved' if (is_connected or existing_conversation) else 'pending'
        
        message = Message(
            sender_id=current_user.id,
            receiver_id=user.id,
            content=content,
            message_request_status=message_status
        )
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message_id': message.id,
            'content': message.content,
            'time': message.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'status': message_status
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Job Referrals routes
@app.route('/referrals')
@login_required
def referrals():
    # Get referral requests (people looking for jobs)
    open_requests = ReferralRequest.query.filter_by(status='open').order_by(ReferralRequest.created_at.desc()).all()
    
    # Get referrals I've given (as a company employee)
    given_referrals = JobReferral.query.filter_by(referrer_id=current_user.id).order_by(JobReferral.created_at.desc()).all()
    
    # Get referrals I've received (as a job seeker)
    received_referrals = JobReferral.query.filter_by(candidate_id=current_user.id).order_by(JobReferral.created_at.desc()).all()
    
    # Get my own referral requests
    my_requests = ReferralRequest.query.filter_by(job_seeker_id=current_user.id).order_by(ReferralRequest.created_at.desc()).all()
    
    return render_template('referrals/index.html', 
                         open_requests=open_requests,
                         given_referrals=given_referrals,
                         received_referrals=received_referrals,
                         my_requests=my_requests)


@app.route('/referrals/request', methods=['GET', 'POST'])
@login_required
def request_referral():
    form = ReferralRequestForm()
    if form.validate_on_submit():
        referral_request = ReferralRequest(
            job_seeker_id=current_user.id,
            target_company=form.target_company.data,
            target_role=form.target_role.data,
            message=form.message.data
        )
        db.session.add(referral_request)
        db.session.commit()
        flash('Referral request posted successfully! Company employees can now see your request.', 'success')
        return redirect(url_for('referrals'))
    
    return render_template('referrals/request.html', form=form)

@app.route('/referrals/request-from/<username>', methods=['GET', 'POST'])
@login_required
def request_referral_from_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Check if users are connected
    if not current_user.is_connected_to(user):
        flash('You can only request referrals from your connections.', 'error')
        return redirect(url_for('view_profile', username=username))
    
    # Check if user is open for referrals
    if not user.open_for_referrals:
        flash(f'{user.get_full_name()} is not currently accepting referral requests.', 'error')
        return redirect(url_for('view_profile', username=username))
    
    form = ReferralRequestForm()
    if form.validate_on_submit():
        # Create a targeted referral request
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        referral_request = ReferralRequest(
            job_seeker_id=current_user.id,
            target_company=form.target_company.data,
            target_role=form.target_role.data,
            message=form.message.data,
            expires_at=expires_at
        )
        db.session.add(referral_request)
        db.session.commit()
        
        # Send a message to the user about the referral request
        message_content = f"Hi {user.get_full_name()},\n\nI've posted a referral request for {form.target_role.data} at {form.target_company.data}. If you have any connections there, I'd really appreciate your help!\n\nYou can view the request in the Referrals section.\n\nThanks!"
        
        message = Message(
            sender_id=current_user.id,
            receiver_id=user.id,
            content=message_content,
            message_request_status='approved'  # Auto-approve since they're connected
        )
        db.session.add(message)
        db.session.commit()
        
        flash(f'Referral request sent to {user.get_full_name()}! They\'ve been notified via message.', 'success')
        return redirect(url_for('view_profile', username=username))
    
    return render_template('referrals/request_from_user.html', form=form, user=user)


@app.route('/referrals/give/<username>', methods=['GET', 'POST'])
@login_required
def give_referral(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    if user.id == current_user.id:
        flash('You cannot refer yourself', 'error')
        return redirect(url_for('view_profile', username=username))
    
    form = JobReferralForm()
    
    # Pre-fill company if current user has one
    if request.method == 'GET' and current_user.current_company:
        form.company.data = current_user.current_company
    
    if form.validate_on_submit():
        job_referral = JobReferral(
            referrer_id=current_user.id,
            candidate_id=user.id,
            company=form.company.data,
            role_title=form.role_title.data,
            role_description=form.role_description.data,
            recommendation_text=form.recommendation_text.data,
            hr_contact=form.hr_contact.data,
            application_link=form.application_link.data,
            referral_type='direct'
        )
        db.session.add(job_referral)
        db.session.commit()
        flash('Job referral submitted successfully!', 'success')
        return redirect(url_for('view_profile', username=username))
    
    return render_template('referrals/give.html', form=form, user=user, is_referral=True)


@app.route('/referrals/respond/<int:request_id>', methods=['GET', 'POST'])
@login_required
def respond_to_request(request_id):
    referral_request = ReferralRequest.query.get_or_404(request_id)
    
    if referral_request.job_seeker_id == current_user.id:
        flash('You cannot respond to your own request', 'error')
        return redirect(url_for('referrals'))
    
    form = JobReferralForm()
    
    # Pre-fill with request details
    if request.method == 'GET':
        form.company.data = referral_request.target_company
        form.role_title.data = referral_request.target_role
    
    if form.validate_on_submit():
        job_referral = JobReferral(
            referrer_id=current_user.id,
            candidate_id=referral_request.job_seeker_id,
            referral_request_id=request_id,
            company=form.company.data,
            role_title=form.role_title.data,
            role_description=form.role_description.data,
            recommendation_text=form.recommendation_text.data,
            hr_contact=form.hr_contact.data,
            application_link=form.application_link.data,
            referral_type='response'
        )
        db.session.add(job_referral)
        
        # Mark request as fulfilled
        referral_request.status = 'fulfilled'
        
        db.session.commit()
        flash('Referral response submitted successfully!', 'success')
        return redirect(url_for('referrals'))
    
    return render_template('recommendations/respond.html', form=form, request=referral_request)


# Jobs routes
@app.route('/jobs')
@login_required
def jobs():
    search_query = request.args.get('search', '')
    location_filter = request.args.get('location', '')
    
    query = JobPosting.query.filter_by(is_active=True)
    
    if search_query:
        query = query.filter(
            or_(
                JobPosting.title.contains(search_query),
                JobPosting.company.contains(search_query),
                JobPosting.description.contains(search_query)
            )
        )
    
    if location_filter:
        query = query.filter(JobPosting.location.contains(location_filter))
    
    jobs = query.order_by(JobPosting.created_at.desc()).all()
    
    return render_template('jobs/index.html', jobs=jobs, 
                         search_query=search_query, location_filter=location_filter)


@app.route('/jobs/post', methods=['GET', 'POST'])
@login_required
def post_job():
    form = JobPostingForm()
    if form.validate_on_submit():
        job = JobPosting(
            title=form.title.data,
            company=form.company.data,
            location=form.location.data,
            description=form.description.data,
            requirements=form.requirements.data,
            salary_range=form.salary_range.data,
            employment_type=form.employment_type.data,
            posted_by_id=current_user.id
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('jobs'))
    
    return render_template('jobs/index.html', form=form)


# Search routes
@app.route('/search')
@login_required
def search():
    form = SearchForm()
    results = []
    
    if request.args.get('query'):
        query = request.args.get('query')
        search_type = request.args.get('search_type', 'people')
        
        if search_type in ['people', 'all']:
            people = User.query.filter(
                or_(
                    User.username.contains(query),
                    User.first_name.contains(query),
                    User.last_name.contains(query),
                    User.headline.contains(query),
                    User.current_company.contains(query)
                )
            ).filter(User.id != current_user.id).all()
            
            for person in people:
                results.append({
                    'type': 'person',
                    'data': person
                })
        
        if search_type in ['jobs', 'all']:
            jobs = JobPosting.query.filter(
                JobPosting.is_active == True,
                or_(
                    JobPosting.title.contains(query),
                    JobPosting.company.contains(query),
                    JobPosting.description.contains(query)
                )
            ).all()
            
            for job in jobs:
                results.append({
                    'type': 'job',
                    'data': job
                })
    
    return render_template('search/index.html', form=form, results=results, query=request.args.get('query', ''))
