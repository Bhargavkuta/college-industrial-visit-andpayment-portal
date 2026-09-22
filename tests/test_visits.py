import pytest
from datetime import datetime, timedelta, date, time
from app.models.visit import IndustrialVisit


def test_admin_can_create_visit(client, admin_user, db):
    """Test admin creation of an industrial visit."""
    client.post('/auth/login', data={'email': admin_user.email, 'password': 'Admin@123'})

    now = datetime.utcnow()
    response = client.post('/admin/visits/create', data={
        'title': 'Robotics and Electric Mobility Tour',
        'company_name': 'Mahindra Electric',
        'company_logo': 'https://example.com/logo.png',
        'cover_image': 'https://example.com/cover.png',
        'description': 'Interactive tour of electric vehicle assembly and battery testing facilities.',
        'location': 'Mahindra Plant, Chakan, Pune',
        'meeting_point': 'Campus Bus Bay 2',
        'visit_date': (now + timedelta(days=20)).strftime('%Y-%m-%d'),
        'start_time': '08:00',
        'end_time': '17:00',
        'capacity': 40,
        'fee': 450.0,
        'registration_deadline_date': (now + timedelta(days=15)).strftime('%Y-%m-%d'),
        'registration_deadline_time': '23:59',
        'eligibility_departments': 'Mechanical Engineering, Electrical Engineering',
        'eligibility_years': 'Third Year, Final Year',
        'schedule_json': '[]',
        'important_instructions': 'Carry ID card.',
        'status': 'published'
    }, follow_redirects=True)

    assert response.status_code == 200
    visit = IndustrialVisit.query.filter_by(company_name='Mahindra Electric').first()
    assert visit is not None
    assert visit.capacity == 40
    assert visit.fee == 450.0
    assert visit.status == 'published'


def test_admin_can_edit_visit(client, admin_user, sample_visit):
    """Test updating an existing industrial visit."""
    client.post('/auth/login', data={'email': admin_user.email, 'password': 'Admin@123'})

    response = client.post(f'/admin/visits/{sample_visit.id}/edit', data={
        'title': 'Updated Title For Tata Tour',
        'company_name': sample_visit.company_name,
        'company_logo': sample_visit.company_logo,
        'cover_image': sample_visit.cover_image,
        'description': 'Updated description with new details for the plant walkthrough.',
        'location': sample_visit.location,
        'meeting_point': sample_visit.meeting_point,
        'visit_date': sample_visit.visit_date.strftime('%Y-%m-%d'),
        'start_time': '09:00',
        'end_time': '18:00',
        'capacity': 60,
        'fee': 600.0,
        'registration_deadline_date': sample_visit.registration_deadline.strftime('%Y-%m-%d'),
        'registration_deadline_time': '23:59',
        'eligibility_departments': 'All',
        'eligibility_years': 'All',
        'schedule_json': '[]',
        'important_instructions': 'Updated instructions.',
        'status': 'published'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert sample_visit.capacity == 60
    assert sample_visit.title == 'Updated Title For Tata Tour'
    assert sample_visit.fee == 600.0


def test_admin_can_delete_visit(client, admin_user, db):
    """Test deleting an unbooked visit."""
    client.post('/auth/login', data={'email': admin_user.email, 'password': 'Admin@123'})

    now = datetime.utcnow()
    draft_visit = IndustrialVisit(
        title="Temporary Visit",
        company_name="Temp Corp",
        description="To be deleted soon.",
        location="Pune",
        meeting_point="Gate 1",
        visit_date=(now + timedelta(days=5)).date(),
        start_time=time(9, 0),
        end_time=time(17, 0),
        capacity=10,
        fee=0.0,
        registration_deadline=now + timedelta(days=2),
        status="draft"
    )
    db.session.add(draft_visit)
    db.session.commit()

    visit_id = draft_visit.id
    response = client.post(f'/admin/visits/{visit_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert IndustrialVisit.query.get(visit_id) is None


def test_student_can_view_published_visit(client, sample_visit):
    """Test public and student access to published visit catalog and details."""
    response = client.get('/visits')
    assert response.status_code == 200
    assert sample_visit.company_name.encode() in response.data

    detail_resp = client.get(f'/visits/{sample_visit.id}')
    assert detail_resp.status_code == 200
    assert sample_visit.company_name.encode() in detail_resp.data
    assert b'Automated Plant' in detail_resp.data


def test_draft_visit_not_visible_to_students(client, db):
    """Ensure draft visits are hidden from the public visit list and return 404 to students."""
    now = datetime.utcnow()
    draft_visit = IndustrialVisit(
        title="Secret Draft Visit",
        company_name="Secret Corp",
        description="Top secret plant.",
        location="Secret Location",
        meeting_point="Gate X",
        visit_date=(now + timedelta(days=30)).date(),
        start_time=time(9, 0),
        end_time=time(17, 0),
        capacity=20,
        fee=100.0,
        registration_deadline=now + timedelta(days=20),
        status="draft"
    )
    db.session.add(draft_visit)
    db.session.commit()

    # Public list should NOT show draft
    resp = client.get('/visits')
    assert b'Secret Draft Visit' not in resp.data

    # Direct access by non-admin returns 404
    detail_resp = client.get(f'/visits/{draft_visit.id}')
    assert detail_resp.status_code == 404


def test_cancelled_visit_cannot_be_registered_for(client, student_user, sample_visit, db):
    """Ensure cancelled visits clearly show cancelled status and disallow registration."""
    sample_visit.status = 'cancelled'
    db.session.commit()

    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    # Attempt registration
    response = client.post(f'/student/register-visit/{sample_visit.id}', data={
        'emergency_contact': 'Father',
        'emergency_phone': '9876543210',
        'terms_accepted': True
    }, follow_redirects=True)

    assert b'not open for registration' in response.data.lower() or b'cancelled' in response.data.lower()
