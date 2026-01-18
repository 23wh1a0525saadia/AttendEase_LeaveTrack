# BVRITH LeaveTrack

A web application for managing leave requests at BVRITH. Built with Flask, MySQL, and Bootstrap.

## Features

- User registration and login
- Apply for leave with permission letter upload
- View leave history
- Admin dashboard for approving/rejecting requests
- Email notifications for status updates

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bvrith-leavetrack.git
   cd bvrith-leavetrack
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up MySQL database:
   - Create a database named `leave_track`
   - Run the SQL scripts to create tables (Users, LeaveRequests, AdminCredentials)

4. Configure email settings in `app.py` (for notifications)

5. Run the app:
   ```bash
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser

## Usage

- Register as a user or admin
- Log in and apply for leave
- Admins can approve/reject requests from the dashboard

## Technologies

- Flask
- MySQL
- Bootstrap
- JavaScript

## Screenshots

- **Login Page**: Beautiful gradient background with modern form design.
- **User Dashboard**: Profile info with gradient buttons for navigation.
- **Leave Request**: Clean form with file upload for permission letters.
- **Leave History**: Responsive table showing request status.
- **Admin Dashboard**: Approve/reject requests with real-time updates.

(Add actual screenshots here)

## Contributing

Pull requests are welcome!