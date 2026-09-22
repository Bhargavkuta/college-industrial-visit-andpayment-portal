from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models.visit import IndustrialVisit
from app.models.registration import Registration
from app.models.payment import Payment
from app.forms.registration_forms import RegistrationStep1Form, CancelRegistrationForm
from app.forms.profile_forms import StudentProfileForm
from app.forms.auth_forms import ChangePasswordForm
from app.utils.decorators import student_required
from app.utils.helpers import generate_registration_id

student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard')
@student_required
def dashboard():
    """Student Dashboard with KPI metrics, upcoming itinerary, and recommendations."""
    now_date = datetime.utcnow().date()

    # 1. Total available published visits
    available_visits_count = IndustrialVisit.query.filter_by(status='published')\
        .filter(IndustrialVisit.visit_date >= now_date).count()

    # 2. Student's registrations
    my_registrations = Registration.query.filter_by(user_id=current_user.id)\
        .order_by(Registration.registered_at.desc()).all()
    total_registrations = len(my_registrations)

    # 3. Upcoming confirmed visit
    upcoming_registration = Registration.query.filter_by(user_id=current_user.id, status='confirmed')\
        .join(IndustrialVisit)\
        .filter(IndustrialVisit.visit_date >= now_date)\
        .order_by(IndustrialVisit.visit_date.asc())\
        .first()

    # 4. Total amount paid
    successful_payments = Payment.query.join(Registration)\
        .filter(Registration.user_id == current_user.id, Payment.status == 'successful')\
        .all()
    total_amount_paid = sum(p.amount for p in successful_payments)

    # 5. Recommended visits (matching student's department)
    recommended_visits = IndustrialVisit.query.filter_by(status='published')\
        .filter(IndustrialVisit.visit_date >= now_date)\
        .filter(
            or_(
                IndustrialVisit.eligibility_departments.ilike(f"%{current_user.department}%"),
                IndustrialVisit.eligibility_departments.ilike('%All%')
            )
        )\
        .order_by(IndustrialVisit.visit_date.asc())\
        .limit(3)\
        .all()

    # 6. College Announcements
    announcements = [
        {
            "title": "Industrial Visit Safety Guidelines 2026",
            "date": "01 Mar 2026",
            "content": "All students must carry physical college identity cards and follow the strict plant dress code on every official visit."
        },
        {
            "title": "Internship & PPO Opportunities via Industrial Visits",
            "date": "24 Feb 2026",
            "content": "Companies frequently shortlist candidates during Q&A sessions. Prepare technical questions beforehand."
        }
    ]

    return render_template(
        'student/dashboard.html',
        available_visits_count=available_visits_count,
        total_registrations=total_registrations,
        upcoming_registration=upcoming_registration,
        total_amount_paid=total_amount_paid,
        recommended_visits=recommended_visits,
        recent_registrations=my_registrations[:5],
        announcements=announcements
    )


@student_bp.route('/register-visit/<int:visit_id>', methods=['GET', 'POST'])
@student_required
def register_visit(visit_id):
    """
    Multi-step registration workflow for a student to book an industrial visit.
    Enforces capacity limits, deadlines, duplicate prevention, and eligibility.
    """
    visit = IndustrialVisit.query.get_or_404(visit_id)

    # Validate eligibility & capacity server-side
    can_reg, error_reason = visit.can_register(current_user)
    if not can_reg:
        flash(error_reason, 'danger')
        return redirect(url_for('main.visit_details', visit_id=visit.id))

    form = RegistrationStep1Form()
    if form.validate_on_submit():
        # Final server-side re-check before database insert
        can_reg_final, reason_final = visit.can_register(current_user)
        if not can_reg_final:
            flash(reason_final, 'danger')
            return redirect(url_for('main.visit_details', visit_id=visit.id))

        new_reg_id = generate_registration_id()
        
        # Free visit (fee == 0) gets confirmed immediately
        initial_status = 'confirmed' if visit.fee == 0 else 'pending'

        registration = Registration(
            registration_id=new_reg_id,
            user_id=current_user.id,
            visit_id=visit.id,
            status=initial_status,
            emergency_contact=form.emergency_contact.data.strip(),
            emergency_phone=form.emergency_phone.data.strip(),
            terms_accepted=True
        )

        try:
            db.session.add(registration)
            db.session.commit()

            if visit.fee == 0:
                # Create a 0.00 successful payment record
                zero_payment = Payment(
                    registration_id=registration.id,
                    amount=0.0,
                    currency='INR',
                    payment_method='Free Waiver',
                    status='successful',
                    paid_at=datetime.utcnow()
                )
                db.session.add(zero_payment)
                db.session.commit()
                flash('Registration successfully confirmed for this complimentary industrial visit!', 'success')
                return redirect(url_for('payment.payment_success', registration_id=registration.id))
            else:
                return redirect(url_for('payment.checkout', registration_id=registration.id))

        except Exception as e:
            db.session.rollback()
            flash('Failed to initiate registration. Please try again.', 'danger')
            return redirect(url_for('main.visit_details', visit_id=visit.id))

    return render_template('student/register_flow.html', visit=visit, form=form)


@student_bp.route('/registrations')
@student_required
def registrations():
    """Tabbed view of all student registrations (All, Upcoming, Completed, Cancelled)."""
    tab = request.args.get('tab', 'all')
    now_date = datetime.utcnow().date()

    base_query = Registration.query.filter_by(user_id=current_user.id).join(IndustrialVisit)

    if tab == 'upcoming':
        regs = base_query.filter(Registration.status == 'confirmed', IndustrialVisit.visit_date >= now_date)\
            .order_by(IndustrialVisit.visit_date.asc()).all()
    elif tab == 'completed':
        regs = base_query.filter(
            or_(Registration.status == 'completed', and_(Registration.status == 'confirmed', IndustrialVisit.visit_date < now_date))
        ).order_by(IndustrialVisit.visit_date.desc()).all()
    elif tab == 'cancelled':
        regs = base_query.filter(Registration.status == 'cancelled')\
            .order_by(Registration.registered_at.desc()).all()
    else:
        tab = 'all'
        regs = base_query.order_by(Registration.registered_at.desc()).all()

    return render_template('student/registrations.html', registrations=regs, active_tab=tab)


@student_bp.route('/registration/<int:reg_id>')
@student_required
def registration_detail(reg_id):
    """Detailed view of a single registration."""
    reg = Registration.query.filter_by(id=reg_id, user_id=current_user.id).first_or_404()
    return render_template('student/registration_detail.html', registration=reg)


@student_bp.route('/registration/<int:reg_id>/cancel', methods=['GET', 'POST'])
@student_required
def cancel_registration(reg_id):
    """Cancels an eligible student registration."""
    reg = Registration.query.filter_by(id=reg_id, user_id=current_user.id).first_or_404()

    can_cancel, reason = reg.can_be_cancelled()
    if not can_cancel:
        flash(reason, 'danger')
        return redirect(url_for('student.registrations'))

    form = CancelRegistrationForm()
    if form.validate_on_submit():
        reg.status = 'cancelled'
        reg.cancellation_reason = form.cancellation_reason.data.strip()
        reg.cancelled_at = datetime.utcnow()
        db.session.commit()
        flash(f'Registration {reg.registration_id} has been cancelled successfully.', 'success')
        return redirect(url_for('student.registrations'))

    return render_template('student/cancel_modal.html', registration=reg, form=form)


@student_bp.route('/registration/<int:reg_id>/receipt')
@student_required
def receipt(reg_id):
    """Generates clean printable receipt for confirmed registration."""
    reg = Registration.query.filter_by(id=reg_id, user_id=current_user.id).first_or_404()
    return render_template('student/receipt.html', registration=reg)


@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    """Allows student to view and update contact & profile information."""
    profile_form = StudentProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if 'submit_profile' in request.form and profile_form.validate_on_submit():
        current_user.full_name = profile_form.full_name.data.strip()
        current_user.phone = profile_form.phone.data.strip()
        current_user.department = profile_form.department.data
        current_user.year = profile_form.year.data
        current_user.division = profile_form.division.data
        db.session.commit()
        flash('Your profile details have been updated successfully.', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html', profile_form=profile_form, password_form=password_form)


@student_bp.route('/change-password', methods=['POST'])
@student_required
def change_password():
    """Handles password update for authenticated students."""
    password_form = ChangePasswordForm()
    profile_form = StudentProfileForm(obj=current_user)

    if password_form.validate_on_submit():
        if not current_user.check_password(password_form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('student/profile.html', profile_form=profile_form, password_form=password_form)

        current_user.set_password(password_form.new_password.data)
        db.session.commit()
        flash('Your password has been changed successfully.', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html', profile_form=profile_form, password_form=password_form)


from sqlalchemy import and_
