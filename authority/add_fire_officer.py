from app import app, db, bcrypt
from models import Officer, Department

with app.app_context():
    # 1️⃣ Find the Fire Department (create if it doesn't exist)
    fire_dept = Department.query.filter_by(name="Fire Department").first()
    if not fire_dept:
        fire_dept = Department(name="Fire Department")
        db.session.add(fire_dept)
        db.session.commit()
        print("🔥 Fire Department added to DB.")

    # 2️⃣ Create the fire officer user
    hashed_pw = bcrypt.generate_password_hash("password123").decode('utf-8')
    fire_officer = Officer(username="fire_officer", password=hashed_pw, department_id=fire_dept.id)
    
    # 3️⃣ Save to DB
    db.session.add(fire_officer)
    db.session.commit()
    print("✅ Fire officer added successfully!")