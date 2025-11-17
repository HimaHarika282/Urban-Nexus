# Urban Nexus - Smart City Management System

## Project Overview

**Urban Nexus** is a comprehensive Smart City Management System that allows citizens and authorities to interact seamlessly. It integrates multiple services such as utilities, emergency requests, property management, transport facilities, and more. The system is built using **Flask**, **MySQL**, and **HTML/CSS/JS** for the frontend.

The project provides:
- Citizen portal for registration, login, and managing personal information.
- Authority portal for managing requests, monitoring services, and dashboards.
- Service requests for utilities like electricity, gas, water, transport.
- Emergency request system for police, fire, and healthcare services.
- Property management system for citizens to list or view properties.

---

## Features

### Citizen Portal
- Signup and login.
- View and update profile (with avatar upload/delete functionality).
- Submit service requests (electricity, water, gas, transport, etc.).
- Submit emergency requests (police, fire, hospital).
- View bills, pay electricity and gas bills online.
- Manage property listings (available or not available).

### Authority Portal
- Login for authority members.
- Dashboard view per department (electricity, water, police, fire, health, infrastructure, transport).
- Manage and monitor citizen requests and emergencies.

### Utilities
- Electricity, gas, and water bill management.
- Transport facilities information.
- Wallet integration for payments.

### Properties
- Dispaly information regarding current users properties. 
- Display information about the available properties.
- provides  aplatform for the user to sell their properties.

---

## Folder Structure

urban_nexus/
│
├── authority/ # Authority portal
│ ├── init.py # Blueprint initialization
│ ├── route.py # Routes for authority portal
│ ├── templates/ # Authority templates
│ └── static/ # Authority static files
│
├── citizen/ # Citizen portal
│ ├── init.py # Blueprint initialization
│ ├── route.py # Routes for citizen portal
│ ├── templates/ # Citizen templates
│ │ ├── profile.html
│ │ ├── signup.html
│ │ ├── requests.html
│ │ └── ... other pages
│ └── static/
│ └── uploads/ # Uploaded files like avatars or images
│
├── templates/ # Main templates
│ └── index.html # Homepage
│
├── app.py # Main Flask application file
├── models.py # Database models for authority tables
├── requirements.txt # Python dependencies
└── README.md # Project documentation

---

## Technologies Used

- Python 3.x  
- Flask  
- MySQL  
- SQLAlchemy (ORM)  
- HTML, CSS, JavaScript  
- Flask-Bcrypt (for password hashing)  
- Flask-Login (for authentication)

## Team Members & Roles

- **Menni Hima Harika** – Developed the **Citizen Portal** (frontend & backend), and managed citizen-related database models and dashboard                                functionalities.integrated the Citizen and Authority portals, testing and debugging.   
- **Gujjula Siri Sahasra** – Developed the **Citizen Portal** (frontend & backend), and managed citizen-related database models and dashboard                             functionalities.integration the Citizen and  Authority portal, testing and debugging.  
- **Bhavika Jaiswal** – Developed the **Authority Portal** (frontend & backend), managed authority-related database models and dashboard functionalities.

## Setup and Usage

**Note:** This guide assumes you have Python and MySQL installed on your system. You do **not** need to create a virtual environment if you want to skip it.

### 1. Clone the Repository
```bash
git clone https://github.com/HimaHarika282/Urban-Nexus.git
cd Urban-Nexus
```
### 2. Install Dependencies
->Install the required Python packages listed in requirements.txt:

```bash
pip install -r requirements.txt
```
### 3. Database Setup

->Make sure MySQL server is running.
->Create the database:
```sql
CREATE DATABASE smartcity_db;
```
->Update database credentials in app.py and citizen/route.py if needed:

```python
user="root"
password="your_mysql_password"
host="127.0.0.1"
database="smartcity_db"
```
->Create tables manually using models.py or allow your app to create tables automatically (for some ORM setups).

### 4.Running the Application
Start the Flask server:
    ```
    python app.py
    ```
  
 ->Open your browser and go to: http://127.0.0.1:5000/
  
 ->Homepage will load.
  
 ->Citizens can register and login to use the portal.
  
 ->Authority members can login using their credentials.**
  

## Usage Guide

  **Citizen Portal**
  
  Signup: Fill in name, date of birth, email, phone, address, zone, password.
  
  Profile: Update details and upload avatar.
  
  Service Requests: Submit requests for utilities, view past requests.
  
  Emergency Requests: Submit requests for police, fire, or hospital.
  
  Bills: View electricity and gas bills, make payments.
  
  Property Management: List properties for sale or view availability.
  

  **Authority Portal**
  
  Login: Use staff ID and department to login.
  
  Dashboard: View requests assigned to your department and manage statuses.

## Notes

  The project uses MySQL for storing all citizen and authority data.
  
  Uploaded avatars and other files are stored in citizen/static/uploads.
  
  Make sure the MySQL database is accessible and credentials are correctly set in app.py.
  
  All information entered by users is saved directly to the database.
  
  No virtual environment is required, but using one is recommended for Python dependency management in real deployments.
  

## Future Improvements

- Deploy the project on a cloud platform with live database access.
- Add automated email notifications for requests.
- Enhance security (HTTPS, CSRF protection, input validation).
- Mobile-friendly responsive design.

**Contact**

  For questions or support, contact:
  1. Menni Hima Harika
      Email: himaharika@282gmail.com
  2. Gujjula Siri Sahasra
      Email: sirisahasrareddy07@gmail.com
  3. Bhavika Jaiswal
      Email: bhavikajaiswal71@gmail.com
