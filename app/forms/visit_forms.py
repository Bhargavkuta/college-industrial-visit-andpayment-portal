from datetime import datetime, date, time
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, DateField, TimeField, 
    IntegerField, FloatField, SelectField, SubmitField, SelectMultipleField, widgets
)
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from app.forms.auth_forms import DEPARTMENTS, YEARS


VISIT_STATUS_CHOICES = [
    ('draft', 'Draft (Hidden from students)'),
    ('published', 'Published (Open for registration)'),
    ('closed', 'Closed (No new registrations)'),
    ('cancelled', 'Cancelled'),
    ('completed', 'Completed')
]


class MultiCheckboxField(SelectMultipleField):
    """A multiple-select field that displays a list of checkboxes."""
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class VisitForm(FlaskForm):
    """Form used by Administrators to Create and Edit Industrial Visits."""
    title = StringField('Visit Title / Theme', validators=[
        DataRequired(message='Visit title is required.'),
        Length(min=5, max=200, message='Title must be between 5 and 200 characters.')
    ])
    company_name = StringField('Company / Organization Name', validators=[
        DataRequired(message='Company name is required.'),
        Length(min=2, max=150, message='Company name must be between 2 and 150 characters.')
    ])
    company_logo = StringField('Company Logo Image URL', validators=[
        Length(max=255)
    ])
    cover_image = StringField('Cover / Banner Image URL', validators=[
        Length(max=255)
    ])
    description = TextAreaField('Detailed Visit Overview & Learning Objectives', validators=[
        DataRequired(message='Description is required.'),
        Length(min=20, message='Please write at least 20 characters describing the visit.')
    ])
    location = StringField('Industrial Facility Address & Location', validators=[
        DataRequired(message='Location is required.'),
        Length(max=200)
    ])
    meeting_point = StringField('Campus Assembly / Meeting Point', validators=[
        DataRequired(message='Meeting point is required.'),
        Length(max=200)
    ])
    visit_date = DateField('Date of Visit', validators=[
        DataRequired(message='Visit date is required.')
    ])
    start_time = TimeField('Reporting / Start Time', validators=[
        DataRequired(message='Start time is required.')
    ])
    end_time = TimeField('Expected Conclusion / Return Time', validators=[
        DataRequired(message='End time is required.')
    ])
    capacity = IntegerField('Total Seat Capacity', validators=[
        DataRequired(message='Capacity is required.'),
        NumberRange(min=1, max=500, message='Capacity must be between 1 and 500 seats.')
    ], default=50)
    fee = FloatField('Student Registration Fee (₹)', validators=[
        DataRequired(message='Fee is required (enter 0 for free visits).'),
        NumberRange(min=0.0, max=50000.0, message='Registration fee cannot be negative.')
    ], default=0.0)
    registration_deadline_date = DateField('Registration Deadline Date', validators=[
        DataRequired(message='Deadline date is required.')
    ])
    registration_deadline_time = TimeField('Registration Deadline Time', validators=[
        DataRequired(message='Deadline time is required.')
    ], default=time(23, 59))
    
    # Comma-separated or text for departments & years
    eligibility_departments = StringField('Eligible Departments (Comma-separated or "All")', default='All', validators=[
        DataRequired(message='Please specify eligible departments or enter "All".')
    ])
    eligibility_years = StringField('Eligible Academic Years (Comma-separated or "All")', default='All', validators=[
        DataRequired(message='Please specify eligible academic years or enter "All".')
    ])
    
    schedule_json = TextAreaField('Visit Itinerary / Schedule (JSON format)', default='[]')
    important_instructions = TextAreaField('Important Instructions, Dress Code & Safety Norms', default='')
    status = SelectField('Publication Status', choices=VISIT_STATUS_CHOICES, default='published')
    
    submit = SubmitField('Save Industrial Visit')

    def validate_registration_deadline_date(self, field):
        """Ensures deadline date is not after visit date."""
        if self.visit_date.data and field.data:
            if field.data > self.visit_date.data:
                raise ValidationError('Registration deadline date cannot be after the visit date.')
