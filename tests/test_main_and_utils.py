import pytest
from app.utils.seed import seed_database
from app.utils.helpers import format_inr
from app.models.user import User
from app.models.visit import IndustrialVisit


def test_main_index_page(client, db):
    """Test public landing page HTTP 200 and statistics rendering."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Turn Classroom Learning Into' in response.data
    assert b'How The Portal Works' in response.data


def test_main_about_page(client):
    """Test about page."""
    response = client.get('/about')
    assert response.status_code == 200
    assert b'Industry-Academia Relations Cell' in response.data


def test_main_visit_filters(client, sample_visit, db):
    """Test various visit catalog filters: department, price, availability, date, and sorting."""
    # Filter by department
    res_dept = client.get('/visits?department=Computer+Engineering')
    assert res_dept.status_code == 200
    assert sample_visit.company_name.encode() in res_dept.data

    # Filter by price
    res_price = client.get('/visits?price=under1000')
    assert res_price.status_code == 200
    assert sample_visit.company_name.encode() in res_price.data

    # Filter by availability
    res_avail = client.get('/visits?availability=open')
    assert res_avail.status_code == 200

    # Sort by price
    res_sort = client.get('/visits?sort=price_low')
    assert res_sort.status_code == 200


def test_database_seeding(app, db):
    """Test seed_database utility creates default admin and visits."""
    with app.app_context():
        seed_database()
        admin = User.query.filter_by(email='admin@college.edu').first()
        assert admin is not None
        assert admin.role == 'admin'
        assert admin.check_password('Admin@123') is True

        visits = IndustrialVisit.query.all()
        assert len(visits) >= 5


def test_helper_formatters():
    """Test INR currency formatting."""
    assert format_inr(500) == '₹500.00'
    assert format_inr(1250.50) == '₹1,250.50'
    assert format_inr(0) == '₹0.00'
    assert format_inr(None) == '₹0.00'
