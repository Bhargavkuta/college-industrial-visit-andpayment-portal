from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class RegistrationStep1Form(FlaskForm):
    """Step 1 & 2 Form: Emergency contact and policy acceptance during registration."""
    emergency_contact = StringField('Emergency Contact Person & Relationship', validators=[
        DataRequired(message='Please provide an emergency contact name and relationship (e.g. Ramesh - Father).'),
        Length(min=3, max=100)
    ])
    emergency_phone = StringField('Emergency Contact Mobile Number', validators=[
        DataRequired(message='Please provide an emergency mobile number.'),
        Length(min=10, max=15, message='Please enter a valid mobile number.')
    ])
    terms_accepted = BooleanField('I agree to the College Code of Conduct, Industrial Visit Safety Guidelines, and Cancellation Policy.', validators=[
        DataRequired(message='You must agree to the guidelines and policies to proceed.')
    ])
    submit = SubmitField('Proceed to Payment Review')


class CancelRegistrationForm(FlaskForm):
    """Form to request registration cancellation."""
    cancellation_reason = TextAreaField('Reason for Cancellation', validators=[
        DataRequired(message='Please provide a reason for cancelling your registration.'),
        Length(min=5, max=500, message='Reason must be between 5 and 500 characters.')
    ])
    submit = SubmitField('Confirm Cancellation')
