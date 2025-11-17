from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ----------------------------
# DEPARTMENT
# ----------------------------
class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    zone_id = db.Column(db.String(50))        # Extra column for citizen portal
    department_address = db.Column(db.String(255)) 
    def __repr__(self):
        return f"<Department {self.name}>"

# ----------------------------
# OFFICER
# ----------------------------
class Officer(UserMixin, db.Model):
    __tablename__ = 'officer'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    department = db.relationship('Department', backref='officers')

    def __repr__(self):
        return f"<Officer {self.username}>"
# ----------------------------
# REQUEST
# ----------------------------
class Request(db.Model):
    __tablename__ = 'request'
    id = db.Column(db.Integer, primary_key=True)
    citizen_name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    department = db.relationship('Department', backref='dept_requests')

# ----------------------------
# POLICE STATION
# ----------------------------
class PoliceStation(db.Model):
    __tablename__ = 'police_station'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    zone_id = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(15))
    station_incharge = db.Column(db.String(100))
    vehicles_available = db.Column(db.Integer)

# ----------------------------
# FIRE STATION
# ----------------------------
class FireStation(db.Model):
    __tablename__ = 'fire_station'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    zone_id = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(255))
    contact_number = db.Column(db.String(15))
    station_incharge = db.Column(db.String(100))
    vehicles_available = db.Column(db.Integer)

# ----------------------------
# EMERGENCY REQUEST
# ----------------------------
class EmergencyRequest(db.Model):
    __tablename__ = 'emergency_requests'
    id = db.Column(db.Integer, primary_key=True)
    citizen_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    department_name = db.Column(db.String(50), nullable=False)  # "police" or "fire"
    status = db.Column(db.String(20), default="Pending")   # Pending / In Progress / Resolved
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    department = db.relationship('Department', backref='emergency_requests')

# ----------------------------
# HOSPITAL
# ----------------------------
class Hospital(db.Model):
    __tablename__ = 'hospital'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    head_doctor = db.Column(db.String(120), nullable=False)
    total_staff = db.Column(db.Integer, nullable=False)
    available_staff = db.Column(db.Integer, nullable=False)
    total_ambulances = db.Column(db.Integer, nullable=False)
    available_ambulances = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.String(20), nullable=False)

# ----------------------------
# INFRASTRUCTURE
# ----------------------------
class Infrastructure(db.Model):
    __tablename__ = 'infrastructure'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(100), nullable=False)        # Park, statue, govt building, etc.
    location = db.Column(db.String(255), nullable=False)
    year_built = db.Column(db.Integer)
    last_renovated = db.Column(db.String(50))
    status = db.Column(db.String(50), default="Good")
