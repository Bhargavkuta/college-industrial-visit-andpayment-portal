import sys
import os
from app import create_app, db
from app.utils.seed import seed_database

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.cli.command("init-db")
def init_db():
    """Create all database tables."""
    with app.app_context():
        db.create_all()
        print("Initialized database schema successfully.")


@app.cli.command("seed-db")
def seed_db():
    """Seed database with admin user and sample industrial visits."""
    with app.app_context():
        db.create_all()
        seed_database()


if __name__ == '__main__':
    # CLI arguments for quick command execution: python run.py seed-db
    if len(sys.argv) > 1 and sys.argv[1] == 'seed-db':
        with app.app_context():
            seed_database()
            print("Database seeded. Exiting.")
            sys.exit(0)
    elif len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        with app.app_context():
            db.create_all()
            print("Database initialized. Exiting.")
            sys.exit(0)

    # Automatically check and seed if database is completely empty on first launch
    with app.app_context():
        from app.models.user import User
        if User.query.count() == 0:
            print("Empty database detected. Auto-seeding initial admin and sample visits...")
            seed_database()

    print("=======================================================================")
    print(" Pillai School of Engineering — Industrial Visit Portal")
    print(" Server running at: http://127.0.0.1:5000")
    print(" Default Admin: admin@college.edu | Password: Admin@123")
    print(" Default Student: student@college.edu | Password: Student@123")
    print("=======================================================================")

    app.run(host='0.0.0.0', port=5000, debug=True)
