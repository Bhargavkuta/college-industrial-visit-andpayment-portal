import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
basedir = Path(__file__).resolve().parent
load_dotenv(basedir / '.env')


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-college-portal-super-secret-key-2026')
    
    # College Metadata
    COLLEGE_NAME = os.environ.get('COLLEGE_NAME', 'Pillai School of Engineering')
    COLLEGE_CODE = os.environ.get('COLLEGE_CODE', 'PSE')
    COLLEGE_EMAIL = os.environ.get('COLLEGE_EMAIL', 'support@pillai.edu')
    
    # SQLAlchemy configuration
    # Default to instance/portal.db in absolute path
    INSTANCE_DIR = basedir / 'instance'
    INSTANCE_DIR.mkdir(exist_ok=True)
    
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{INSTANCE_DIR / "portal.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No strict timeout for student registration forms
    
    # Razorpay Payment Gateway settings
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '').strip()
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '').strip()
    RAZORPAY_CURRENCY = os.environ.get('RAZORPAY_CURRENCY', 'INR').strip()
    
    @classmethod
    def is_mock_payment_mode(cls):
        """Returns True if Razorpay live/test keys are not provided or set to mock values."""
        key_id = cls.RAZORPAY_KEY_ID or os.environ.get('RAZORPAY_KEY_ID', '').strip()
        key_secret = cls.RAZORPAY_KEY_SECRET or os.environ.get('RAZORPAY_KEY_SECRET', '').strip()
        return not (key_id and key_secret and len(key_id) > 5 and len(key_secret) > 5)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration with in-memory or dedicated test sqlite db."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF in tests for clean form submissions
    SERVER_NAME = 'localhost.localdomain'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Enable over HTTPS in production


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
