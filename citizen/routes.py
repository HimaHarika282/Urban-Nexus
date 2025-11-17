import os
from flask import current_app
from flask import Flask, render_template, redirect, url_for, request, flash, session
import mysql.connector
from werkzeug.utils import secure_filename
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import time
from . import citizen_bp   # import blueprint


def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="harikam@2007",
        database="smartcity_db"
    )

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- HOME ----------
@citizen_bp.route('/')
def index():
    return render_template('index.html')

# ---------- STATIC PAGES ----------
@citizen_bp.route('/about')
def about():
    return render_template('about.html')

# ---------- LOGOUT ----------
@citizen_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully!", "success")
    return redirect(url_for('index'))

# ---------- MY PROFILE ----------
@citizen_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    db=get_db()
    if "citizen_id" not in session:
        flash("Please log in to access your profile", "warning")
        return redirect(url_for("citizen_bp.citizen_login"))

    user_id = session["citizen_id"]

    cursor = db.cursor(dictionary=True)

    # Ensure upload folder exists
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder:
        # Fallback to default folder inside 'static/uploads'
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        current_app.config['UPLOAD_FOLDER'] = upload_folder

    if request.method == "POST":
        # ---------- Update basic info ----------
        name = request.form.get("name")
        dob = request.form.get("dob")
        email = request.form.get("email")
        phone_no = request.form.get("phone_no")
        address = request.form.get("address")
        zone_id = request.form.get("zone_id")

        cursor.execute("""
            UPDATE citizens
            SET name=%s, date_of_birth=%s, email=%s, phone_no=%s, address=%s, zone_id=%s
            WHERE citizen_id=%s
        """, (name, dob, email, phone_no, address, zone_id, user_id))
        db.commit()

        # ---------- Avatar handling ----------
        avatar_file = request.files.get("avatar")
        delete_avatar = request.form.get("delete_avatar")

        cursor.execute("SELECT avatar FROM citizens WHERE citizen_id=%s", (user_id,))
        user = cursor.fetchone()
        old_avatar = user.get("avatar")

        # Delete old avatar
        if delete_avatar == "on" and old_avatar:
            old_path = os.path.join(upload_folder, old_avatar)
            if os.path.exists(old_path):
                os.remove(old_path)
            cursor.execute("UPDATE citizens SET avatar=NULL WHERE citizen_id=%s", (user_id,))
            db.commit()
            flash("Avatar deleted successfully", "success")

        # Upload new avatar
        elif avatar_file and avatar_file.filename != "":
            if allowed_file(avatar_file.filename):
                ext = avatar_file.filename.rsplit(".", 1)[1].lower()
                # Use old filename if exists, else new filename based on citizen_id
                filename = old_avatar if old_avatar else f"{user_id}.{ext}"
                avatar_path = os.path.join(upload_folder, filename)
                avatar_file.save(avatar_path)
                cursor.execute("UPDATE citizens SET avatar=%s WHERE citizen_id=%s", (filename, user_id))
                db.commit()
                flash("Avatar updated successfully", "success")
            else:
                flash("Invalid file type. Allowed: png, jpg, jpeg, gif", "danger")

        cursor.close()
        return redirect(url_for('citizen_bp.profile'))

    # ---------- GET request: fetch user info ----------
    cursor.execute("SELECT * FROM citizens WHERE citizen_id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    avatar_url = url_for('static', filename='default_avatar.png')
    if user.get('avatar'):
        avatar_url = url_for('static', filename=f'uploads/{user["avatar"]}')

    return render_template("profile.html", user=user, avatar_url=avatar_url)


# ---------- CONTACT ----------
@citizen_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'citizen_id' not in session:
        flash("Please log in to send a message.", "warning")
        return redirect(url_for('citizen_bp.citizen_login'))

    citizen_id = session['citizen_id']
    db=get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT email, name FROM citizens WHERE citizen_id = %s", (citizen_id,))
    user = cursor.fetchone()

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('citizen_bp.citizen_login'))

    if request.method == 'POST':
        email = request.form['email']
        message_text = request.form['message']

        if email.strip().lower() != user['email'].lower():
            flash("Email does not match your account. Please use your registered email.", "danger")
            return redirect(url_for('citizen_bp.contact'))

        cursor.execute("INSERT INTO messages (citizen_id, message) VALUES (%s, %s)", (citizen_id, message_text))
        db.commit()
        flash("Message sent successfully!", "success")
        return redirect(url_for('citizen_bp.contact'))

    cursor.execute("""
        SELECT message, reply, created_at 
        FROM messages 
        WHERE citizen_id = %s 
        ORDER BY created_at DESC
    """, (citizen_id,))
    messages = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('contact.html', messages=messages, user=user)

# ---------- CITIZEN SIGNUP ----------
@citizen_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    db=get_db()
    if request.method == 'POST':
        name = request.form.get('name')
        dob = request.form.get('dob')
        citizen_id = request.form.get('citizen_id')
        address = request.form.get('address')
        phone = request.form.get('phone')
        zone_id = request.form.get('zone_id')
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'))

        try:
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO citizens 
                (name, date_of_birth, citizen_id, address, phone_no, zone_id, email, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, dob, citizen_id, address, phone, zone_id, email, password))
            db.commit()
            cursor.close()
            db.close()
            flash("Signup successful! You can now login.", "success")
            return redirect(url_for('citizen_bp.citizen_login'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")
            return render_template('signup.html')

    return render_template('signup.html')

# ---------- CITIZEN LOGIN ----------
@citizen_bp.route('/citizen-login', methods=['GET', 'POST'])
def citizen_login():
    db=get_db()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM citizens WHERE email=%s", (email,))
            user = cursor.fetchone()
            cursor.close()
            db.close()

            if user and check_password_hash(user['password'], password):
                session['citizen_id'] = user['citizen_id']
                session['citizen_name'] = user['name']

                flash("Login successful!", "success")
                return redirect(url_for('citizen_bp.citizen_dashboard'))
            else:
                flash("Invalid email or password", "danger")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")

    return render_template('citizen_login.html')

# ---------- CITIZEN DASHBOARD ----------
@citizen_bp.route('/citizen-dashboard')
def citizen_dashboard():
    return render_template('citizen_dashboard.html')

# ---------- AUTHORITY LOGIN ----------
@citizen_bp.route('/authority-login', methods=['GET', 'POST'])
def authority_login():
    db=get_db()
    if request.method == 'POST':
        staff_id = request.form.get('staff_id')
        department = request.form.get('department')
        password = request.form.get('password')

        if not staff_id or not department or not password:
            flash("Please fill all fields", "danger")
            return render_template('authority_login.html', show_flash=True)

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM authorities WHERE staff_id=%s", (staff_id,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if not user:
            flash("Invalid Authority ID", "danger")
            return render_template('authority_login.html', show_flash=True)

        if user['password'] != password:
            flash("Incorrect password", "danger")
            return render_template('authority_login.html', show_flash=True)

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT department_name FROM departments WHERE department_id=%s", (user['dept_id'],))
        dept = cursor.fetchone()
        cursor.close()
        db.close()

        if dept and dept['department_name'].lower() == department.lower():
            flash("Login successful!", "success")
            return redirect(url_for('citizen_bp.authority_dashboard', dept_name=department.lower()))
        else:
            flash("Department does not match your Authority ID", "danger")
            return render_template('authority_login.html', show_flash=True)

    return render_template('authority_login.html', show_flash=False)

# ---------- AUTHORITY DASHBOARD ----------
@citizen_bp.route('/authority-dashboard/<dept_name>')
def authority_dashboard(dept_name):
    valid_departments = [
        "electricity", "transport", "infrastructure",
        "water", "gas", "health", "police", "fire"
    ]
    if dept_name.lower() in valid_departments:
        return render_template(f"department_{dept_name.lower()}.html")
    else:
        flash("Invalid department", "danger")
        return redirect(url_for('citizen_bp.authority_login'))

# ---------- SERVICE REQUESTS ----------
@citizen_bp.route('/requests', methods=['GET', 'POST'])
def citizen_requests():
    db=get_db()
    cursor = db.cursor(dictionary=True)

    citizen_name = session.get('citizen_name')  # stored during login

    if request.method == 'POST':
        department_name = request.form['department']
        description = request.form['description']
        location = request.form['location']

        # Fetch department id
        cursor.execute("SELECT id FROM department WHERE name = %s", (department_name,))
        dept = cursor.fetchone()

        if dept:
            department_id = dept['id']

            # Insert request
            cursor.execute("""
                INSERT INTO request 
                (citizen_name, department_id, description, location, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (citizen_name, department_id, description, location, "Pending"))

            db.commit()

    # Fetch departments
    cursor.execute("SELECT name FROM department")
    departments = [row['name'] for row in cursor.fetchall()]

    # Fetch previous requests of this citizen (FIXED)
    cursor.execute("""
        SELECT 
            r.id,
            d.name AS department_name,
            r.description,
            r.location,
            r.status,
            r.timestamp
        FROM request r
        JOIN department d ON r.department_id = d.id
        WHERE r.citizen_name = %s
        ORDER BY r.timestamp DESC
    """, (session.get('citizen_name'),))

    requests_list = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('requests.html', departments=departments, requests=requests_list)



# ---------- EMERGENCY REQUESTS ----------
@citizen_bp.route('/emergency-requests', methods=['GET', 'POST'])
def emergency_requests():
    if 'citizen_name' not in session:
        flash("Please log in to submit emergency requests.", "warning")
        return redirect(url_for('citizen_bp.citizen_login'))

    citizen_name = session['citizen_name']
    db=get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        department_name = request.form.get('department')
        location = request.form.get('location')
        description = request.form.get('description')

        if not department_name or not location:
            flash("Please fill all required fields.", "danger")
        else:
            try:
                # Optional: map department_name to department_id if needed
                department_id_map = {'Police': 1, 'Fire': 2, 'Hospital': 3}
                department_id = department_id_map.get(department_name, None)

                cursor.execute("""
                    INSERT INTO emergency_requests
                    (citizen_name, location, description, department_id, department_name, status, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (citizen_name, location, description, department_id, department_name, 'Pending'))
                
                db.commit()
                flash("Emergency request submitted successfully!", "success")
                return redirect(url_for('citizen_bp.emergency_requests'))
            except mysql.connector.Error as err:
                db.rollback()
                flash(f"Database error: {err}", "danger")
                print(f"[DB ERROR] {err}")

    # Fetch past emergency requests
    try:
        cursor.execute("""
            SELECT id, citizen_name, location, description, department_name, status, timestamp
            FROM emergency_requests
            WHERE citizen_name = %s
            ORDER BY timestamp DESC
        """, (citizen_name,))
        emergencies = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Error fetching emergency requests: {err}", "danger")
        emergencies = []
        print(f"[DB ERROR] {err}")
    finally:
        cursor.close()
        db.close()

    return render_template('emergency_requests.html', emergencies=emergencies)


@citizen_bp.route('/transport')
def transport():
    db=get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transport_facilities")
    transports = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('transport.html', transports=transports)


# @app.route('/electricity')
# def electricity():
#     return render_template('electricity.html')

# ---------- ELECTRICITY ----------  
@citizen_bp.route('/electricity', methods=['GET'])
def electricity():
    db=get_db()
    if "citizen_id" not in session:
        flash("Please login first", "warning")
        return redirect(url_for("citizen_bp.citizen_login"))

    citizen_id = session["citizen_id"]
    cursor = db.cursor(dictionary=True)

    # Load all bills for this citizen
    cursor.execute("""
        SELECT bill_id, connection_id, billing_month, units, BillAmount, due_date, paid_date, status 
        FROM electricity_bills
        WHERE citizen_id = %s
        ORDER BY bill_id DESC
    """, (citizen_id,))
    bills = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("electricity.html", bills=bills)


# ---------- PAY BILL PAGE ----------
@citizen_bp.route('/pay_bill/<int:bill_id>', methods=['GET'])
def pay_bill(bill_id):
    db=get_db()
    if 'citizen_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('citizen_bp.citizen_login'))

    citizen_id = session['citizen_id']
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT bill_id, connection_id, billing_month, units, BillAmount, due_date, paid_date, status 
        FROM electricity_bills
        WHERE bill_id = %s AND citizen_id = %s
    """, (bill_id, citizen_id))
    bill = cursor.fetchone()
    cursor.close()
    db.close()

    if not bill:
        flash("Bill not found.", "danger")
        return redirect(url_for("citizen_bp.electricity"))

    return render_template("pay_bill.html", bill=bill)


# ---------- CONFIRM PAYMENT ----------
@citizen_bp.route('/confirm_payment/<int:bill_id>', methods=['POST'])
def confirm_payment(bill_id):
    db=get_db()
    if 'citizen_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('citizen_bp.citizen_login'))

    citizen_id = session['citizen_id']
    cursor = db.cursor()

    try:
        cursor.execute("""
            UPDATE electricity_bills
            SET status = 'Paid', paid_date = CURDATE()
            WHERE bill_id = %s AND citizen_id = %s
        """, (bill_id, citizen_id))
        db.commit()
        flash("Payment successful!", "success")

    except mysql.connector.Error as err:
        flash(str(err), "danger")
    
    cursor.close()
    db.close()
    return redirect(url_for("citizen_bp.electricity"))

@citizen_bp.route("/gas", methods=['GET', 'POST'])
def gas():
    db=get_db()
    if 'citizen_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('citizen_bp.citizen_login'))

    citizen_id = session['citizen_id']
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        # User clicked "Order Gas Cylinder"
        order_date = request.form.get('order_date')
        cost = request.form.get('cost', 800)  # default 800

        # Insert order with status 'Unpaid'
        cursor.execute("""
            INSERT INTO gas_bills (citizen_id, order_date, billamount, status)
            VALUES (%s, %s, %s, 'Unpaid')
        """, (citizen_id, order_date, cost))
        db.commit()
        

        gasbill_id = cursor.lastrowid
        cursor.close()
        db.close()

        flash("Gas Cylinder Ordered Successfully!", "success")
        return redirect(url_for('citizen_bp.pay_gas_bill', gasbill_id=gasbill_id))

    # GET: Fetch all orders for this citizen
    cursor.execute("""
        SELECT gasbill_id, order_date, delivery_date, billamount, status
        FROM gas_bills
        WHERE citizen_id=%s
        ORDER BY gasbill_id DESC
    """, (citizen_id,))
    orders = cursor.fetchall()
    cursor.close()

    return render_template("gas.html", orders=orders)

# ---------- PAY GAS BILL PAGE ----------
@citizen_bp.route('/pay_gas_bill/<int:gasbill_id>', methods=['GET'])
def pay_gas_bill(gasbill_id):
    db=get_db()
    if 'citizen_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('citizen_bp.citizen_login'))

    citizen_id = session['citizen_id']
    cursor = db.cursor(dictionary=True)

    # Get gas bill details
    cursor.execute("""
        SELECT gasbill_id, order_date, delivery_date, billamount, status
        FROM gas_bills
        WHERE gasbill_id=%s AND citizen_id=%s
    """, (gasbill_id, citizen_id))
    bill = cursor.fetchone()

    # Get citizen wallet balance
    cursor.execute("SELECT Amount FROM citizens WHERE citizen_id=%s", (citizen_id,))
    wallet = cursor.fetchone()
    cursor.close()
    db.close()

    if not bill:
        flash("Gas order not found.", "danger")
        return redirect(url_for('citizen_bp.gas'))

    return render_template("pay_gas_bill.html", bill=bill, wallet=wallet)



# ---------- CONFIRM GAS PAYMENT ----------
# ---------- CONFIRM GAS PAYMENT ----------
# ---------- CONFIRM GAS PAYMENT ----------
@citizen_bp.route('/confirm_gas_payment/<int:gasbill_id>', methods=['POST'])
def confirm_gas_payment(gasbill_id):
    db=get_db()
    if 'citizen_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('citizen_bp.citizen_login'))

    citizen_id = session['citizen_id']
    cursor = db.cursor(dictionary=True)

    try:
        # Update gas bill status to 'Paid'
        # Trigger handles wallet check & deduction
        cursor.execute("""
            UPDATE gas_bills
            SET status='Paid', delivery_date=CURDATE()
            WHERE gasbill_id=%s AND citizen_id=%s
        """, (gasbill_id, citizen_id))

        db.commit()
        flash("Payment successful! Gas will be delivered soon.", "success")

    except mysql.connector.Error as err:
        db.rollback()
        # Trigger error for insufficient balance
        if err.sqlstate == '45000':
            flash(f"Payment failed: {err.msg}", "danger")
        else:
            flash(f"Payment failed: {err}", "danger")

    finally:
        cursor.close()
        db.close()

    return redirect(url_for('citizen_bp.gas'))

@citizen_bp.route('/water')
def water():
    db=get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT area, supply_days, start_time, end_time, notes FROM water_schedule")
    rows = cursor.fetchall()
    cursor.close()
    db.close()

    # Convert TIME objects to strings
    for row in rows:
        if isinstance(row['start_time'], time):
            row['start_time'] = row['start_time'].strftime('%H:%M')
        if isinstance(row['end_time'], time):
            row['end_time'] = row['end_time'].strftime('%H:%M')

    return render_template('water.html', schedule_data=rows)




@citizen_bp.route('/utility')
def utility():
    return render_template('utility.html')

# ---------- PROPERTY MANAGEMENT ----------

@citizen_bp.route('/properties')
def properties():
    return render_template('properties.html')

# ---------- AVAILABLE PROPERTIES ----------
@citizen_bp.route('/availprop')
def availprop():
    db=get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM properties WHERE status='available'")
    properties = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('availprop.html', properties=properties)

# ---------- MY PROPERTIES (GET + UPDATE) ----------
@citizen_bp.route('/myprop', methods=['GET', 'POST'])
def myprop():
    db=get_db()
    if "citizen_id" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('citizen_bp.citizen_login'))

    citizen_id = session["citizen_id"]
    cursor = db.cursor(dictionary=True)

    # ---------- When user clicks 'Save Changes' ----------
    if request.method == "POST":
        sell_props = request.form.getlist("sell_props")  # list of checked property IDs

        # Step 1️⃣: Set all this user's properties to 'not_available'
        cursor.execute("UPDATE properties SET status = 'not_available' WHERE citizen_id = %s", (citizen_id,))

        # Step 2️⃣: Update only selected ones to 'available'
        if sell_props:
            for prop_id in sell_props:
                cursor.execute(
                    "UPDATE properties SET status = 'available' WHERE prop_id = %s AND citizen_id = %s",
                    (prop_id, citizen_id)
                )

        db.commit()
        flash("Property sale preferences updated successfully!", "success")
        cursor.close()
        db.close()
        return redirect(url_for('citizen_bp.myprop'))

    # ---------- Show user's properties ----------
    cursor.execute("SELECT * FROM properties WHERE citizen_id = %s", (citizen_id,))
    properties = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('myprop.html', properties=properties)