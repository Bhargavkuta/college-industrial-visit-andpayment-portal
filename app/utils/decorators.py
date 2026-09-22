from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user


def role_required(required_role: str):
    """Decorator to restrict access to users with a specific role ('admin' or 'student')."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for('auth.login', next=request.url))
            
            if current_user.role != required_role:
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator requiring administrative role."""
    return role_required('admin')(f)


def student_required(f):
    """Decorator requiring student role."""
    return role_required('student')(f)
