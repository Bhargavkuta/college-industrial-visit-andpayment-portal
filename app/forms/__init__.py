from app.forms.auth_forms import StudentRegistrationForm, LoginForm, ChangePasswordForm, DEPARTMENTS, YEARS, DIVISIONS
from app.forms.visit_forms import VisitForm, VISIT_STATUS_CHOICES
from app.forms.registration_forms import RegistrationStep1Form, CancelRegistrationForm
from app.forms.profile_forms import StudentProfileForm

__all__ = [
    'StudentRegistrationForm',
    'LoginForm',
    'ChangePasswordForm',
    'VisitForm',
    'VISIT_STATUS_CHOICES',
    'RegistrationStep1Form',
    'CancelRegistrationForm',
    'StudentProfileForm',
    'DEPARTMENTS',
    'YEARS',
    'DIVISIONS'
]
