from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.student import student_bp
from app.routes.admin import admin_bp
from app.routes.payment import payment_bp

__all__ = ['auth_bp', 'main_bp', 'student_bp', 'admin_bp', 'payment_bp']
