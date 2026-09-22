import os
import pytest
from datetime import datetime, timedelta, date, time
from app import create_app, db as _db
from app.models.user import User
from app.models.visit import IndustrialVisit
from app.models.registration import Registration
from app.models.payment import Payment


@pytest.fixture(scope='session')
def app():
    """Create and configure testing Flask application."""
    app = create_app('testing')
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key-123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    return app


@pytest.fixture(scope='function')
def db(app):
    """Provide a clean database for each test function."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    """Test client fixture."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner fixture."""
    return app.test_cli_runner()


@pytest.fixture
def admin_user(app, db):
    """Create an administrator user."""
    admin = User(
        full_name="Admin Coordinator",
        email="admin@college.edu",
        phone="+91 98765 43210",
        roll_number="STAFF-01",
        department="Industry Relations",
        year="Staff",
        division="A",
        role="admin",
        is_active=True
    )
    admin.set_password("Admin@123")
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def student_user(app, db):
    """Create a standard student user."""
    student = User(
        full_name="Bhargav Sharma",
        email="student@college.edu",
        phone="+91 98234 56789",
        roll_number="CS2026-042",
        department="Computer Engineering",
        year="Third Year",
        division="A",
        role="student",
        is_active=True
    )
    student.set_password("Student@123")
    db.session.add(student)
    db.session.commit()
    return student


@pytest.fixture
def mechanical_student(app, db):
    """Create a mechanical engineering student user."""
    mech_student = User(
        full_name="Rohan Mech",
        email="rohan@college.edu",
        phone="+91 98111 22233",
        roll_number="ME2026-015",
        department="Mechanical Engineering",
        year="Second Year",
        division="B",
        role="student",
        is_active=True
    )
    mech_student.set_password("Student@123")
    db.session.add(mech_student)
    db.session.commit()
    return mech_student


@pytest.fixture
def sample_visit(app, db):
    """Create a published upcoming industrial visit."""
    now = datetime.utcnow()
    visit = IndustrialVisit(
        title="Automated Plant & AI Lab Tour",
        company_name="Tata Motors Ltd.",
        company_logo="https://example.com/tata.png",
        cover_image="https://example.com/cover.jpg",
        description="Comprehensive plant tour and robotics assembly walkthrough.",
        location="Tata Motors Pimpri Works, Pune",
        meeting_point="College Gate 1",
        visit_date=(now + timedelta(days=15)).date(),
        start_time=time(8, 0),
        end_time=time(17, 0),
        capacity=50,
        fee=500.0,
        registration_deadline=now + timedelta(days=10),
        eligibility_departments="Computer Engineering, Information Technology",
        eligibility_years="Third Year, Final Year",
        schedule_json='[{"time": "08:00 AM", "activity": "Assembly", "description": "Bus departure"}]',
        important_instructions="Formal dress code and leather safety shoes mandatory.",
        status="published"
    )
    db.session.add(visit)
    db.session.commit()
    return visit
