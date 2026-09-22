import pytest
from datetime import datetime
from app.models.registration import Registration
from app.models.payment import Payment


def test_payment_order_creation(client, student_user, sample_visit, db):
    """Test payment checkout order creation."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    # Create pending registration
    reg = Registration(
        registration_id="IV-2026-112233",
        user_id=student_user.id,
        visit_id=sample_visit.id,
        status="pending",
        emergency_contact="Parent",
        emergency_phone="9811122233",
        terms_accepted=True
    )
    db.session.add(reg)
    db.session.commit()

    # Load checkout page
    response = client.get(f'/payment/checkout/{reg.id}')
    assert response.status_code == 200
    assert b'Registration Payment' in response.data
    assert reg.registration_id.encode() in response.data

    # Check that payment record was created
    payment = reg.latest_payment
    assert payment is not None
    assert payment.amount == sample_visit.fee
    assert payment.status == 'created'


def test_successful_payment_confirms_registration(client, student_user, sample_visit, db):
    """Test successful mock payment confirmation flow."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    reg = Registration(
        registration_id="IV-2026-554433",
        user_id=student_user.id,
        visit_id=sample_visit.id,
        status="pending",
        emergency_contact="Parent",
        emergency_phone="9811122233",
        terms_accepted=True
    )
    db.session.add(reg)
    db.session.commit()

    # Simulate success
    response = client.post('/payment/mock-process', data={
        'registration_id': reg.id,
        'simulate_status': 'success',
        'payment_method': 'DevMock UPI'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Registration Confirmed' in response.data
    assert reg.status == 'confirmed'

    payment = reg.latest_payment
    assert payment.status == 'successful'
    assert payment.razorpay_payment_id.startswith('pay_mock_')
    assert payment.paid_at is not None


def test_failed_payment_does_not_confirm_registration(client, student_user, sample_visit, db):
    """Test failed payment keeps registration in pending/unconfirmed state."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    reg = Registration(
        registration_id="IV-2026-667788",
        user_id=student_user.id,
        visit_id=sample_visit.id,
        status="pending",
        emergency_contact="Parent",
        emergency_phone="9811122233",
        terms_accepted=True
    )
    db.session.add(reg)
    db.session.commit()

    # Simulate failure
    response = client.post('/payment/mock-process', data={
        'registration_id': reg.id,
        'simulate_status': 'failure',
        'payment_method': 'DevMock Card'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Payment Unsuccessful' in response.data
    assert reg.status == 'pending'  # NOT confirmed!

    payment = reg.latest_payment
    assert payment.status == 'failed'


def test_invalid_payment_signature_rejected(client, student_user, sample_visit, db):
    """Ensure invalid signature verification sets payment status to failed and prevents confirmation."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    reg = Registration(
        registration_id="IV-2026-990011",
        user_id=student_user.id,
        visit_id=sample_visit.id,
        status="pending",
        emergency_contact="Parent",
        emergency_phone="9811122233",
        terms_accepted=True
    )
    db.session.add(reg)
    db.session.commit()

    # Create payment
    payment = Payment(
        registration_id=reg.id,
        razorpay_order_id="order_fake_123",
        amount=sample_visit.fee,
        currency="INR",
        status="created"
    )
    db.session.add(payment)
    db.session.commit()

    # Submit fake/invalid signature
    response = client.post('/payment/verify', data={
        'registration_id': reg.id,
        'razorpay_order_id': 'order_fake_123',
        'razorpay_payment_id': 'pay_fake_456',
        'razorpay_signature': 'invalid_forged_signature_hash'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Payment Unsuccessful' in response.data or b'failed' in response.data.lower()
    assert reg.status == 'pending'
    assert payment.status == 'failed'


def test_payment_amount_validation(client, student_user, sample_visit, db):
    """Verify that payment amount matches visit fee accurately."""
    client.post('/auth/login', data={'email': student_user.email, 'password': 'Student@123'})

    reg = Registration(
        registration_id="IV-2026-778899",
        user_id=student_user.id,
        visit_id=sample_visit.id,
        status="pending",
        emergency_contact="Parent",
        emergency_phone="9811122233",
        terms_accepted=True
    )
    db.session.add(reg)
    db.session.commit()

    # Load checkout
    client.get(f'/payment/checkout/{reg.id}')
    payment = reg.latest_payment
    assert payment.amount == sample_visit.fee
    assert payment.formatted_amount == f"₹{sample_visit.fee:,.2f}"
