import json
from datetime import datetime
from app import db


class IndustrialVisit(db.Model):
    """Model representing an Industrial Visit organised for college students."""
    __tablename__ = 'industrial_visits'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    company_logo = db.Column(db.String(255), default='')
    cover_image = db.Column(db.String(255), default='')
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    meeting_point = db.Column(db.String(200), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=50)
    fee = db.Column(db.Float, nullable=False, default=0.0)
    registration_deadline = db.Column(db.DateTime, nullable=False)
    
    # Eligibility rules
    eligibility_departments = db.Column(db.Text, default='All', nullable=False)  # Comma separated or 'All'
    eligibility_years = db.Column(db.Text, default='All', nullable=False)  # Comma separated or 'All'
    
    # Schedule & Instructions
    schedule_json = db.Column(db.Text, default='[]', nullable=False)  # JSON array of timeline steps
    important_instructions = db.Column(db.Text, default='', nullable=True)
    
    # Status: 'draft', 'published', 'closed', 'cancelled', 'completed'
    status = db.Column(db.String(20), default='draft', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    registrations = db.relationship(
        'Registration',
        backref='visit',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @property
    def confirmed_registrations_count(self) -> int:
        """Returns the number of active/confirmed student registrations for this visit."""
        return self.registrations.filter_by(status='confirmed').count()

    @property
    def pending_registrations_count(self) -> int:
        """Returns the number of pending registrations."""
        return self.registrations.filter_by(status='pending').count()

    @property
    def available_seats(self) -> int:
        """Calculates remaining available capacity."""
        remaining = self.capacity - self.confirmed_registrations_count
        return max(0, remaining)

    @property
    def is_full(self) -> bool:
        """Checks if all seats have been filled."""
        return self.available_seats <= 0

    @property
    def is_almost_full(self) -> bool:
        """Checks if seats are critically low (<=20% of capacity)."""
        if self.is_full:
            return False
        threshold = max(1, int(self.capacity * 0.2))
        return self.available_seats <= threshold

    @property
    def is_past_deadline(self) -> bool:
        """Checks if current time is past the registration deadline."""
        return datetime.utcnow() > self.registration_deadline

    @property
    def dynamic_status(self) -> str:
        """Returns calculated status for public display."""
        if self.status == 'cancelled':
            return 'CANCELLED'
        if self.status == 'draft':
            return 'DRAFT'
        if self.status == 'completed':
            return 'COMPLETED'
        if self.status == 'closed' or self.is_past_deadline:
            return 'CLOSED'
        if self.is_full:
            return 'FULL'
        if self.is_almost_full:
            return 'ALMOST FULL'
        return 'OPEN'

    @property
    def status_badge_class(self) -> str:
        """Returns Bootstrap badge color class based on dynamic status."""
        status_map = {
            'OPEN': 'bg-success text-white',
            'ALMOST FULL': 'bg-warning text-dark',
            'FULL': 'bg-danger text-white',
            'CLOSED': 'bg-secondary text-white',
            'CANCELLED': 'bg-dark text-white',
            'DRAFT': 'bg-info text-dark',
            'COMPLETED': 'bg-primary text-white'
        }
        return status_map.get(self.dynamic_status, 'bg-secondary text-white')

    @property
    def parsed_schedule(self):
        """Returns parsed list of schedule items."""
        try:
            return json.loads(self.schedule_json) if self.schedule_json else []
        except Exception:
            return []

    def is_student_eligible(self, student) -> tuple[bool, str]:
        """Validates student's department and academic year against visit eligibility."""
        if not student:
            return False, "You must be logged in as a student to register."

        # Check Department
        if self.eligibility_departments and self.eligibility_departments.strip() != 'All':
            allowed_depts = [d.strip().lower() for d in self.eligibility_departments.split(',') if d.strip()]
            if student.department and student.department.strip().lower() not in allowed_depts:
                return False, f"This visit is open only to {self.eligibility_departments} students."

        # Check Year
        if self.eligibility_years and self.eligibility_years.strip() != 'All':
            allowed_years = [y.strip().lower() for y in self.eligibility_years.split(',') if y.strip()]
            if student.year and student.year.strip().lower() not in allowed_years:
                return False, f"This visit is open only to {self.eligibility_years} students."

        return True, "Eligible"

    def can_register(self, student=None) -> tuple[bool, str]:
        """Comprehensive check whether a new registration can be initiated."""
        if self.status != 'published':
            return False, f"This visit is not open for registration (Status: {self.status.capitalize()})."
        if self.is_past_deadline:
            return False, "The registration deadline for this visit has passed."
        if self.is_full:
            return False, "This industrial visit is completely full. No seats remaining."
        if student:
            eligible, reason = self.is_student_eligible(student)
            if not eligible:
                return False, reason
            # Check if student is already registered
            existing = self.registrations.filter_by(user_id=student.id).filter(
                Registration.status.in_(['confirmed', 'pending'])
            ).first()
            if existing:
                return False, "You have already registered for this industrial visit."
        return True, "Can register"

    def __repr__(self):
        return f"<IndustrialVisit #{self.id} {self.company_name} - {self.title}>"


# Avoid circular import by referencing Registration in method
from app.models.registration import Registration
