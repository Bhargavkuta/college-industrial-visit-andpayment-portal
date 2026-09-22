import pytest
from datetime import datetime, timedelta, time
from app.models.registration import Registration
from app.models.visit import IndustrialVisit
from app.models.user import User


def test_student_can_register(client, student_user, sample_visit, db):
    """Test standard student registration initiation."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    response = client.post(f'/student/register-visit/{sample_visit.id}', data={
        'emergency_contact': 'Ramesh Sharma (Father)',
        'emergency_phone': '9811122233',
        'terms_accepted': True
    }, follow_redirects=True)

    assert response.status_code == 200
    reg = Registration.query.filter_by(user_id=student_user.id, visit_id=sample_visit.id).first()
    assert reg is not None
    assert reg.status == 'pending'
    assert reg.registration_id.startswith('IV-')
    assert reg.emergency_contact == 'Ramesh Sharma (Father)'


def test_duplicate_registration_rejected(client, student_user, sample_visit, db):
    """Ensure student cannot register for the same visit twice."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    # First registration
    client.post(f'/student/register-visit/{sample_visit.id}', data={
        'emergency_contact': 'Parent',
        'emergency_phone': '9811122233',
        'terms_accepted': True
    })

    # Second registration attempt
    response = client.post(f'/student/register-visit/{sample_visit.id}', data={
        'emergency_contact': 'Parent',
        'emergency_phone': '9811122233',
        'terms_accepted': True
    }, follow_redirects=True)

    assert b'already registered' in response.data.lower()
    # Ensure only 1 record exists
    count = Registration.query.filter_by(user_id=student_user.id, visit_id=sample_visit.id).count()
    assert count == 1


def test_full_visit_rejects_registration(client, student_user, db):
    """Ensure registration is rejected when capacity is full (available seats = 0)."""
    now = datetime.utcnow()
    # Create visit with capacity = 1
    tiny_visit = IndustrialVisit(
        title="Exclusive Micro Tour",
        company_name="Micro Tech",
        description="Only 1 seat available.",
        location="Pune",
        meeting_point="Gate 1",
        visit_date=(now + timedelta(days=10)).date(),
        start_time=time(9, 0),
        end_time=time(17, 0),
        capacity=1,
        fee=200.0,
        registration_deadline=now + timedelta(days=5),
        eligibility_departments="All",
        eligibility_years="All",
        status="published"
    )
    db.session.add(tiny_visit)
    db.session.commit()

    # Create another student who takes the only seat and is confirmed
    other_student = User(
        full_name="Other Student",
        email="other@college.edu",
        phone="9876543210",
        roll_number="OT-001",
        department="Computer Engineering",
        year="Third Year",
        division="A",
        role="student"
    )
    other_student.set_password("Student@123")
    db.session.add(other_student)
    db.session.commit()

    reg1 = Registration(
        registration_id="IV-2026-999001",
        user_id=other_student.id,
        visit_id=tiny_visit.id,
        status="confirmed",
        emergency_contact="Parent",
        emergency_phone="9876543210",
        terms_accepted=True
    )
    db.session.add(reg1)
    db.session.commit()

    # Verify visit is full
    assert tiny_visit.is_full is True
    assert tiny_visit.available_seats == 0

    # Main student attempts to register
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})
    response = client.post(f'/student/register-visit/{tiny_visit.id}', data={
        'emergency_contact': 'Parent',
        'emergency_phone': '9811122233',
        'terms_accepted': True
    }, follow_redirects=True)

    assert b'completely full' in response.data.lower() or b'no seats' in response.data.lower()
    # Ensure no second registration created
    assert tiny_visit.registrations.count() == 1


def test_registration_after_deadline_rejected(client, student_user, db):
    """Ensure registration is rejected when deadline has passed."""
    now = datetime.utcnow()
    expired_visit = IndustrialVisit(
        title="Expired Tour",
        company_name="Expired Tech",
        description="Deadline has already passed.",
        location="Pune",
        meeting_point="Gate 1",
        visit_date=(now + timedelta(days=2)).date(),
        start_time=time(9, 0),
        end_time=time(17, 0),
        capacity=50,
        fee=200.0,
        registration_deadline=now - timedelta(days=1),  # in the past!
        eligibility_departments="All",
        eligibility_years="All",
        status="published"
    )
    db.session.add(expired_visit)
    db.session.commit()

    assert expired_visit.is_past_deadline is True

    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})
    response = client.post(f'/student/register-visit/{expired_visit.id}', data={
        'emergency_contact': 'Parent',
        'emergency_phone': '9811122233',
        'terms_accepted': True
    }, follow_redirects=True)

    assert b'deadline' in response.data.lower()
    assert expired_visit.registrations.count() == 0


def test_ineligible_department_rejected(client, mechanical_student, sample_visit):
    """Ensure student from ineligible branch is rejected (sample_visit is for Computer/IT only)."""
    client.post('/auth/login', data={'email': mechanical_student.email, 'password': 'Student@123'})

    response = client.post(f'/student/register-visit/{sample_visit.id}', data={
        'emergency_contact': 'Parent',
        'emergency_phone': '9811122233',
        'terms_accepted': True
    }, follow_redirects=True)

    assert b'open only to' in response.data.lower() or b'eligible' in response.data.lower()
    assert sample_visit.registrations.count() == 0


def test_ineligible_year_rejected(client, db, sample_visit):
    """Ensure student in ineligible year is rejected."""
    first_year_student = User(
        full_name="Freshman Student",
        email="freshman@college.edu",
        phone="9876543210",
        roll_number="FE-2026-001",
        department="Computer Engineering",
        year="First Year",  # sample_visit requires Third Year / Final Year
        division="A",
        role="student"
    )
    first_year_student.set_password("Student@123")
    db.session.add(first_year_student)
    db.session.commit()

    client.post('/auth/login', data={'email': first_year_student.email, 'password': 'Student@123'})
    response = client.post(f'/student/register-visit/{sample_visit.id}', data={
        'emergency_contact': 'Parent',
        'emergency_phone': '9811122233',
        'terms_accepted': True
    }, follow_redirects=True)

    assert b'open only to' in response.data.lower() or b'eligible' in response.data.lower()
    assert sample_visit.registrations.count() == 0


def test_registration_generates_unique_id(client, student_user, sample_visit, db):
    """Verify unique human-readable registration IDs generated in standard format."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    client.post(f'/student/register-visit/{sample_visit.id}', data={
        'emergency_contact': 'Parent',
        'emergency_phone': '9811122233',
        'terms_accepted': True
    })

    reg = Registration.query.filter_by(user_id=student_user.id).first()
    assert reg is not None
    # Check format: IV-YYYY-XXXXXX
    parts = reg.registration_id.split('-')
    assert len(parts) == 3
    assert parts[0] == 'IV'
    assert len(parts[1]) == 4  # e.g. 2026
    assert len(parts[2]) == 6  # e.g. 104829
