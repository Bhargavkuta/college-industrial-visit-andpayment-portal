from datetime import datetime
from app import db


class Payment(db.Model):
    """Model tracking financial transactions for registrations."""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registrations.id', ondelete='CASCADE'), nullable=False)
    
    razorpay_order_id = db.Column(db.String(100), nullable=True, index=True)
    razorpay_payment_id = db.Column(db.String(100), nullable=True, index=True)
    razorpay_signature = db.Column(db.String(255), nullable=True)
    
    amount = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(10), default='INR', nullable=False)
    payment_method = db.Column(db.String(50), default='Razorpay', nullable=False)  # 'Razorpay', 'DevMock', 'UPI', 'Card', 'NetBanking'
    
    # Status: 'created', 'pending', 'successful', 'failed', 'refunded'
    status = db.Column(db.String(20), default='created', nullable=False)
    paid_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def status_badge_class(self) -> str:
        """Returns Bootstrap badge color class based on payment status."""
        status_map = {
            'successful': 'bg-success text-white',
            'pending': 'bg-warning text-dark',
            'created': 'bg-info text-dark',
            'failed': 'bg-danger text-white',
            'refunded': 'bg-secondary text-white'
        }
        return status_map.get(self.status, 'bg-secondary text-white')

    @property
    def formatted_amount(self) -> str:
        """Returns formatted currency string (e.g. ₹750.00)."""
        symbol = '₹' if self.currency == 'INR' else '$'
        return f"{symbol}{self.amount:,.2f}"

    def __repr__(self):
        return f"<Payment #{self.id} RegID:{self.registration_id} Amt:{self.amount} Status:{self.status}>"
