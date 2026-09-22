import random
import string
from datetime import datetime
from app import db
from app.models.registration import Registration


def generate_registration_id() -> str:
    """
    Generates a unique, human-readable registration ID.
    Example format: IV-2026-104829
    """
    current_year = datetime.utcnow().year
    
    while True:
        # Generate 6 random digits
        random_num = ''.join(random.choices(string.digits, k=6))
        candidate_id = f"IV-{current_year}-{random_num}"
        
        # Check uniqueness in database
        existing = Registration.query.filter_by(registration_id=candidate_id).first()
        if not existing:
            return candidate_id


def format_inr(amount: float) -> str:
    """Format float amount into Indian Rupee string."""
    try:
        val = float(amount)
        return f"₹{val:,.2f}"
    except (ValueError, TypeError):
        return f"₹0.00"
