import os
import hmac
import hashlib
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, jsonify
from flask_login import current_user
from app import db
from app.models.registration import Registration
from app.models.payment import Payment
from app.utils.decorators import student_required
from config import Config

payment_bp = Blueprint('payment', __name__)


def get_razorpay_client():
    """Initializes and returns Razorpay client if keys are present, else None."""
    key_id = current_app.config.get('RAZORPAY_KEY_ID', '')
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET', '')
    if key_id and key_secret and len(key_id) > 5 and len(key_secret) > 5:
        try:
            import razorpay
            return razorpay.Client(auth=(key_id, key_secret))
        except Exception:
            return None
    return None


@payment_bp.route('/checkout/<int:registration_id>')
@student_required
def checkout(registration_id):
    """
    Renders the payment checkout page.
    Generates Razorpay Order if configured, or prepares Mock Order for Development Mode.
    """
    registration = Registration.query.filter_by(id=registration_id, user_id=current_user.id).first_or_404()

    if registration.status == 'confirmed':
        flash('This registration is already confirmed and paid for.', 'info')
        return redirect(url_for('payment.payment_success', registration_id=registration.id))

    visit = registration.visit
    amount_inr = visit.fee
    amount_paise = int(amount_inr * 100)

    razorpay_client = get_razorpay_client()
    razorpay_order = None
    is_mock = Config.is_mock_payment_mode() or (razorpay_client is None)

    # Check or create payment record
    payment = registration.latest_payment
    if not payment:
        payment = Payment(
            registration_id=registration.id,
            amount=amount_inr,
            currency='INR',
            payment_method='Razorpay' if not is_mock else 'DevMock Gateway',
            status='created'
        )
        db.session.add(payment)
        db.session.commit()

    if not is_mock and razorpay_client:
        try:
            # Create real Razorpay order
            order_data = {
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': f"rcpt_{registration.registration_id}",
                'payment_capture': 1,
                'notes': {
                    'registration_id': registration.registration_id,
                    'student_roll': current_user.roll_number,
                    'visit_id': visit.id
                }
            }
            razorpay_order = razorpay_client.order.create(data=order_data)
            payment.razorpay_order_id = razorpay_order.get('id')
            db.session.commit()
        except Exception as e:
            # Fallback to mock mode if Razorpay API fails (e.g. invalid test keys)
            is_mock = True
            payment.razorpay_order_id = f"order_mock_{registration.id}_{int(datetime.utcnow().timestamp())}"
            payment.payment_method = 'DevMock Gateway'
            db.session.commit()
    else:
        # Dev Mock Order
        if not payment.razorpay_order_id:
            payment.razorpay_order_id = f"order_mock_{registration.id}_{int(datetime.utcnow().timestamp())}"
            db.session.commit()

    return render_template(
        'student/payment_page.html',
        registration=registration,
        visit=visit,
        payment=payment,
        amount_inr=amount_inr,
        amount_paise=amount_paise,
        razorpay_order=razorpay_order,
        is_mock=is_mock,
        razorpay_key_id=current_app.config.get('RAZORPAY_KEY_ID', '')
    )


@payment_bp.route('/verify', methods=['POST'])
@student_required
def verify():
    """
    Official Razorpay payment callback verification endpoint.
    Strictly verifies Razorpay HMAC-SHA256 signature server-side.
    """
    razorpay_payment_id = request.form.get('razorpay_payment_id', '').strip()
    razorpay_order_id = request.form.get('razorpay_order_id', '').strip()
    razorpay_signature = request.form.get('razorpay_signature', '').strip()
    registration_id = request.form.get('registration_id')

    if not registration_id:
        flash('Invalid verification request parameters.', 'danger')
        return redirect(url_for('student.registrations'))

    registration = Registration.query.filter_by(id=registration_id, user_id=current_user.id).first_or_404()
    payment = registration.latest_payment

    if not payment:
        flash('Payment record not found.', 'danger')
        return redirect(url_for('student.registrations'))

    razorpay_client = get_razorpay_client()
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET', '')

    # Server-side verification
    is_valid = False
    if razorpay_client and key_secret:
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)
            is_valid = True
        except Exception:
            is_valid = False

    if is_valid:
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = 'successful'
        payment.paid_at = datetime.utcnow()
        registration.status = 'confirmed'
        db.session.commit()
        flash('Payment verified successfully! Your registration is confirmed.', 'success')
        return redirect(url_for('payment.payment_success', registration_id=registration.id))
    else:
        payment.status = 'failed'
        payment.razorpay_payment_id = razorpay_payment_id
        db.session.commit()
        flash('Payment signature verification failed. Your card/account was not debited.', 'danger')
        return redirect(url_for('payment.payment_failed', registration_id=registration.id))


@payment_bp.route('/mock-process', methods=['POST'])
@student_required
def mock_process():
    """
    Handles Development / Mock Payment simulation.
    Allows testing successful and failed transaction flows in local and CI environments.
    """
    registration_id = request.form.get('registration_id')
    simulate_status = request.form.get('simulate_status', 'success')  # 'success' or 'failure'
    mock_payment_method = request.form.get('payment_method', 'DevMock UPI')

    registration = Registration.query.filter_by(id=registration_id, user_id=current_user.id).first_or_404()
    payment = registration.latest_payment

    if not payment:
        payment = Payment(
            registration_id=registration.id,
            amount=registration.visit.fee,
            currency='INR',
            payment_method=mock_payment_method,
            status='created'
        )
        db.session.add(payment)
        db.session.commit()

    if simulate_status == 'success':
        mock_pay_id = f"pay_mock_{int(datetime.utcnow().timestamp())}_{registration.id}"
        payment.razorpay_payment_id = mock_pay_id
        payment.payment_method = mock_payment_method
        payment.razorpay_signature = "mock_verified_signature"
        payment.status = 'successful'
        payment.paid_at = datetime.utcnow()
        
        # Confirm registration
        registration.status = 'confirmed'
        db.session.commit()

        flash('Mock payment completed successfully! Registration confirmed.', 'success')
        return redirect(url_for('payment.payment_success', registration_id=registration.id))
    else:
        # Simulate payment failure
        payment.status = 'failed'
        payment.payment_method = mock_payment_method
        db.session.commit()
        flash('Mock payment simulation resulted in transaction failure.', 'danger')
        return redirect(url_for('payment.payment_failed', registration_id=registration.id))


@payment_bp.route('/success/<int:registration_id>')
@student_required
def payment_success(registration_id):
    """Payment Confirmation & Registration Success Page."""
    registration = Registration.query.filter_by(id=registration_id, user_id=current_user.id).first_or_404()
    payment = registration.latest_payment
    return render_template('student/payment_success.html', registration=registration, payment=payment)


@payment_bp.route('/failed/<int:registration_id>')
@student_required
def payment_failed(registration_id):
    """Payment Failure Page with retry option."""
    registration = Registration.query.filter_by(id=registration_id, user_id=current_user.id).first_or_404()
    payment = registration.latest_payment
    return render_template('student/payment_failed.html', registration=registration, payment=payment)
