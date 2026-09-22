from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from app.forms.auth_forms import DEPARTMENTS, YEARS, DIVISIONS


class StudentProfileForm(FlaskForm):
    """Student profile update form."""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full Name is required.'),
        Length(min=3, max=100)
    ])
    phone = StringField('Mobile Number', validators=[
        DataRequired(message='Phone number is required.'),
        Length(min=10, max=15)
    ])
    department = SelectField('Department', choices=DEPARTMENTS, validators=[
        DataRequired(message='Department is required.')
    ])
    year = SelectField('Academic Year', choices=YEARS, validators=[
        DataRequired(message='Academic Year is required.')
    ])
    division = SelectField('Division', choices=DIVISIONS, validators=[
        DataRequired(message='Division is required.')
    ])
    submit = SubmitField('Save Profile Changes')
