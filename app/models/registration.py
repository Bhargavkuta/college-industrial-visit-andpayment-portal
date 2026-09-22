from datetime import datetime
from app import db


class Registration(db.Model):
    """Model tracking student registrations for Industrial Visits."""
    __tablename__ = 'registrations'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'visit_id', name='uq_user_visit_registration'),
    )

    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('industrial_visits.id', ondelete='CASCADE'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Status: 'pending', 'confirmed', 'cancelled', 'completed'
    status = db.Column(db.String(20), default='pending', nullable=False)
    
    emergency_contact = db.Column(db.String(100), nullable=False)
    emergency_phone = db.Column(db.String(20), nullable=False)
    terms_accepted = db.Column(db.Boolean, default=True, nullable=False)
    
    cancellation_reason = db.Column(db.Text, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    payments = db.relationship(
        'Payment',
        backref='registration',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @property
    def latest_payment(self):
        """Returns the most recent payment record."""
        return self.payments.order_by(db.desc('created_at')).first()

    @property
    def is_paid(self) -> bool:
        """Returns True if at least one payment was successful."""
        return self.payments.filter_by(status='successful').count() > 0

    @property
    def status_badge_class(self) -> str:
        """Returns Bootstrap badge color class based on registration status."""
        status_map = {
            'confirmed': 'bg-success text-white',
            'pending': 'bg-warning text-dark',
            'cancelled': 'bg-danger text-white',
            'completed': 'bg-primary text-white'
        }
        return status_map.get(self.status, 'bg-secondary text-white')

    def can_be_cancelled(self) -> tuple[bool, str]:
        """Checks whether the student can cancel this registration."""
        if self.status == 'cancelled':
            return False, "This registration is already cancelled."
        if self.status == 'completed':
            return False, "Completed visits cannot be cancelled."
        
        # Check if visit date is in future
        if self.visit and self.visit.visit_date <= datetime.utcnow().date():
            return False, "Registrations cannot be cancelled on or after the visit date."

        return True, "Cancellation allowed"

    def __repr__(self):
        return f"<Registration {self.registration_id} (User: {self.user_id}, Visit: {self.visit_id}, Status: {self.status})>"
