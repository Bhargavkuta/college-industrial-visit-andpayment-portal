# Pillai School of Engineering — Industrial Visit Registration & Payment Portal

A production-quality full-stack web application designed for Pillai School of Engineering to streamline industrial visit discovery, student registration, eligibility verification, online payment processing, and administrative reporting.

---

## 🌟 Key Features

### 👨‍🎓 For Students
- **Account & Profile Management**: Student registration with real-time password strength validation, department/year tracking, and profile updates.
- **Explore Industrial Visits**: Searchable and filterable catalog with live criteria for branch, location, date, price, and seat availability.
- **Dynamic Capacity Meters**: Visual seat counters and badges (`OPEN`, `ALMOST FULL`, `FULL`, `CLOSED`, `CANCELLED`).
- **Multi-Step Booking Flow**:
  1. Profile Verification & Emergency Contact Collection.
  2. Safety Guidelines & Cancellation Policy Consent.
  3. Secure Payment Gateway (Razorpay & Dev Mock Gateway).
  4. Instant Confirmation with Unique Registration ID (`IV-YYYY-XXXXXX`).
- **Official Printable Receipts**: Printable registration vouchers complete with college header, QR/barcode branding, bus departure logistics, and payment verification stamps.
- **My Registrations**: Tabbed history (`All`, `Upcoming`, `Completed`, `Cancelled`) with direct cancellation workflows.

### 🛡️ For Administrators
- **Executive Dashboard**: Real-time KPI summary cards and interactive **Chart.js** analytics (Registrations by Department and Tour Participation by Company).
- **Industrial Visit CRUD**: Comprehensive tour builder with timetable/schedule JSON builder, eligibility filters (branch & year), capacity limits, fees, and deadlines.
- **Status Controls**: Instant publication toggle (`Draft`, `Published`, `Closed`, `Cancelled`, `Completed`).
- **Registration Management Ledger**: Filterable participant audit log with manual status overrides.
- **Financial Payments Ledger**: Complete audit trail of Razorpay order/payment IDs, transaction timestamps, and payment statuses.
- **Automated Data Exports**:
  - **CSV Export**: Dynamic export respecting all active filters.
  - **Excel (.xlsx) Export**: Formatted, styled spreadsheet output powered by `openpyxl`.
- **Interactive Reports Hub**: Visit utilization metrics, seat fill percentages, and branch-wise revenue breakdowns.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.13+, Flask 3.1, Jinja2 |
| **ORM & Database** | Flask-SQLAlchemy 3.1, SQLite (default, easily switchable to MySQL) |
| **Authentication** | Flask-Login 0.6, Werkzeug Password Hashing |
| **Forms & Security** | Flask-WTF 1.3, CSRF Protection, Email-Validator |
| **Payment Gateway** | Razorpay Python SDK + Built-in Development Mock Gateway |
| **Frontend** | HTML5, Vanilla CSS3, Bootstrap 5.3, Bootstrap Icons, Chart.js |
| **Exports** | OpenPyXL 3.1 (Excel), Python CSV |
| **Testing** | Pytest 9.1, Pytest-Flask, Pytest-Cov (Coverage > 85%) |

---

## 📁 Project Architecture

```
industrial-visit-portal/
├── run.py                          # Application entrypoint & CLI commands
├── config.py                       # Configuration classes (Dev, Testing, Prod)
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── README.md                       # Comprehensive documentation
├── instance/
│   └── portal.db                   # SQLite database (auto-generated)
├── app/
│   ├── __init__.py                 # Flask app factory, extensions & error handlers
│   ├── models/
│   │   ├── user.py                 # Student & Admin User models
│   │   ├── visit.py                # IndustrialVisit model with capacity counters
│   │   ├── registration.py         # Registration model with unique ID generator
│   │   └── payment.py              # Payment transaction model
│   ├── forms/
│   │   ├── auth_forms.py           # Registration, login & password forms
│   │   ├── visit_forms.py          # Visit creation and editing forms
│   │   ├── registration_forms.py   # Multi-step checkout & cancellation forms
│   │   └── profile_forms.py        # Student profile form
│   ├── routes/
│   │   ├── auth.py                 # Authentication blueprint (/auth)
│   │   ├── main.py                 # Public landing & visit catalog (/)
│   │   ├── student.py              # Student dashboard & registrations (/student)
│   │   ├── payment.py              # Razorpay checkout & dev mock processor (/payment)
│   │   └── admin.py                # Admin dashboard, CRUD, reports & exports (/admin)
│   ├── utils/
│   │   ├── decorators.py           # @role_required, @admin_required, @student_required
│   │   ├── helpers.py              # Registration ID generator & formatters
│   │   ├── export.py               # CSV and Excel export engines
│   │   └── seed.py                 # Initial database seeding script
│   ├── static/
│   │   ├── css/                    # Custom design system & dashboard stylesheets
│   │   └── js/                     # Tooltips, validation, and payment handlers
│   └── templates/
│       ├── base.html               # Master layout
│       ├── index.html              # Public landing page
│       ├── about.html              # IARC cell about page
│       ├── errors/                 # Custom 403, 404, 500 error pages
│       ├── auth/                   # Sign in & student registration
│       ├── visits/                 # Visit catalog & detailed itinerary views
│       ├── student/                # Student dashboard, checkout, receipts, profile
│       └── admin/                  # Admin dashboard, visits list, reports, ledger
└── tests/
    ├── conftest.py                 # Pytest fixtures & isolated test DB
    ├── test_auth.py                # Auth & RBAC access tests
    ├── test_visits.py              # Visit CRUD & capacity tests
    ├── test_registrations.py       # Registration, eligibility & deadline tests
    ├── test_payments.py            # Razorpay & mock payment tests
    ├── test_admin.py               # Admin reports & export tests
    ├── test_student_features.py    # Student dashboard & receipt tests
    └── test_main_and_utils.py      # Public landing & filter tests
```

---

## 🚀 Quickstart & Installation

### 1. Clone & Set Up Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` if desired:

```ini
SECRET_KEY=your-custom-secret-key-here
DATABASE_URL=sqlite:///instance/portal.db
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_CURRENCY=INR
```

*(Note: Leaving `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` empty automatically activates **Development Mock Payment Gateway** mode for immediate testing).*

### 4. Initialize Database & Seed Realistic Sample Data

```bash
python run.py seed-db
```

### 5. Run the Application

```bash
python run.py
```

The portal will be accessible at: **`http://127.0.0.1:5000`**

---

## 🔑 Default Seed Credentials

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Administrator** | `admin@college.edu` | `Admin@123` | Full Admin Console (`/admin`) |
| **Sample Student** | `student@college.edu` | `Student@123` | Student Dashboard (`/student`) |

---

## 💳 Payment Gateway & Development Mock Mode

The application supports both official **Razorpay** integration and a **Development Mock Payment Gateway**:

- **Production / Razorpay Live Mode**: When `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are provided in `.env`, the checkout launches Razorpay's Standard Checkout modal and performs server-side HMAC-SHA256 signature verification.
- **Development Mock Mode**: When Razorpay keys are omitted, the application seamlessly presents a clearly labeled **Development / Mock Payment Gateway** enabling students to simulate successful payments or simulated transaction failures without needing live API keys.

---

## 🧪 Automated Testing & Test Coverage

Run the complete test suite:

```bash
pytest -v
```

Run tests with test coverage breakdown:

```bash
pytest --cov=app --cov-report=term-missing
```

### Test Suite Summary:
- **48 Automated Tests** covering Authentication, RBAC Authorization, Industrial Visit CRUD, Capacity Enforcement, Deadline Validation, Department & Academic Year Eligibility, Duplicate Prevention, Signature Verification, Payment Failures, CSV/Excel Exports, and Admin Reports.
- **Code Coverage**: **86%+** across all core application logic.

---

## 📊 Switching from SQLite to MySQL

To connect to a MySQL database:

1. Install the MySQL driver:
   ```bash
   pip install pymysql cryptography
   ```
2. Update `DATABASE_URL` in `.env`:
   ```ini
   DATABASE_URL=mysql+pymysql://username:password@localhost:3306/college_portal_db
   ```
3. Initialize tables:
   ```bash
   python run.py init-db
   python run.py seed-db
   ```

---

## 📄 License
This project is developed for college academic and production deployment. All rights reserved.
