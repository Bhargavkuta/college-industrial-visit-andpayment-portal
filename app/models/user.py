from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """User model representing both Students and College Administrators."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=True, index=True)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(20), nullable=False)  # e.g., 'First Year', 'Second Year', 'Third Year', 'Final Year'
    division = db.Column(db.String(10), nullable=False)  # e.g., 'A', 'B', 'C'
    role = db.Column(db.String(20), default='student', nullable=False)  # 'student' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    registrations = db.relationship(
        'Registration',
        backref='student',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def set_password(self, password: str) -> None:
        """Hashes and sets the user's password using Werkzeug."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifies the password against the stored hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        """Returns True if the user has administrator privileges."""
        return self.role == 'admin'

    @property
    def is_student(self) -> bool:
        """Returns True if the user is a student."""
        return self.role == 'student'

    def get_id(self):
        """Flask-Login user ID."""
        return str(self.id)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
