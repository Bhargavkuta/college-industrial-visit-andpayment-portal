import json
from datetime import datetime, date, time
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, Response, send_file
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, func
from app import db
from app.models.user import User
from app.models.visit import IndustrialVisit
from app.models.registration import Registration
from app.models.payment import Payment
from app.forms.visit_forms import VisitForm
from app.utils.decorators import admin_required
from app.utils.export import generate_registrations_csv, generate_registrations_excel
from app.utils.seed import seed_database

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin Dashboard with comprehensive KPIs, financial analytics, and visual charts."""
    # KPI Metrics
    total_students = User.query.filter_by(role='student').count()
    active_visits = IndustrialVisit.query.filter_by(status='published').count()
    total_registrations = Registration.query.count()
    successful_payments_count = Payment.query.filter_by(status='successful').count()
    
    total_revenue = db.session.query(func.sum(Payment.amount))\
        .filter(Payment.status == 'successful').scalar() or 0.0

    # Recent Registrations
    recent_registrations = Registration.query.order_by(Registration.registered_at.desc()).limit(8).all()

    # Upcoming Visits
    now_date = datetime.utcnow().date()
    upcoming_visits = IndustrialVisit.query.filter(IndustrialVisit.visit_date >= now_date)\
        .order_by(IndustrialVisit.visit_date.asc()).limit(5).all()

    # Department-wise Registrations Data for Chart
    dept_stats = db.session.query(
        User.department,
        func.count(Registration.id)
    ).join(Registration, User.id == Registration.user_id)\
     .filter(Registration.status == 'confirmed')\
     .group_by(User.department).all()

    dept_labels = [row[0] for row in dept_stats] or ['Computer', 'Mechanical', 'IT', 'Civil', 'Electrical']
    dept_counts = [row[1] for row in dept_stats] or [0, 0, 0, 0, 0]

    # Visit-wise Registrations Data for Chart
    visit_stats = db.session.query(
        IndustrialVisit.company_name,
        func.count(Registration.id)
    ).join(Registration, IndustrialVisit.id == Registration.visit_id)\
     .filter(Registration.status == 'confirmed')\
     .group_by(IndustrialVisit.company_name)\
     .limit(6).all()

    visit_labels = [row[0] for row in visit_stats] or ['Tata Motors', 'Infosys', 'L&T', 'Reliance', 'Mahindra']
    visit_counts = [row[1] for row in visit_stats] or [0, 0, 0, 0, 0]

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        active_visits=active_visits,
        total_registrations=total_registrations,
        successful_payments_count=successful_payments_count,
        total_revenue=total_revenue,
        recent_registrations=recent_registrations,
        upcoming_visits=upcoming_visits,
        dept_labels_json=json.dumps(dept_labels),
        dept_counts_json=json.dumps(dept_counts),
        visit_labels_json=json.dumps(visit_labels),
        visit_counts_json=json.dumps(visit_counts)
    )


@admin_bp.route('/visits')
@admin_required
def visits():
    """Industrial Visits listing and management table."""
    status_filter = request.args.get('status', 'all')
    
    query = IndustrialVisit.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    all_visits = query.order_by(IndustrialVisit.visit_date.desc()).all()

    return render_template(
        'admin/visits_list.html',
        visits=all_visits,
        active_status=status_filter
    )


@admin_bp.route('/visits/create', methods=['GET', 'POST'])
@admin_required
def create_visit():
    """Form to create a new Industrial Visit."""
    form = VisitForm()
    if form.validate_on_submit():
        # Combine deadline date and time
        deadline_dt = datetime.combine(
            form.registration_deadline_date.data,
            form.registration_deadline_time.data
        )

        visit = IndustrialVisit(
            title=form.title.data.strip(),
            company_name=form.company_name.data.strip(),
            company_logo=form.company_logo.data.strip() if form.company_logo.data else '',
            cover_image=form.cover_image.data.strip() if form.cover_image.data else '',
            description=form.description.data.strip(),
            location=form.location.data.strip(),
            meeting_point=form.meeting_point.data.strip(),
            visit_date=form.visit_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            capacity=form.capacity.data,
            fee=form.fee.data,
            registration_deadline=deadline_dt,
            eligibility_departments=form.eligibility_departments.data.strip(),
            eligibility_years=form.eligibility_years.data.strip(),
            schedule_json=form.schedule_json.data.strip() if form.schedule_json.data else '[]',
            important_instructions=form.important_instructions.data.strip() if form.important_instructions.data else '',
            status=form.status.data
        )

        try:
            db.session.add(visit)
            db.session.commit()
            flash(f"Industrial Visit '{visit.title}' created successfully!", 'success')
            return redirect(url_for('admin.visits'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating visit: {str(e)}', 'danger')

    return render_template('admin/visit_form.html', form=form, title='Create Industrial Visit', is_edit=False)


@admin_bp.route('/visits/<int:visit_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_visit(visit_id):
    """Form to update an existing Industrial Visit."""
    visit = IndustrialVisit.query.get_or_404(visit_id)
    form = VisitForm(obj=visit)

    if request.method == 'GET':
        if visit.registration_deadline:
            form.registration_deadline_date.data = visit.registration_deadline.date()
            form.registration_deadline_time.data = visit.registration_deadline.time()

    if form.validate_on_submit():
        deadline_dt = datetime.combine(
            form.registration_deadline_date.data,
            form.registration_deadline_time.data
        )

        visit.title = form.title.data.strip()
        visit.company_name = form.company_name.data.strip()
        visit.company_logo = form.company_logo.data.strip() if form.company_logo.data else ''
        visit.cover_image = form.cover_image.data.strip() if form.cover_image.data else ''
        visit.description = form.description.data.strip()
        visit.location = form.location.data.strip()
        visit.meeting_point = form.meeting_point.data.strip()
        visit.visit_date = form.visit_date.data
        visit.start_time = form.start_time.data
        visit.end_time = form.end_time.data
        visit.capacity = form.capacity.data
        visit.fee = form.fee.data
        visit.registration_deadline = deadline_dt
        visit.eligibility_departments = form.eligibility_departments.data.strip()
        visit.eligibility_years = form.eligibility_years.data.strip()
        visit.schedule_json = form.schedule_json.data.strip() if form.schedule_json.data else '[]'
        visit.important_instructions = form.important_instructions.data.strip() if form.important_instructions.data else ''
        visit.status = form.status.data

        try:
            db.session.commit()
            flash(f"Industrial Visit '{visit.title}' updated successfully!", 'success')
            return redirect(url_for('admin.visits'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating visit: {str(e)}', 'danger')

    return render_template('admin/visit_form.html', form=form, title=f"Edit: {visit.company_name}", is_edit=True, visit=visit)


@admin_bp.route('/visits/<int:visit_id>/status/<string:new_status>')
@admin_required
def update_visit_status(visit_id, new_status):
    """Quick toggle visit status (published, closed, cancelled, draft, completed)."""
    visit = IndustrialVisit.query.get_or_404(visit_id)
    if new_status in ['draft', 'published', 'closed', 'cancelled', 'completed']:
        visit.status = new_status
        db.session.commit()
        flash(f"Visit status changed to '{new_status.capitalize()}'.", 'success')
    else:
        flash('Invalid status supplied.', 'danger')
    return redirect(url_for('admin.visits'))


@admin_bp.route('/visits/<int:visit_id>/delete', methods=['POST'])
@admin_required
def delete_visit(visit_id):
    """Deletes a visit if it has no confirmed registrations."""
    visit = IndustrialVisit.query.get_or_404(visit_id)
    if visit.confirmed_registrations_count > 0:
        flash('Cannot delete a visit with confirmed student registrations. Please cancel or close it instead.', 'danger')
        return redirect(url_for('admin.visits'))

    db.session.delete(visit)
    db.session.commit()
    flash(f"Visit '{visit.title}' has been deleted.", 'success')
    return redirect(url_for('admin.visits'))


@admin_bp.route('/registrations')
@admin_required
def registrations():
    """Searchable, filterable registration ledger."""
    search = request.args.get('search', '').strip()
    visit_id = request.args.get('visit_id', '').strip()
    dept = request.args.get('department', '').strip()
    year = request.args.get('year', '').strip()
    payment_status = request.args.get('payment_status', '').strip()
    reg_status = request.args.get('status', '').strip()

    query = Registration.query.join(User).join(IndustrialVisit).outerjoin(Payment)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Registration.registration_id.ilike(search_filter),
                User.full_name.ilike(search_filter),
                User.email.ilike(search_filter),
                User.roll_number.ilike(search_filter),
                IndustrialVisit.title.ilike(search_filter),
                IndustrialVisit.company_name.ilike(search_filter)
            )
        )

    if visit_id and visit_id.isdigit():
        query = query.filter(Registration.visit_id == int(visit_id))

    if dept and dept != 'All':
        query = query.filter(User.department == dept)

    if year and year != 'All':
        query = query.filter(User.year == year)

    if reg_status and reg_status != 'All':
        query = query.filter(Registration.status == reg_status)

    if payment_status and payment_status != 'All':
        query = query.filter(Payment.status == payment_status)

    regs = query.order_by(Registration.registered_at.desc()).all()

    # Dropdown choices
    all_visits = IndustrialVisit.query.order_by(IndustrialVisit.title.asc()).all()

    return render_template(
        'admin/registrations.html',
        registrations=regs,
        visits=all_visits,
        search=search,
        selected_visit_id=visit_id,
        selected_dept=dept,
        selected_year=year,
        selected_reg_status=reg_status,
        selected_payment_status=payment_status
    )


@admin_bp.route('/registration/<int:reg_id>')
@admin_required
def registration_detail(reg_id):
    """Full detail view for a student registration and payments."""
    reg = Registration.query.get_or_404(reg_id)
    return render_template('admin/registration_detail.html', registration=reg)


@admin_bp.route('/registration/<int:reg_id>/status/<string:new_status>')
@admin_required
def update_registration_status(reg_id, new_status):
    """Admin manual override for registration status."""
    reg = Registration.query.get_or_404(reg_id)
    if new_status in ['confirmed', 'pending', 'cancelled', 'completed']:
        reg.status = new_status
        if new_status == 'cancelled':
            reg.cancelled_at = datetime.utcnow()
            reg.cancellation_reason = "Cancelled by College Administrator"
        db.session.commit()
        flash(f"Registration status updated to '{new_status.capitalize()}'.", 'success')
    else:
        flash('Invalid status.', 'danger')
    return redirect(url_for('admin.registrations'))


@admin_bp.route('/registrations/export/csv')
@admin_required
def export_registrations_csv():
    """Exports filtered registrations as a CSV file."""
    # Respect the current filters
    regs = get_filtered_registrations()
    csv_data = generate_registrations_csv(regs)
    
    filename = f"registrations_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@admin_bp.route('/registrations/export/excel')
@admin_required
def export_registrations_excel():
    """Exports filtered registrations as a formatted Excel (.xlsx) file."""
    regs = get_filtered_registrations()
    excel_stream = generate_registrations_excel(regs)
    
    filename = f"registrations_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        excel_stream,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def get_filtered_registrations():
    """Helper to query registrations respecting active URL parameters."""
    search = request.args.get('search', '').strip()
    visit_id = request.args.get('visit_id', '').strip()
    dept = request.args.get('department', '').strip()
    year = request.args.get('year', '').strip()
    payment_status = request.args.get('payment_status', '').strip()
    reg_status = request.args.get('status', '').strip()

    query = Registration.query.join(User).join(IndustrialVisit).outerjoin(Payment)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Registration.registration_id.ilike(search_filter),
                User.full_name.ilike(search_filter),
                User.email.ilike(search_filter),
                User.roll_number.ilike(search_filter),
                IndustrialVisit.title.ilike(search_filter),
                IndustrialVisit.company_name.ilike(search_filter)
            )
        )
    if visit_id and visit_id.isdigit():
        query = query.filter(Registration.visit_id == int(visit_id))
    if dept and dept != 'All':
        query = query.filter(User.department == dept)
    if year and year != 'All':
        query = query.filter(User.year == year)
    if reg_status and reg_status != 'All':
        query = query.filter(Registration.status == reg_status)
    if payment_status and payment_status != 'All':
        query = query.filter(Payment.status == payment_status)

    return query.order_by(Registration.registered_at.desc()).all()


@admin_bp.route('/students')
@admin_required
def students():
    """Manage enrolled students directory."""
    search = request.args.get('search', '').strip()
    dept = request.args.get('department', '').strip()
    year = request.args.get('year', '').strip()

    query = User.query.filter_by(role='student')

    if search:
        sf = f"%{search}%"
        query = query.filter(
            or_(
                User.full_name.ilike(sf),
                User.email.ilike(sf),
                User.roll_number.ilike(sf),
                User.phone.ilike(sf)
            )
        )

    if dept and dept != 'All':
        query = query.filter(User.department == dept)
    if year and year != 'All':
        query = query.filter(User.year == year)

    students_list = query.order_by(User.created_at.desc()).all()

    return render_template(
        'admin/students_list.html',
        students=students_list,
        search=search,
        selected_dept=dept,
        selected_year=year
    )


@admin_bp.route('/students/<int:student_id>/toggle-status')
@admin_required
def toggle_student_status(student_id):
    """Toggle student active/deactivated state."""
    student = User.query.get_or_404(student_id)
    if student.role == 'admin':
        flash('Cannot deactivate administrator accounts.', 'danger')
        return redirect(url_for('admin.students'))

    student.is_active = not student.is_active
    db.session.commit()
    state = "activated" if student.is_active else "deactivated"
    flash(f"Student account for {student.full_name} has been {state}.", 'success')
    return redirect(url_for('admin.students'))


@admin_bp.route('/payments')
@admin_required
def payments():
    """Financial payments ledger."""
    status_filter = request.args.get('status', 'all')
    
    query = Payment.query.join(Registration).join(User).join(IndustrialVisit)
    if status_filter != 'all':
        query = query.filter(Payment.status == status_filter)

    all_payments = query.order_by(Payment.created_at.desc()).all()

    total_revenue = db.session.query(func.sum(Payment.amount))\
        .filter(Payment.status == 'successful').scalar() or 0.0
    successful_count = Payment.query.filter_by(status='successful').count()
    pending_count = Payment.query.filter_by(status='pending').count()
    failed_count = Payment.query.filter_by(status='failed').count()
    refunded_count = Payment.query.filter_by(status='refunded').count()

    return render_template(
        'admin/payments_list.html',
        payments=all_payments,
        total_revenue=total_revenue,
        successful_count=successful_count,
        pending_count=pending_count,
        failed_count=failed_count,
        refunded_count=refunded_count,
        active_status=status_filter
    )


@admin_bp.route('/reports')
@admin_required
def reports():
    """Interactive reporting and analytics hub."""
    all_visits = IndustrialVisit.query.order_by(IndustrialVisit.title.asc()).all()
    
    # Aggregated Visit Reports
    visit_reports = []
    for v in all_visits:
        confirmed = v.confirmed_registrations_count
        revenue = db.session.query(func.sum(Payment.amount))\
            .join(Registration, Payment.registration_id == Registration.id)\
            .filter(Registration.visit_id == v.id, Payment.status == 'successful').scalar() or 0.0
        
        visit_reports.append({
            'visit': v,
            'confirmed_count': confirmed,
            'capacity': v.capacity,
            'utilization': round((confirmed / v.capacity * 100), 1) if v.capacity > 0 else 0,
            'revenue': revenue
        })

    # Department breakdown
    dept_breakdown = db.session.query(
        User.department,
        func.count(Registration.id),
        func.sum(Payment.amount)
    ).join(Registration, User.id == Registration.user_id)\
     .outerjoin(Payment, Registration.id == Payment.registration_id)\
     .filter(Registration.status == 'confirmed')\
     .group_by(User.department).all()

    return render_template(
        'admin/reports.html',
        visit_reports=visit_reports,
        dept_breakdown=dept_breakdown,
        visits=all_visits
    )


@admin_bp.route('/seed-database', methods=['POST'])
@admin_required
def trigger_seed():
    """Seeds sample data from admin interface if desired."""
    try:
        seed_database()
        flash('Database seeded with sample visits and student records successfully!', 'success')
    except Exception as e:
        flash(f'Error during seeding: {str(e)}', 'danger')
    return redirect(url_for('admin.dashboard'))
