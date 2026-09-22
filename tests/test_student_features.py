import pytest
from datetime import datetime, timedelta, time
from app.models.registration import Registration
from app.models.payment import Payment
from app.models.visit import IndustrialVisit


def test_student_dashboard_metrics(client, student_user, sample_visit, db):
    """Test student dashboard calculations and recommendations."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    reg = Registration(
        registration_id="IV-2026-DASH01",
        user_id=student_user.id,
        visit_id=sample_visit.id,
        status="confirmed",
        emergency_contact="Parent",
        emergency_phone="9811122233",
        terms_accepted=True
    )
    db.session.add(reg)
    db.session.flush()

    payment = Payment(
        registration_id=reg.id,
        razorpay_payment_id="pay_dash_1",
        amount=sample_visit.fee,
        currency="INR",
        status="successful",
        paid_at=datetime.utcnow()
    )
    db.session.add(payment)
    db.session.commit()

    response = client.get('/student/dashboard')
    assert response.status_code == 200
    assert b'Welcome back, Bhargav' in response.data
    assert b'My Registrations' in response.data


def test_student_registration_tabs(client, student_user, sample_visit, db):
    """Test tab filtering in student registrations view."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    reg = Registration(
        registration_id="IV-2026-TAB01",
        user_id=student_user.id,
        visit_id=sample_visit.id,
        status="confirmed",
        emergency_contact="Parent",
        emergency_phone="9811122233",
        terms_accepted=True
    )
    db.session.add(reg)
    db.session.commit()

    # All tab
    res_all = client.get('/student/registrations?tab=all')
    assert res_all.status_code == 200
    assert b'IV-2026-TAB01' in res_all.data

    # Upcoming tab
    res_up = client.get('/student/registrations?tab=upcoming')
    assert res_up.status_code == 200
    assert b'IV-2026-TAB01' in res_up.data

    # Completed tab
    res_comp = client.get('/student/registrations?tab=completed')
    assert res_comp.status_code == 200

    # Cancelled tab
    res_canc = client.get('/student/registrations?tab=cancelled')
    assert res_canc.status_code == 200


def test_student_view_receipt(client, student_user, sample_visit, db):
    """Test printable receipt page generation."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    reg = Registration(
        registration_id="IV-2026-RCPT01",
        user_id=student_user.id,
        visit_id=sample_visit.id,
        status="confirmed",
        emergency_contact="Parent",
        emergency_phone="9811122233",
        terms_accepted=True
    )
    db.session.add(reg)
    db.session.flush()

    payment = Payment(
        registration_id=reg.id,
        razorpay_payment_id="pay_rcpt_1",
        amount=sample_visit.fee,
        currency="INR",
        status="successful",
        paid_at=datetime.utcnow()
    )
    db.session.add(payment)
    db.session.commit()

    response = client.get(f'/student/registration/{reg.id}/receipt')
    assert response.status_code == 200
    assert b'Official Registration Voucher' in response.data
    assert b'IV-2026-RCPT01' in response.data
    assert student_user.full_name.encode() in response.data


def test_student_cancellation_flow(client, student_user, sample_visit, db):
    """Test student registration cancellation workflow."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    reg = Registration(
        registration_id="IV-2026-CANC01",
        user_id=student_user.id,
        visit_id=sample_visit.id,
        status="confirmed",
        emergency_contact="Parent",
        emergency_phone="9811122233",
        terms_accepted=True
    )
    db.session.add(reg)
    db.session.commit()

    # GET cancellation form
    get_res = client.get(f'/student/registration/{reg.id}/cancel')
    assert get_res.status_code == 200
    assert b'Cancel Registration' in get_res.data

    # POST cancellation
    post_res = client.post(f'/student/registration/{reg.id}/cancel', data={
        'cancellation_reason': 'Academic exam clash on the same day.'
    }, follow_redirects=True)

    assert post_res.status_code == 200
    assert reg.status == 'cancelled'
    assert reg.cancellation_reason == 'Academic exam clash on the same day.'


def test_free_visit_instant_confirmation(client, student_user, db):
    """Test that a free visit (fee == 0) confirms immediately without payment checkout."""
    now = datetime.utcnow()
    free_visit = IndustrialVisit(
        title="Complimentary Research Tour",
        company_name="National Innovation Lab",
        description="Free educational tour for college students.",
        location="Pune",
        meeting_point="Gate 1",
        visit_date=(now + timedelta(days=12)).date(),
        start_time=time(9, 0),
        end_time=time(17, 0),
        capacity=30,
        fee=0.0,
        registration_deadline=now + timedelta(days=8),
        eligibility_departments="All",
        eligibility_years="All",
        status="published"
    )
    db.session.add(free_visit)
    db.session.commit()

    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})
    response = client.post(f'/student/register-visit/{free_visit.id}', data={
        'emergency_contact': 'Parent',
        'emergency_phone': '9811122233',
        'terms_accepted': True
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Registration Confirmed' in response.data
    reg = Registration.query.filter_by(user_id=student_user.id, visit_id=free_visit.id).first()
    assert reg.status == 'confirmed'


def test_student_profile_update(client, student_user, db):
    """Test updating student profile contact details."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    response = client.post('/student/profile', data={
        'full_name': 'Bhargav S. Updated',
        'phone': '9899988877',
        'department': 'Information Technology',
        'year': 'Final Year',
        'division': 'B',
        'submit_profile': '1'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert student_user.full_name == 'Bhargav S. Updated'
    assert student_user.department == 'Information Technology'
    assert student_user.year == 'Final Year'


def test_student_change_password(client, student_user, db):
    """Test password update flow."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    response = client.post('/student/change-password', data={
        'current_password': 'Student@123',
        'new_password': 'BrandNewPassword@2026',
        'confirm_new_password': 'BrandNewPassword@2026'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert student_user.check_password('BrandNewPassword@2026') is True
