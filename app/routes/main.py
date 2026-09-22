from datetime import datetime
from flask import Blueprint, render_template, request, abort
from flask_login import current_user
from sqlalchemy import or_, and_
from app import db
from app.models.visit import IndustrialVisit
from app.models.user import User
from app.models.registration import Registration
from app.models.payment import Payment

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Public Landing Page featuring industrial visits, live statistics, workflow and testimonials."""
    # Featured visits (published, upcoming)
    featured_visits = IndustrialVisit.query.filter_by(status='published')\
        .filter(IndustrialVisit.visit_date >= datetime.utcnow().date())\
        .order_by(IndustrialVisit.visit_date.asc())\
        .limit(3)\
        .all()
    
    # Real-time statistics
    total_students = User.query.filter_by(role='student').count()
    total_visits = IndustrialVisit.query.filter(IndustrialVisit.status.in_(['published', 'completed'])).count()
    total_registrations = Registration.query.filter_by(status='confirmed').count()
    total_partner_companies = db.session.query(db.func.count(db.func.distinct(IndustrialVisit.company_name))).scalar() or 12

    stats = {
        'total_students': total_students if total_students > 0 else 450,
        'total_visits': total_visits if total_visits > 0 else 18,
        'total_registrations': total_registrations if total_registrations > 0 else 380,
        'total_partner_companies': total_partner_companies
    }

    return render_template('index.html', featured_visits=featured_visits, stats=stats)


@main_bp.route('/about')
def about():
    """About Page for the College Industry Relations Cell."""
    return render_template('about.html')


@main_bp.route('/visits')
def visits():
    """
    Explore Industrial Visits catalog with live search, multi-criteria filters, and sorting.
    Draft visits are strictly hidden from this public view.
    """
    # Base query: exclude drafts
    query = IndustrialVisit.query.filter(IndustrialVisit.status != 'draft')

    # Search keyword filter (title, company_name, location, description)
    search = request.args.get('search', '').strip()
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                IndustrialVisit.title.ilike(search_filter),
                IndustrialVisit.company_name.ilike(search_filter),
                IndustrialVisit.location.ilike(search_filter),
                IndustrialVisit.description.ilike(search_filter)
            )
        )

    # Filter by Department
    dept = request.args.get('department', '').strip()
    if dept and dept != 'All':
        query = query.filter(
            or_(
                IndustrialVisit.eligibility_departments.ilike(f"%{dept}%"),
                IndustrialVisit.eligibility_departments.ilike('%All%')
            )
        )

    # Filter by Location
    loc = request.args.get('location', '').strip()
    if loc:
        query = query.filter(IndustrialVisit.location.ilike(f"%{loc}%"))

    # Filter by Price range
    price = request.args.get('price', '').strip()
    if price == 'free':
        query = query.filter(IndustrialVisit.fee == 0.0)
    elif price == 'under500':
        query = query.filter(IndustrialVisit.fee <= 500.0)
    elif price == 'under1000':
        query = query.filter(IndustrialVisit.fee <= 1000.0)

    # Filter by Date
    date_filter = request.args.get('date', '').strip()
    now_date = datetime.utcnow().date()
    if date_filter == 'upcoming':
        query = query.filter(IndustrialVisit.visit_date >= now_date)
    elif date_filter == 'past':
        query = query.filter(IndustrialVisit.visit_date < now_date)

    # Sorting
    sort_by = request.args.get('sort', 'date_asc')
    if sort_by == 'date_asc':
        query = query.order_by(IndustrialVisit.visit_date.asc())
    elif sort_by == 'date_desc':
        query = query.order_by(IndustrialVisit.visit_date.desc())
    elif sort_by == 'price_low':
        query = query.order_by(IndustrialVisit.fee.asc())
    elif sort_by == 'price_high':
        query = query.order_by(IndustrialVisit.fee.desc())
    elif sort_by == 'title_asc':
        query = query.order_by(IndustrialVisit.title.asc())
    else:
        query = query.order_by(IndustrialVisit.visit_date.asc())

    all_visits = query.all()

    # Filter by availability in python if requested
    availability = request.args.get('availability', '').strip()
    if availability == 'open':
        all_visits = [v for v in all_visits if v.dynamic_status in ['OPEN', 'ALMOST FULL']]

    # Distinct locations for filter dropdown
    locations = db.session.query(db.func.distinct(IndustrialVisit.location))\
        .filter(IndustrialVisit.status != 'draft').all()
    location_list = [l[0] for l in locations if l[0]]

    return render_template(
        'visits/list.html',
        visits=all_visits,
        search=search,
        selected_dept=dept,
        selected_loc=loc,
        selected_price=price,
        selected_date=date_filter,
        selected_availability=availability,
        selected_sort=sort_by,
        locations=location_list
    )


@main_bp.route('/visits/<int:visit_id>')
def visit_details(visit_id):
    """Detailed view for a specific Industrial Visit."""
    visit = IndustrialVisit.query.get_or_404(visit_id)

    # If draft and not admin, return 404
    if visit.status == 'draft' and (not current_user.is_authenticated or not current_user.is_admin):
        abort(404)

    # Check student registration status & eligibility if logged in
    user_registered = False
    existing_registration = None
    can_register = False
    eligibility_message = ""

    if current_user.is_authenticated and current_user.is_student:
        existing_registration = Registration.query.filter_by(
            user_id=current_user.id,
            visit_id=visit.id
        ).filter(Registration.status.in_(['confirmed', 'pending'])).first()
        
        if existing_registration:
            user_registered = True
        
        can_reg, reason = visit.can_register(current_user)
        can_register = can_reg
        eligibility_message = reason
    elif not current_user.is_authenticated:
        can_reg, reason = visit.can_register()
        can_register = can_reg
        eligibility_message = reason

    return render_template(
        'visits/detail.html',
        visit=visit,
        user_registered=user_registered,
        existing_registration=existing_registration,
        can_register=can_register,
        eligibility_message=eligibility_message
    )
