import json
from datetime import datetime, timedelta, date, time
from app import db
from app.models.user import User
from app.models.visit import IndustrialVisit
from app.models.registration import Registration
from app.models.payment import Payment
from app.utils.helpers import generate_registration_id


def seed_database():
    """Seeds the database with initial admin user, sample students, and realistic industrial visits."""
    
    # 1. Create or verify Administrator account
    admin_email = "admin@college.edu"
    admin_user = User.query.filter_by(email=admin_email).first()
    if not admin_user:
        admin_user = User(
            full_name="College Portal Administrator",
            email=admin_email,
            phone="+91 98765 43210",
            roll_number="FAC-ADMIN-01",
            department="Industry-Academia Relations Cell",
            year="Staff",
            division="HQ",
            role="admin",
            is_active=True
        )
        admin_user.set_password("Admin@123")
        db.session.add(admin_user)
        print(f"Created Admin account: {admin_email} (Password: Admin@123)")
    
    # 2. Create Sample Student account for testing
    student_email = "student@college.edu"
    student_user = User.query.filter_by(email=student_email).first()
    if not student_user:
        student_user = User(
            full_name="Bhargav Sharma",
            email=student_email,
            phone="+91 98234 56789",
            roll_number="CS2026-042",
            department="Computer Engineering",
            year="Third Year",
            division="A",
            role="student",
            is_active=True
        )
        student_user.set_password("Student@123")
        db.session.add(student_user)
        print(f"Created Sample Student account: {student_email} (Password: Student@123)")

    # 3. Create Realistic Industrial Visits
    now = datetime.utcnow()
    
    sample_visits = [
        {
            "title": "Automated EV Assembly Line & Robotics Plant Tour",
            "company_name": "Tata Motors Ltd.",
            "company_logo": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=200&auto=format&fit=crop&q=80",
            "cover_image": "https://images.unsplash.com/photo-1565043589221-1a6fd9ae45c7?w=1200&auto=format&fit=crop&q=80",
            "description": "Explore one of Asia's largest automotive manufacturing facilities. Witness cutting-edge automated robotic welding lines, battery pack integration for electric passenger vehicles (Nexon EV / Curvv EV), paint shop technology, and final vehicle quality inspection corridors.",
            "location": "Tata Motors Car Plant, Pimpri-Chinchwad, Pune, Maharashtra",
            "meeting_point": "College Main Campus Gate No. 1 (College Bus Departure)",
            "visit_date": (now + timedelta(days=14)).date(),
            "start_time": time(7, 30),
            "end_time": time(17, 30),
            "capacity": 50,
            "fee": 650.0,
            "registration_deadline": now + timedelta(days=10),
            "eligibility_departments": "Mechanical Engineering, Electrical Engineering, Automobile Engineering, Computer Engineering",
            "eligibility_years": "Second Year, Third Year, Final Year",
            "schedule_json": json.dumps([
                {"time": "07:30 AM", "activity": "Assembly & Attendance", "description": "Mandatory ID verification and briefing at College Gate 1"},
                {"time": "08:00 AM", "activity": "Bus Departure", "description": "Air-conditioned bus transit to Tata Motors Pimpri facility"},
                {"time": "09:30 AM", "activity": "Arrival & Safety Induction", "description": "Safety video, issuance of safety goggles and high-visibility vests"},
                {"time": "10:30 AM", "activity": "Robotics & Body Assembly Tour", "description": "Guided walkthrough of robotic spot-welding and sheet metal press lines"},
                {"time": "01:00 PM", "activity": "Networking Lunch", "description": "Buffet lunch provided at Tata Motors Visitor Dining Hall"},
                {"time": "02:00 PM", "activity": "EV Powertrain & Battery Lab", "description": "Interactive session with Tata Motors R&D Senior Engineers"},
                {"time": "03:30 PM", "activity": "Q&A and Feedback Session", "description": "Career paths, internship opportunities, and certificate distribution"},
                {"time": "04:30 PM", "activity": "Return Journey", "description": "Departure back to College Campus (Estimated arrival 05:30 PM)"}
            ]),
            "important_instructions": "• Mandatory College ID card and formal dress code.\n• Fully enclosed leather shoes/safety boots required (No sandals, heels or open footwear allowed in plant).\n• Photography and video recording inside assembly corridors are strictly prohibited as per company policy.\n• Refreshments and lunch are included in the registration fee.",
            "status": "published"
        },
        {
            "title": "Enterprise Cloud Architecture & AI Innovation Hub",
            "company_name": "Infosys Limited",
            "company_logo": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=200&auto=format&fit=crop&q=80",
            "cover_image": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&auto=format&fit=crop&q=80",
            "description": "Step inside Infosys's state-of-the-art Global Development Centre. Experience world-class enterprise AI frameworks, cloud security operations command center, green building architecture, and live interaction with principal solution architects.",
            "location": "Infosys SEZ Campus, Hinjawadi Phase 2, Pune",
            "meeting_point": "College Auditorium Concourse (Campus Bus Bay 3)",
            "visit_date": (now + timedelta(days=21)).date(),
            "start_time": time(8, 30),
            "end_time": time(16, 30),
            "capacity": 45,
            "fee": 450.0,
            "registration_deadline": now + timedelta(days=16),
            "eligibility_departments": "Computer Engineering, Information Technology, Electronics & Telecommunication, Artificial Intelligence & Data Science",
            "eligibility_years": "Third Year, Final Year",
            "schedule_json": json.dumps([
                {"time": "08:30 AM", "activity": "Campus Departure", "description": "Bus departure from College Concourse"},
                {"time": "09:45 AM", "activity": "Campus Security & Smart Card Issuance", "description": "Visitor entry clearance at Infosys Main Gate"},
                {"time": "10:30 AM", "activity": "Topaz AI & Cloud Living Lab Tour", "description": "Live demonstration of enterprise generative AI platforms"},
                {"time": "12:30 PM", "activity": "Lunch at Food Court 3", "description": "Complimentary lunch vouchers provided"},
                {"time": "01:45 PM", "activity": "Tech Talk by Principal Architect", "description": "Topic: Modern Distributed Microservices & Zero-Trust Cloud Architecture"},
                {"time": "03:15 PM", "activity": "HR Career & Fresher Hiring Overview", "description": "Insights on Infosys Springboard, certifications, and hiring pathways"},
                {"time": "04:00 PM", "activity": "Return Transit", "description": "Bus departure back to campus"}
            ]),
            "important_instructions": "• Government Photo ID (Aadhaar / Voter ID / Passport) is strictly required along with College ID.\n• Business casuals or college uniform.\n• Laptops are not permitted inside security gates; personal mobile phones must be silenced.",
            "status": "published"
        },
        {
            "title": "Mega Infrastructure & Heavy Engineering Manufacturing",
            "company_name": "Larsen & Toubro (L&T)",
            "company_logo": "https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?w=200&auto=format&fit=crop&q=80",
            "cover_image": "https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?w=1200&auto=format&fit=crop&q=80",
            "description": "Gain firsthand insights into mega-scale infrastructure fabrication, nuclear reactor vessel engineering, heavy precision machinery, and modular construction systems that power national defense and international transport corridors.",
            "location": "L&T Heavy Engineering Complex, Hazira / Powai Works",
            "meeting_point": "College Mechanical Engineering Department Foyer",
            "visit_date": (now + timedelta(days=28)).date(),
            "start_time": time(7, 0),
            "end_time": time(18, 0),
            "capacity": 40,
            "fee": 750.0,
            "registration_deadline": now + timedelta(days=22),
            "eligibility_departments": "Mechanical Engineering, Civil Engineering, Electrical Engineering, Production Engineering",
            "eligibility_years": "Third Year, Final Year",
            "schedule_json": json.dumps([
                {"time": "07:00 AM", "activity": "Morning Assembly", "description": "Safety gear check and breakfast packet distribution"},
                {"time": "07:30 AM", "activity": "Departure", "description": "Transit to L&T Manufacturing Complex"},
                {"time": "09:30 AM", "activity": "Safety Induction & PPE Issuance", "description": "Hard hats, safety glasses, and steel-toe shoe compliance check"},
                {"time": "10:30 AM", "activity": "Heavy Machine Bay & Welding Tour", "description": "Inspection of precision CNC gantry machines and submarine module fabrication"},
                {"time": "01:00 PM", "activity": "Executive Dining Hall Lunch", "description": "Buffet lunch with L&T project leads"},
                {"time": "02:15 PM", "activity": "Civil Design & BIM Simulation Session", "description": "Session on 3D Building Information Modelling for High-Speed Rail Projects"},
                {"time": "04:30 PM", "activity": "Return Departure", "description": "Bus transit back to College Campus"}
            ]),
            "important_instructions": "• Strict Safety Norms: Hard hats and earplugs will be provided on site.\n• Loose clothing, shorts, skirts, or open footwear are forbidden.\n• Prior submission of medical fitness self-declaration is mandatory.",
            "status": "published"
        },
        {
            "title": "Clean Energy, 5G Telco NOC & Digital Services Facility",
            "company_name": "Reliance Industries Limited",
            "company_logo": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=200&auto=format&fit=crop&q=80",
            "cover_image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&auto=format&fit=crop&q=80",
            "description": "Experience Reliance Jio's National Network Operations Center (NOC) managing over 450 million subscribers, coupled with an interactive tour of the Green Energy Giga-Complex research facilities for solar photovoltaics and green hydrogen.",
            "location": "Reliance Corporate Park (RCP), Ghansoli, Navi Mumbai",
            "meeting_point": "College Administrative Block Porch",
            "visit_date": (now + timedelta(days=35)).date(),
            "start_time": time(8, 0),
            "end_time": time(17, 0),
            "capacity": 60,
            "fee": 500.0,
            "registration_deadline": now + timedelta(days=29),
            "eligibility_departments": "All",
            "eligibility_years": "All",
            "schedule_json": json.dumps([
                {"time": "08:00 AM", "activity": "Departure", "description": "Depart from College Campus via AC Express coaches"},
                {"time": "09:30 AM", "activity": "Welcome & Corporate Overview", "description": "Keynote presentation at Reliance Auditorium"},
                {"time": "10:30 AM", "activity": "Jio 5G NOC Command Floor", "description": "Observing real-time global traffic routing and cloud datacenters"},
                {"time": "01:00 PM", "activity": "Lunch at RCP Central Diner", "description": "Full course lunch provided"},
                {"time": "02:00 PM", "activity": "Renewable Energy Research Showcase", "description": "Solar cells, green hydrogen electrolyzers and battery storage demos"},
                {"time": "03:45 PM", "activity": "Interactive Quiz & Certificate Handover", "description": "Gift hampers for quiz winners"},
                {"time": "04:30 PM", "activity": "Departure", "description": "Return to College Campus"}
            ]),
            "important_instructions": "• Smart Casuals or College Uniform.\n• College ID card is mandatory.\n• Smartwatches and cameras are prohibited inside the NOC floor.",
            "status": "published"
        },
        {
            "title": "Off-Road Vehicle Testing & Electric Mobility R&D Lab",
            "company_name": "Mahindra & Mahindra",
            "company_logo": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=200&auto=format&fit=crop&q=80",
            "cover_image": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1200&auto=format&fit=crop&q=80",
            "description": "Visit the Mahindra Research Valley (MRV) automotive testing grounds. See crash simulation rigs, wind tunnel aerodynamic testing, NVH acoustic chambers, and ride along on the vehicle test track.",
            "location": "Mahindra Vehicle Manufacturers Ltd., Chakan Industrial Area, Pune",
            "meeting_point": "College Main Campus Parking Lot",
            "visit_date": (now + timedelta(days=42)).date(),
            "start_time": time(8, 0),
            "end_time": time(17, 30),
            "capacity": 35,
            "fee": 550.0,
            "registration_deadline": now + timedelta(days=36),
            "eligibility_departments": "Mechanical Engineering, Automobile Engineering, Electrical Engineering, Electronics Engineering",
            "eligibility_years": "Third Year, Final Year",
            "schedule_json": json.dumps([
                {"time": "08:00 AM", "activity": "Bus Departure", "description": "Transit to Mahindra Chakan Mega Plant"},
                {"time": "09:30 AM", "activity": "Orientation & Safety Briefing", "description": "Introduction to Mahindra Rise philosophy and testing safety"},
                {"time": "10:30 AM", "activity": "Acoustic Chamber & Wind Tunnel Lab", "description": "Live demonstration of NVH (Noise, Vibration, Harshness) measurement"},
                {"time": "12:45 PM", "activity": "Executive Dining Lunch", "description": "Lunch with vehicle dynamics team"},
                {"time": "02:00 PM", "activity": "High-Speed Proving Ground & Test Track", "description": "Observing electronic stability control and off-road articulation tracks"},
                {"time": "03:45 PM", "activity": "Session with Chief Product Engineer", "description": "Future of Autonomous Driving & ADAS Level 2+ in India"},
                {"time": "04:45 PM", "activity": "Return Transit", "description": "Departure to college campus"}
            ]),
            "important_instructions": "• Sturdy footwear mandatory.\n• Long hair must be tied securely.\n• College ID card required at all checkpoints.",
            "status": "published"
        },
        {
            "title": "Space Electronics & Satellite Integration Facility",
            "company_name": "ISRO Satellite Centre (URSC)",
            "company_logo": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=200&auto=format&fit=crop&q=80",
            "cover_image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&auto=format&fit=crop&q=80",
            "description": "Exclusive visit to the space technology center. Explore cleanroom satellite integration bays, thermovac test chambers simulating deep-space vacuum and solar radiation, and telemetry command ground stations.",
            "location": "ISRO Satellite Centre, Space Exhibition Hall & Cleanrooms",
            "meeting_point": "College Auditorium Concourse",
            "visit_date": (now + timedelta(days=60)).date(),
            "start_time": time(9, 0),
            "end_time": time(16, 0),
            "capacity": 30,
            "fee": 900.0,
            "registration_deadline": now + timedelta(days=50),
            "eligibility_departments": "All",
            "eligibility_years": "Third Year, Final Year",
            "schedule_json": json.dumps([
                {"time": "09:00 AM", "activity": "Security Clearance", "description": "Biometric verification and security gate clearance"},
                {"time": "10:00 AM", "activity": "Cleanroom Observation Gallery", "description": "Viewing Earth observation satellite assembly under ISO Class 5 cleanrooms"},
                {"time": "12:30 PM", "activity": "Scientist Interaction & Lunch", "description": "Discussions with ISRO payload scientists"},
                {"time": "02:00 PM", "activity": "Thermal Vacuum Simulation Facility", "description": "Cryogenic thermal chamber demonstration"},
                {"time": "03:30 PM", "activity": "Space Museum & Mission Gallery", "description": "Guided walkthrough of scale models (Chandrayaan, Aditya-L1)"}
            ]),
            "important_instructions": "• High security zone: Aadhaar Card / Passport mandatory.\n• Non-Indian nationals must obtain prior clearance from ISRO Liaison Office.\n• Absolutely zero electronics allowed inside the cleanroom gallery.",
            "status": "draft"
        }
    ]

    for item in sample_visits:
        existing_visit = IndustrialVisit.query.filter_by(
            title=item["title"],
            company_name=item["company_name"]
        ).first()
        
        if not existing_visit:
            visit = IndustrialVisit(**item)
            db.session.add(visit)
            print(f"Added Visit: {item['company_name']} - {item['title']} ({item['status']})")
    
    db.session.commit()

    # 4. Create a sample confirmed registration and payment for the sample student on Tata Motors visit
    tata_visit = IndustrialVisit.query.filter_by(company_name="Tata Motors Ltd.").first()
    if tata_visit and student_user:
        existing_reg = Registration.query.filter_by(
            user_id=student_user.id,
            visit_id=tata_visit.id
        ).first()
        
        if not existing_reg:
            sample_reg_id = generate_registration_id()
            reg = Registration(
                registration_id=sample_reg_id,
                user_id=student_user.id,
                visit_id=tata_visit.id,
                registered_at=now - timedelta(days=1),
                status='confirmed',
                emergency_contact="Ramesh Sharma (Father)",
                emergency_phone="+91 98111 22233",
                terms_accepted=True
            )
            db.session.add(reg)
            db.session.flush()

            # Add successful payment
            payment = Payment(
                registration_id=reg.id,
                razorpay_order_id="order_mock_demo_101",
                razorpay_payment_id="pay_mock_demo_882314",
                razorpay_signature="mock_valid_signature_hash_verified",
                amount=tata_visit.fee,
                currency="INR",
                payment_method="DevMock UPI",
                status="successful",
                paid_at=now - timedelta(days=1),
                created_at=now - timedelta(days=1)
            )
            db.session.add(payment)
            db.session.commit()
            print(f"Created sample confirmed registration {sample_reg_id} for {student_user.full_name}")

    print("Database seeding completed successfully!")
