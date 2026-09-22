import os
from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config_by_name, Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

# Configure Flask-Login
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please sign in to access this page.'
login_manager.login_message_category = 'warning'


def create_app(config_name=None) -> Flask:
    """Application factory creating and configuring the Flask application."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # User loader callback for Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Jinja2 Context Processors
    @app.context_processor
    def inject_global_template_vars():
        return {
            'now': datetime.utcnow(),
            'current_year': datetime.utcnow().year,
            'college_name': app.config.get('COLLEGE_NAME', 'Pillai School of Engineering'),
            'college_code': app.config.get('COLLEGE_CODE', 'PSE'),
            'college_email': app.config.get('COLLEGE_EMAIL', 'support@pillai.edu'),
            'is_mock_payment_mode': Config.is_mock_payment_mode(),
            'razorpay_key_id': app.config.get('RAZORPAY_KEY_ID', '')
        }

    # Register custom Jinja filters
    @app.template_filter('format_inr')
    def format_inr_filter(value):
        try:
            return f"₹{float(value):,.2f}"
        except (ValueError, TypeError):
            return "₹0.00"

    @app.template_filter('format_date')
    def format_date_filter(dt, fmt='%d %b %Y'):
        if not dt:
            return 'N/A'
        try:
            return dt.strftime(fmt)
        except Exception:
            return str(dt)

    @app.template_filter('format_time')
    def format_time_filter(t, fmt='%I:%M %p'):
        if not t:
            return 'N/A'
        try:
            return t.strftime(fmt)
        except Exception:
            return str(t)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.student import student_bp
    from app.routes.admin import admin_bp
    from app.routes.payment import payment_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(payment_bp, url_prefix='/payment')

    # Register Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html', error=error), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html', error=error), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html', error=error), 500

    # Ensure database tables exist automatically on startup in development
    with app.app_context():
        db.create_all()

    return app
