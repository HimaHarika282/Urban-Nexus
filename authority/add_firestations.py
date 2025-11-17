from app import app, db
from models import FireStation

with app.app_context():
    s1 = FireStation(
        name="Central Fire Station",
        zone_id="Zone 1",
        location="MG Road",
        contact_number="1234567890",
        station_incharge="Rajesh Kumar",
        vehicles_available=5
    )

    s2 = FireStation(
        name="South Fire Brigade",
        zone_id="Zone 2",
        location="Vijay Nagar",
        contact_number="9876543210",
        station_incharge="Anita Mehta",
        vehicles_available=3
    )

    db.session.add_all([s1, s2])
    db.session.commit()
    print("✅ Fire stations added successfully!")