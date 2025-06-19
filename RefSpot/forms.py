from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SelectField, DateField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from wtforms.widgets import TextArea


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', 
                             validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=50)])
    headline = StringField('Professional Headline', validators=[Optional(), Length(max=200)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    about = TextAreaField('About', validators=[Optional()], widget=TextArea())
    current_company = StringField('Current Company', validators=[Optional(), Length(max=100)])
    current_position = StringField('Current Position', validators=[Optional(), Length(max=100)])
    job_status = SelectField('Job Status', choices=[
        ('employed', 'Employed'),
        ('seeking', 'Actively Seeking'),
        ('open', 'Open to Opportunities')
    ], default='employed')
    open_for_referrals = BooleanField('Open for Referrals', description='Allow others to request referrals from you')
    submit = SubmitField('Update Profile')


class ExperienceForm(FlaskForm):
    company = StringField('Company', validators=[DataRequired(), Length(max=100)])
    position = StringField('Position', validators=[DataRequired(), Length(max=100)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    current = BooleanField('I currently work here')
    employment_type = SelectField('Employment Type', choices=[
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('intern', 'Internship'),
        ('contract', 'Contract')
    ], default='full-time')
    description = TextAreaField('Description', validators=[Optional()])
    location = StringField('Location', validators=[Optional(), Length(max=100)])

    submit = SubmitField('Save Experience')


class EducationForm(FlaskForm):
    institution = StringField('Institution', validators=[DataRequired(), Length(max=100)])
    degree = StringField('Degree', validators=[Optional(), Length(max=100)])
    field_of_study = StringField('Field of Study', validators=[Optional(), Length(max=100)])
    start_year = SelectField('Start Year', coerce=int, validators=[Optional()])
    end_year = SelectField('End Year', coerce=int, validators=[Optional()])
    current = BooleanField('I currently study here')
    submit = SubmitField('Save Education')


class SkillForm(FlaskForm):
    skill_name = StringField('Skill', validators=[DataRequired(), Length(max=100)])
    proficiency = SelectField('Proficiency', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ], default='intermediate')
    submit = SubmitField('Add Skill')


class ConnectionRequestForm(FlaskForm):
    message = TextAreaField('Message', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Send Connection Request')


class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired()], widget=TextArea())
    submit = SubmitField('Send Message')


class ReferralRequestForm(FlaskForm):
    target_company = StringField('Company', validators=[DataRequired(), Length(max=100)])
    target_role = StringField('Role/Position', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Why do you want this role?', validators=[Optional()], widget=TextArea())
    submit = SubmitField('Request Referral')


class JobReferralForm(FlaskForm):
    company = StringField('Company', validators=[DataRequired(), Length(max=100)])
    role_title = StringField('Role Title', validators=[DataRequired(), Length(max=200)])
    role_description = TextAreaField('Role Description', validators=[Optional()])
    recommendation_text = TextAreaField('Why do you recommend this candidate?', validators=[DataRequired()], widget=TextArea())
    hr_contact = StringField('HR Contact (email/phone)', validators=[Optional(), Length(max=200)])
    application_link = StringField('Application Link', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Referral')


class JobPostingForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(max=200)])
    company = StringField('Company', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    requirements = TextAreaField('Requirements', validators=[Optional()])
    salary_range = StringField('Salary Range', validators=[Optional(), Length(max=100)])
    employment_type = SelectField('Employment Type', choices=[
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship')
    ], default='full-time')
    submit = SubmitField('Post Job')


class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    search_type = SelectField('Search In', choices=[
        ('people', 'People'),
        ('jobs', 'Jobs'),
        ('all', 'Everything')
    ], default='people')
    submit = SubmitField('Search')

class ProfilePhotoForm(FlaskForm):
    photo = FileField('Profile Photo')
    submit = SubmitField('Upload Photo')

class ResumeUploadForm(FlaskForm):
    resume = FileField('Resume (PDF only)', validators=[DataRequired()])
    submit = SubmitField('Upload Resume')
