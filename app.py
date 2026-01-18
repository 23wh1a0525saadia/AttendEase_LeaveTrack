from flask import Flask, request, jsonify, send_from_directory, redirect, render_template, session
from flask_cors import CORS
import mysql.connector
import os
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Session Configuration (Replace with a strong secret key)
app.secret_key = 'your_strong_secret_key_here'

# MySQL Config
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2005",
    database="leave_track"
)
cursor = db.cursor(dictionary=True)

# File Upload Config
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Email Configuration (Replace with your actual details)
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_email_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def send_email(to_email, subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, [to_email], msg.as_string())
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

def get_admin_email():
    if 'admin_id' in session:
        cursor.execute("SELECT email FROM AdminCredentials WHERE id = %s", (session['admin_id'],))
        admin_data = cursor.fetchone()
        if admin_data and 'email' in admin_data:
            return admin_data['email']
    return None

def get_user_email(user_id):
    cursor.execute("SELECT email FROM Users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    return user_data['email'] if user_data and 'email' in user_data else None

def get_user_name(user_email):
    cursor.execute("SELECT name FROM Users WHERE email = %s", (user_email,))
    user_data = cursor.fetchone()
    return user_data['name'] if user_data and 'name' in user_data else None

# ================= Routes to HTML Pages =================

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/leave')
def leave_page():
    if 'user_id' in session:
        return render_template('leave.html')
    else:
        return redirect('/') # Redirect to login if not logged in

@app.route('/history')
def history_page():
    if 'user_email' in session:
        cursor.execute("SELECT date_from, date_to, reason, status, permission_letter FROM LeaveRequests WHERE email = %s ORDER BY id DESC", (session['user_email'],))
        leaves = cursor.fetchall()
        return render_template('history.html', leaves=leaves)
    else:
        return redirect('/') # Redirect to login if not logged in

@app.route('/profile')
def profile_page():
    if 'user_email' in session:
        user_email = session['user_email']
        user_name = session.get('user_name') # Get user_name from session
        # You might fetch more user data from the database here if needed
        return render_template('profile.html', user_email=user_email, user_name=user_name)
    else:
        return redirect('/') # Redirect to login if not logged in

@app.route('/admin-login')
def admin_login_page():
    return render_template('admin_login.html')

@app.route('/admin')
def admin_dashboard_page():
    if 'admin_id' not in session:
        return redirect('/admin-login')
    cursor.execute("""
        SELECT lr.id, u.name, lr.email, lr.date_from, lr.date_to, lr.reason, lr.status, lr.permission_letter
        FROM LeaveRequests lr
        JOIN Users u ON lr.email = u.email
        ORDER BY lr.id DESC
    """)
    requests = cursor.fetchall()
    return render_template('admin_dashboard.html', leave_requests=requests)

@app.route('/admin/profile')
def admin_profile():
    if 'admin_id' in session:
        return render_template('admin_profile.html')
    else:
        return redirect('/admin-login')

@app.route('/admin-signup')
def admin_signup_page():
    return render_template('admin_signup.html')

# ================== User Authentication ==================

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        roll_no = data.get('roll_no')
        branch = data.get('branch')
        year = data.get('year')
        section = data.get('section')

        cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({'error': 'Email already registered'}), 400

        cursor.execute("""
            INSERT INTO Users (name, email, password, roll_no, branch, year, section)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, email, password, roll_no, branch, year, section))
        db.commit()
        return jsonify({'message': 'Signup successful'})
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() or request.form
        if data:
            email = data.get('email')
            password = data.get('password')

            cursor.execute("SELECT id, name, email, roll_no, branch, year, section FROM Users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()

            if user:
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                if request.form:  # Form submit, redirect
                    return redirect('/profile')
                else:  # JSON request, return JSON
                    return jsonify({'message': 'Login successful', 'user': {'name': user['name'], 'email': user['email'], 'roll_number': user['roll_no'], 'branch': user['branch'], 'year': user['year'], 'section': user['section']}})
            else:
                if request.form:
                    return redirect('/')  # Or render with error
                else:
                    return jsonify({'error': 'Invalid credentials'}), 401
        else:
            if request.form:
                return redirect('/')
            else:
                return jsonify({'error': 'No data received'}), 400
    return render_template('login.html')

# ================= Admin Authentication =================

@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.form
    username = data.get('username')
    password = data.get('password')

    cursor.execute("SELECT id, email FROM AdminCredentials WHERE username = %s AND password = %s", (username, password))
    admin_data = cursor.fetchone()

    if admin_data:
        session['admin_id'] = admin_data['id']
        session['admin_email'] = admin_data['email']
        return redirect("/admin", code=302)  # Redirect to admin dashboard after login
    else:
        return "<script>alert('Invalid admin credentials'); window.location.href='/admin-login';</script>"

# ================= Admin Signup =================

@app.route('/admin-signup', methods=['POST'])
def admin_signup():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    email = data.get('email') # Get admin's email during signup

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    # --- IMPORTANT SECURITY STEP: HASH THE PASSWORD BEFORE STORING ---
    # You should use a library like bcrypt for this in a real application
    hashed_password = password  # Replace this with actual password hashing

    try:
        cursor.execute("SELECT * FROM AdminCredentials WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({'error': 'Username already exists'}), 400

        cursor.execute("""
            INSERT INTO AdminCredentials (username, password, email)
            VALUES (%s, %s, %s)
        """, (username, hashed_password, email)) # Store email during signup
        db.commit()
        return jsonify({'message': 'Admin account created successfully'})
    except mysql.connector.Error as err:
        print(f"Error creating admin user: {err}")
        return jsonify({'error': 'Error creating admin account'}), 500

# ================= Leave Request Submission =================

@app.route('/leave', methods=['POST'])
def submit_leave():
    if 'user_email' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    email = session['user_email']
    name = session.get('user_name', 'Unknown')
    date_from = request.form.get('from')
    date_to = request.form.get('to')
    reason = request.form.get('reason')
    location = request.form.get('location')
    file = request.files['permission']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({'error': 'Error saving permission letter'}), 500

    try:
        cursor.execute("""
            INSERT INTO LeaveRequests (email, date_from, date_to, reason, location, status, permission_letter)
            VALUES (%s, %s, %s, %s, %s, 'Pending', %s)
        """, (email, date_from, date_to, reason, location, filename))
        db.commit()

        # Send email to the logged-in admin
        admin_email = session.get('admin_email') # Retrieve admin's email from session
        if admin_email:
            subject = f"New Leave Request from {name}"
            body = f"Name: {name}\nEmail: {email}\nFrom: {date_from}\nTo: {date_to}\nReason: {reason}\nLocation: {location}\nPermission Letter: {filename}"
            send_email(admin_email, subject, body)
        else:
            print("Admin email not found in session, so leave request email not sent.")

        return redirect('/history')
    except mysql.connector.Error as err:
        print(f"Database error during leave submission: {err}")
        return jsonify({'error': 'Error submitting leave request'}), 500

# ================= Update Leave Status (for AJAX) =================

@app.route('/admin/handle-request', methods=['POST'])
def handle_leave_request():
    if 'admin_id' not in session:
        return jsonify({'error': 'Admin not logged in'}), 401

    data = request.get_json()
    if not data or 'leave_id' not in data or 'status' not in data:
        return jsonify({'error': 'Invalid request data'}), 400

    leave_id = data['leave_id']
    status = data['status']

    try:
        cursor.execute("UPDATE LeaveRequests SET status = %s WHERE id = %s", (status, leave_id))
        db.commit()

        # Send email to the user about the status update
        cursor.execute("SELECT u.email, u.name FROM LeaveRequests lr JOIN Users u ON lr.email = u.email WHERE lr.id = %s", (leave_id,))
        leave_data = cursor.fetchone()
        if leave_data:
            user_email = leave_data['email']
            user_name = leave_data['name']
            subject = f"Leave Request Status Updated"
            body = f"Dear {user_name},\n\nYour leave request with ID {leave_id} has been updated to: {status}\n\nPlease log in to view the details."
            send_email(user_email, subject, body)

        return jsonify({'message': f'Leave request {leave_id} updated to {status}'}), 200
    except mysql.connector.Error as err:
        print(f"Error updating leave status: {err}")
        return jsonify({'error': 'Error updating leave status'}), 500

    

# ================= Leave History =================

@app.route('/history')
def leave_history():
    if 'user_email' in session:
        cursor.execute("SELECT date_from, date_to, reason, status, permission_letter FROM LeaveRequests WHERE email = %s ORDER BY id DESC", (session['user_email'],))
        leaves = cursor.fetchall()
        return render_template('history.html', leaves=leaves)
    else:
        return redirect('/') # Redirect if not logged in

# ================= Logout =================

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    session.pop('admin_id', None)
    session.pop('admin_email', None)
    return redirect('/') # Redirect to the login page

# =============== Serve Uploaded Files =================

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# =============== Run App =================

if __name__ == '__main__':
    app.run(debug=True)