import pytest
from flask import url_for
from app.models.user import User


def test_student_registration_success(client, db):
    """Test successful student account registration."""
    response = client.post('/auth/register', data={
        'full_name': 'Aarav Patel',
        'email': 'aarav@college.edu',
        'roll_number': 'CS2026-099',
        'phone': '9876543210',
        'department': 'Computer Engineering',
        'year': 'Third Year',
        'division': 'A',
        'password': 'SecurePassword@123',
        'confirm_password': 'SecurePassword@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    user = User.query.filter_by(email='aarav@college.edu').first()
    assert user is not None
    assert user.full_name == 'Aarav Patel'
    assert user.role == 'student'
    assert user.check_password('SecurePassword@123') is True
    # Password must NEVER be plaintext
    assert user.password_hash != 'SecurePassword@123'


def test_duplicate_email_registration(client, student_user):
    """Test rejection of duplicate student email."""
    response = client.post('/auth/register', data={
        'full_name': 'Duplicate User',
        'email': student_user.email,  # same email
        'roll_number': 'UNIQUE-123',
        'phone': '9876543210',
        'department': 'Computer Engineering',
        'year': 'Third Year',
        'division': 'A',
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    })

    assert response.status_code == 200
    assert b'already exists' in response.data


def test_duplicate_roll_number_registration(client, student_user):
    """Test rejection of duplicate roll number."""
    response = client.post('/auth/register', data={
        'full_name': 'New Student',
        'email': 'newstudent@college.edu',
        'roll_number': student_user.roll_number,  # duplicate roll number
        'phone': '9876543210',
        'department': 'Computer Engineering',
        'year': 'Third Year',
        'division': 'A',
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    })

    assert response.status_code == 200
    assert b'Roll Number' in response.data or b'already exists' in response.data


def test_invalid_email_registration(client, db):
    """Test rejection of malformed email address."""
    response = client.post('/auth/register', data={
        'full_name': 'Bad Email',
        'email': 'not-an-email',
        'roll_number': 'CS-999',
        'phone': '9876543210',
        'department': 'Computer Engineering',
        'year': 'Third Year',
        'division': 'A',
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    })

    assert response.status_code == 200
    assert b'valid email' in response.data.lower() or b'invalid' in response.data.lower()


def test_weak_password_registration(client, db):
    """Test rejection of weak passwords lacking complexity rules."""
    # Too short
    resp1 = client.post('/auth/register', data={
        'full_name': 'Weak Pwd',
        'email': 'weak1@college.edu',
        'roll_number': 'CS-001',
        'phone': '9876543210',
        'department': 'Computer Engineering',
        'year': 'Third Year',
        'division': 'A',
        'password': 'short',
        'confirm_password': 'short'
    })
    assert b'at least 8 characters' in resp1.data.lower()

    # Missing special character
    resp2 = client.post('/auth/register', data={
        'full_name': 'Weak Pwd 2',
        'email': 'weak2@college.edu',
        'roll_number': 'CS-002',
        'phone': '9876543210',
        'department': 'Computer Engineering',
        'year': 'Third Year',
        'division': 'A',
        'password': 'Password123',
        'confirm_password': 'Password123'
    })
    assert b'special character' in resp2.data.lower()


def test_login_success(client, student_user):
    """Test valid credentials authentication and redirect to dashboard."""
    response = client.post('/auth/login', data={
        'email': student_user.email,
        'password': 'Student@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Student Dashboard' in response.data or b'Welcome back' in response.data


def test_login_invalid_password(client, student_user):
    """Test invalid password rejection."""
    response = client.post('/auth/login', data={
        'email': student_user.email,
        'password': 'WrongPassword@999'
    })

    assert response.status_code == 200
    assert b'Invalid email or password' in response.data


def test_logout(client, student_user):
    """Test user session termination upon logout."""
    # First login
    client.post('/auth/login', data={
        'email': student_user.email,
        'password': 'Student@123'
    })

    # Then logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out' in response.data.lower()


# Authorization Tests
def test_student_cannot_access_admin_dashboard(client, student_user):
    """Ensure student role receives 403 Forbidden on admin routes."""
    client.post('/auth/login', data={
        'email': student_user.email,
        'password': 'Student@123'
    })

    response = client.get('/admin/dashboard')
    assert response.status_code == 403
    assert b'403' in response.data


def test_student_cannot_create_visit(client, student_user):
    """Ensure student cannot create industrial visits."""
    client.post('/auth/login', data={
        'email': student_user.email,
        'password': 'Student@123'
    })

    response = client.get('/admin/visits/create')
    assert response.status_code == 403


def test_admin_can_access_admin_dashboard(client, admin_user):
    """Ensure admin can access admin dashboard."""
    client.post('/auth/login', data={
        'email': admin_user.email,
        'password': 'Admin@123'
    }, follow_redirects=True)

    response = client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b'Administrative Overview' in response.data


def test_logged_out_user_cannot_access_student_dashboard(client):
    """Ensure unauthenticated user is redirected to login from student dashboard."""
    response = client.get('/student/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b'Sign In' in response.data
