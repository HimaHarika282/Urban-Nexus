
from flask import render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
from flask_migrate import Migrate
from werkzeug.security import check_password_hash
from models import db, Officer, Department, Request, PoliceStation, FireStation, EmergencyRequest, Hospital, Infrastructure
from . import authority_bp


@authority_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Officer.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful', 'success')

            # Dynamically redirect based on department name
            if user.department and user.department.name.lower() == 'police':
                return redirect(url_for('authority_bp.police_dashboard'))
            elif user.department and user.department.name.lower() == 'fire department':
                return redirect(url_for('authority_bp.fire_dashboard'))
            elif user.department and user.department.name.lower() == 'hospital':
                return redirect(url_for('authority_bp.hospital_dashboard'))
            elif user.department and user.department.name.lower() == 'water supply':
                return redirect(url_for('authority_bp.water_dashboard'))
            elif user.department and user.department.name.lower() == 'infrastructure':
                return redirect(url_for('authority_bp.infrastructure_dashboard'))
            elif user.department and user.department.name.lower() == 'electricity':
                return redirect(url_for('authority_bp.electricity_dashboard'))
            elif user.department and user.department.name.lower() == 'gas':
                return redirect(url_for('authority_bp.gas_dashboard'))
            elif user.department and user.department.name.lower() == 'transport':
                return redirect(url_for('authority_bp.transport_dashboard'))
            else:
                flash('Department not recognized.', 'danger')
                return redirect(url_for('authority_bp.login'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@authority_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@authority_bp.route('/dashboard/police')
@login_required
def police_dashboard():
    requests = Request.query.filter_by(department_id=current_user.department_id).all()
    return render_template('police/dashboard.html', officer=current_user, requests=requests, )

@authority_bp.route('/dashboard/police/requests')
@login_required
def police_requests():
    requests = Request.query.filter_by(department_id=current_user.department_id).all()
    return render_template('police/requests.html', requests=requests)

@authority_bp.route('/dashboard/police/emergency')
@login_required
def police_emergency():
    police_dept = Department.query.filter_by(name="Police").first()
    emergencies = EmergencyRequest.query.filter_by(department_id=police_dept.id).all()
    return render_template('police/emergency.html', emergencies=emergencies)

@authority_bp.route('/dashboard/police/stations')
@login_required
def police_stations():
    stations = PoliceStation.query.all()

    # Calculate stats
    total_stations = len(stations)
    total_vehicles = sum([s.vehicles_available or 0 for s in stations])
    zones = set([s.zone_id for s in stations])
    zones_count = len(zones)

    return render_template(
        'police/stations.html',
        stations=stations,
        total_stations=total_stations,
        total_vehicles=total_vehicles,
        zones_count=zones_count
    )

@authority_bp.route('/dashboard/police/map')
@login_required
def police_map():
    # Fetch requests and stations from database
    requests = Request.query.filter_by(department_id=current_user.department_id).all()
    stations = PoliceStation.query.all()

    # Prepare data for map (convert to list of dicts for JSON)
    request_data = [
        {
            "id": r.id,
            "citizen_name": r.citizen_name,
            "location": r.location,
            "description": r.description,
            "status": r.status
        }
        for r in requests
    ]

    station_data = [
        {
            "id": s.id,
            "name": s.name,
            "zone": s.zone_id,
            "contact": s.contact_number,
            "incharge": s.station_incharge
        }
        for s in stations
    ]

    return render_template(
        'police/map.html',
        request_data=request_data,
        station_data=station_data
    )

@authority_bp.route('/dashboard/fire')
@login_required
def fire_dashboard():
    # ensure only fire officers access (optional)
    if not (current_user.department and current_user.department.name.lower().startswith('fire')):
        flash("Access denied: You are not a fire department user.", "danger")
        return redirect(url_for('authority_bp.login'))

    # queries (adjust model names if you used a different one for stations)
    total_stations = FireStation.query.count() if 'FireStation' in globals() else 0
    stations = FireStation.query.all() if 'FireStation' in globals() else []
    total_vehicles = sum((s.vehicles_available or 0) for s in stations) if stations else 0
    # active requests for Fire department
    fire_dept = Department.query.filter(Department.name.ilike('%fire%')).first()
    active_count = 0
    if fire_dept:
        active_count = Request.query.filter_by(department_id=fire_dept.id, status='Pending').count()

    return render_template('fire/dashboard.html',
                           officer=current_user,
                           total_stations=total_stations,
                           total_vehicles=total_vehicles,
                           active_count=active_count)

@authority_bp.route('/dashboard/fire/requests')
@login_required
def fire_requests():
    fire_dept = Department.query.filter(Department.name.ilike("%fire%")).first()

    fire_requests = []
    if fire_dept:
        fire_requests = Request.query.filter_by(department_id=fire_dept.id).all()

    return render_template(
        'fire/requests.html',
        fire_requests=fire_requests,
        officer=current_user
    )


@authority_bp.route('/dashboard/fire/stations')
@login_required
def fire_stations():
    stations = FireStation.query.all() if 'FireStation' in globals() else []
    return render_template('fire/stations.html', stations=stations, officer=current_user)

@authority_bp.route('/dashboard/fire/map')
@login_required
def fire_map():
    # prepare station and request data similar to police_map
    return render_template('fire/map.html', officer=current_user)

@authority_bp.route('/dashboard/fire/resources')
@login_required
def fire_resources():
    resources = [
        {"name": "Fire Truck A1", "status": "Available", "station": "Central"},
        {"name": "Fire Truck B2", "status": "In Use", "station": "East Station"},
        {"name": "Hydrant Set", "status": "Operational", "station": "North Station"}
    ]
    return render_template('fire/resources.html')

@authority_bp.route('/dashboard/fire/emergency')
@login_required
def fire_emergency():
    fire_dept = Department.query.filter_by(name="Fire Department").first()
    emergencies = EmergencyRequest.query.filter_by(department_id=fire_dept.id).all()
    return render_template('fire/emergency.html', emergencies=emergencies)

@authority_bp.route('/police/requests/update/<int:req_id>', methods=['POST'])
@login_required
def update_request(req_id):
    req = Request.query.get(req_id)
    req.status = request.form['status']
    db.session.commit()
    flash('Status updated successfully', 'success')
    return redirect(url_for('authority_bp.police_dashboard'))

@authority_bp.route('/police/emergency/update/<int:req_id>/<string:status>')
@login_required
def update_emergency_request(req_id, status):
    req = EmergencyRequest.query.get(req_id)
    if req:
        req.status = status
        db.session.commit()
        flash("Emergency request status updated!", "success")
    else:
        flash("Request not found!", "danger")
    return redirect(url_for('authority_bp.police_dashboard'))

@authority_bp.route('/fire/request/update/<int:req_id>/<string:new_status>')
@login_required
def update_fire_request(req_id, new_status):
    req = Request.query.get(req_id)

    if req:
        req.status = new_status
        db.session.commit()
        flash("🔥 Request status updated!", "success")
    else:
        flash("Request not found!", "danger")

    return redirect(url_for('authority_bp.fire_requests'))

@authority_bp.route('/fire/emergency/update/<int:req_id>/<string:new_status>', methods=['GET'])
@login_required
def update_fire_emergency(req_id, new_status):
    req = EmergencyRequest.query.get(req_id)

    if req:
        req.status = new_status
        db.session.commit()
        flash("Fire emergency request updated!", "success")
    else:
        flash("Request not found!", "danger")

    return redirect(url_for('authority_bp.fire_emergency'))

@authority_bp.route('/dashboard/hospital')
@login_required
def hospital_dashboard():
    hospital_dept = Department.query.filter_by(name="Hospital").first()

    # Filter Requests and EmergencyRequests for hospital
    requests = Request.query.filter_by(department_id=hospital_dept.id).all()
    emergencies = EmergencyRequest.query.filter_by(department_id=hospital_dept.id).all()

    hospitals = Hospital.query.all()

    return render_template(
        'hospital/dashboard.html',
        requests=requests,
        emergencies=emergencies,
        hospitals=hospitals
    )

@authority_bp.route('/hospital/requests')
@login_required
def hospital_requests():
    hospital_dept = Department.query.filter_by(name="Hospital").first()
    requests = Request.query.filter_by(department_id=hospital_dept.id).all()

    return render_template("hospital/requests.html", requests=requests)

@authority_bp.route('/hospital/emergency')
@login_required
def hospital_emergency():
    hospital_dept = Department.query.filter_by(name="Hospital").first()
    emergencies = EmergencyRequest.query.filter_by(department_id=hospital_dept.id).all()

    return render_template("hospital/emergency.html", emergencies=emergencies)

@authority_bp.route('/hospital/info')
@login_required
def hospital_info():
    hospitals = Hospital.query.all()
    return render_template("hospital/info.html", hospitals=hospitals)

@authority_bp.route('/hospital/request/update/<int:req_id>/<string:status>')
@login_required
def update_hospital_request(req_id, status):
    req = Request.query.get(req_id)

    if req:
        req.status = status
        db.session.commit()
        flash("Request status updated successfully!", "success")
    else:
        flash("Request not found!", "danger")

    return redirect(url_for('authority_bp.hospital_requests'))

@authority_bp.route('/hospital/emergency/update/<int:req_id>/<string:status>')
@login_required
def update_hospital_emergency(req_id, status):
    req = EmergencyRequest.query.get(req_id)

    if req:
        req.status = status
        db.session.commit()
        flash("Emergency request status updated!", "success")
    else:
        flash("Emergency request not found!", "danger")

    return redirect(url_for('authority_bp.hospital_emergency'))

@authority_bp.route('/dashboard/water')
@login_required
def water_dashboard():
    water_dept = Department.query.filter(Department.name.ilike('%water%')).first()
    requests = Request.query.filter_by(department_id=water_dept.id).all() if water_dept else []

    return render_template(
        'water/dashboard.html',
        requests=requests,
        officer=current_user
    )

@authority_bp.route('/water/request/update/<int:req_id>/<string:new_status>')
@login_required
def update_water_request(req_id, new_status):
    req = Request.query.get(req_id)
    if req:
        req.status = new_status
        db.session.commit()
        flash("Request status updated!", "success")
    else:
        flash("Request not found!", "danger")
    return redirect(url_for('authority_bp.water_dashboard'))

@authority_bp.route('/dashboard/electricity')
@login_required
def electricity_dashboard():
    dept_id = current_user.department_id

    search = request.args.get("search", "").lower()
    status_filter = request.args.get("status", "")

    query = Request.query.filter_by(department_id=dept_id)

    if search:
        query = query.filter(
            (Request.citizen_name.ilike(f"%{search}%")) |
            (Request.description.ilike(f"%{search}%")) |
            (Request.location.ilike(f"%{search}%"))
        )

    if status_filter:
        query = query.filter_by(status=status_filter)

    requests_list = query.all()

    return render_template(
        "electricity/dashboard.html",
        requests=requests_list,
        search=search,
        status_filter=status_filter
    )

@authority_bp.route('/electricity/request/update/<int:req_id>/<string:new_status>')
@login_required
def update_electricity_request(req_id, new_status):
    req = Request.query.get(req_id)

    # get the electricity department dynamically
    electricity_dept = Department.query.filter(Department.name.ilike("%electric%")).first()

    if req and electricity_dept and req.department_id == electricity_dept.id:
        req.status = new_status
        db.session.commit()
        flash("Electricity request status updated!", "success")
    else:
        flash("Request not found!", "danger")

    return redirect(url_for('authority_bp.electricity_dashboard'))

@authority_bp.route('/dashboard/gas')
@login_required
def gas_dashboard():
    dept_id = current_user.department_id

    search = request.args.get("search", "").lower()
    status_filter = request.args.get("status", "")

    query = Request.query.filter_by(department_id=dept_id)

    if search:
        query = query.filter(
            (Request.citizen_name.ilike(f"%{search}%")) |
            (Request.description.ilike(f"%{search}%")) |
            (Request.location.ilike(f"%{search}%"))
        )

    if status_filter:
        query = query.filter_by(status=status_filter)

    requests_list = query.all()

    return render_template(
        "gas/dashboard.html",
        requests=requests_list,
        search=search,
        status_filter=status_filter
    )

@authority_bp.route('/gas/update/<int:req_id>/<string:new_status>')
@login_required
def update_gas_request(req_id, new_status):
    req = Request.query.get(req_id)

    if req:
        req.status = new_status
        db.session.commit()
        flash("Request status updated!", "success")
    else:
        flash("Request not found!", "danger")

    return redirect(url_for('authority_bp.gas_dashboard'))

@authority_bp.route('/dashboard/infrastructure')
@login_required
def infrastructure_dashboard():
    if current_user.department.name.lower() != "infrastructure":
        flash("Unauthorized access!", "danger")
        return redirect(url_for('authority_bp.login'))

    requests = Request.query.filter_by(department_id=8).all()
    properties = Infrastructure.query.all()

    return render_template(
        'infrastructure/dashboard.html',
        requests=requests,
        properties=properties
    )

@authority_bp.route('/infrastructure/requests')
@login_required
def infrastructure_requests():
    infra_requests = Request.query.filter_by(department_id=7).all()

    return render_template(
        'infrastructure/requests.html',
        requests=infra_requests
    )

@authority_bp.route('/infrastructure/request/update/<int:req_id>/<string:new_status>')
@login_required
def update_infra_request(req_id, new_status):
    req = Request.query.get(req_id)

    if req and req.department_id == 7:  # Infrastructure department ID
        req.status = new_status
        db.session.commit()
        flash("Infrastructure request status updated!", "success")
    else:
        flash("Request not found!", "danger")

    return redirect(url_for('authority_bp.infrastructure_requests'))

@authority_bp.route('/infrastructure/properties')
@login_required
def infrastructure_properties():
    props = Infrastructure.query.all()
    return render_template(
        'infrastructure/properties.html',
        properties=props
    )

# ----------------------------
# ADD DEMO DATA (ONLY ONCE)
# ----------------------------
@authority_bp.cli.command('initdb')
def initdb():
    db.drop_all()
    db.create_all()

    # Departments
    water = Department(name="Water Supply")
    elec = Department(name="Electricity")
    db.session.add_all([water, elec])
    db.session.commit()

    # Officers
    hashed_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')
    officer1 = Officer(username="water_officer", password=hashed_pwd, department=water)
    officer2 = Officer(username="elec_officer", password=hashed_pwd, department=elec)
    db.session.add_all([officer1, officer2])

    # Demo Requests
    req1 = ServiceRequest(citizen_name="John", description="Water leak in sector 9", department=water)
    req2 = ServiceRequest(citizen_name="Ravi", description="Electric pole broken", department=elec)
    db.session.add_all([req1, req2])
    db.session.commit()
    print("✅ Database initialized with demo data!")


@authority_bp.route("/reset_officers")
def reset_officers():
    try:
        # Clear existing officers (optional, comment out if you want to keep them)
        Officer.query.delete()

        # Create sample departments
        water = Department.query.filter_by(name="Water").first()
        if not water:
            water = Department(name="Water")
            db.session.add(water)

        electricity = Department.query.filter_by(name="Electricity").first()
        if not electricity:
            electricity = Department(name="Electricity")
            db.session.add(electricity)

        roads = Department.query.filter_by(name="Roads").first()
        if not roads:
            roads = Department(name="Roads")
            db.session.add(roads)

        db.session.commit()

        # Create officers for each department
        officers = [
            ("water_officer", "password123", water),
            ("electricity_officer", "password123", electricity),
            ("roads_officer", "password123", roads)
        ]

        for username, password, dept in officers:
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            officer = Officer(username=username, password=hashed_pw, department=dept)
            db.session.add(officer)

        db.session.commit()

        return "✅ Officers and departments reset successfully!"
    except Exception as e:
        db.session.rollback()
        return f"❌ Error: {str(e)}"
    
@authority_bp.route("/wipe_officers")
def wipe_officers():
    try:
        Officer.query.delete()
        Department.query.delete()
        db.session.commit()
        return "🧹 All officers and departments deleted. Now visit /reset_officers to recreate."
    except Exception as e:
        db.session.rollback()
        return f"❌ Error while wiping: {e}"
