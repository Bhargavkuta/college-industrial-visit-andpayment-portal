import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User


DEPARTMENTS = [
    ('Computer Engineering', 'Computer Engineering'),
    ('Information Technology', 'Information Technology'),
    ('Mechanical Engineering', 'Mechanical Engineering'),
    ('Civil Engineering', 'Civil Engineering'),
    ('Electrical Engineering', 'Electrical Engineering'),
    ('Electronics & Telecommunication', 'Electronics & Telecommunication'),
    ('Artificial Intelligence & Data Science', 'Artificial Intelligence & Data Science'),
    ('Automobile Engineering', 'Automobile Engineering')
]

YEARS = [
    ('First Year', 'First Year (FE)'),
    ('Second Year', 'Second Year (SE)'),
    ('Third Year', 'Third Year (TE)'),
    ('Final Year', 'Final Year (BE)')
]

DIVISIONS = [
    ('A', 'Division A'),
    ('B', 'Division B'),
    ('C', 'Division C'),
    ('D', 'Division D')
]


def password_complexity_check(form, field):
    """
    Validates password strength:
    - Minimum 8 characters (enforced by Length validator as well)
    - At least one numeric digit (0-9)
    - At least one special character (!@#$%^&*()_+-=[]{}|;':",.<>/?)
    """
    password = field.data or ''
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one numerical digit (0-9).')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>\-_+=\[\]\\/`~]', password):
        raise ValidationError('Password must contain at least one special character (e.g. !@#$%^&*).')


class StudentRegistrationForm(FlaskForm):
    """Student account creation form with real-time validation."""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full Name is required.'),
        Length(min=3, max=100, message='Name must be between 3 and 100 characters.')
    ])
    email = StringField('College Email Address', validators=[
        DataRequired(message='Email address is required.'),
        Email(message='Please provide a valid email address.'),
        Length(max=120)
    ])
    roll_number = StringField('Roll Number / Student PRN', validators=[
        DataRequired(message='Roll number is required.'),
        Length(min=2, max=50, message='Roll number must be between 2 and 50 characters.')
    ])
    phone = StringField('Mobile Number', validators=[
        DataRequired(message='Phone number is required.'),
        Length(min=10, max=15, message='Please enter a valid 10 to 15-digit mobile number.')
    ])
    department = SelectField('Academic Department', choices=DEPARTMENTS, validators=[
        DataRequired(message='Please select your department.')
    ])
    year = SelectField('Current Academic Year', choices=YEARS, validators=[
        DataRequired(message='Please select your current academic year.')
    ])
    division = SelectField('Class Division', choices=DIVISIONS, validators=[
        DataRequired(message='Please select your division.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=8, message='Password must be at least 8 characters.'),
        password_complexity_check
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords do not match.')
    ])
    submit = SubmitField('Create Student Account')

    def validate_email(self, field):
        """Ensures email uniqueness across all users."""
        email = field.data.strip().lower()
        if User.query.filter(db.func.lower(User.email) == email).first():
            raise ValidationError('An account with this email address already exists. Please login instead.')

    def validate_roll_number(self, field):
        """Ensures roll number uniqueness."""
        roll = field.data.strip().upper()
        if User.query.filter(db.func.upper(User.roll_number) == roll).first():
            raise ValidationError('A student account with this Roll Number / PRN already exists.')


class LoginForm(FlaskForm):
    """User login form."""
    email = StringField('College Email', validators=[
        DataRequired(message='Please enter your email.'),
        Email(message='Please enter a valid email address.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Please enter your password.')
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ChangePasswordForm(FlaskForm):
    """Password update form for authenticated users."""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required.')
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required.'),
        Length(min=8, message='New password must be at least 8 characters.'),
        password_complexity_check
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password.'),
        EqualTo('new_password', message='New passwords do not match.')
    ])
    submit = SubmitField('Update Password')


from app import db
