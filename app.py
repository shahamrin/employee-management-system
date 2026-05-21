"""
app.py - Main Flask application for Smart Employee Management System
Handles routing, authentication, session management, and CSV export.
"""

import csv
import io
from datetime import datetime
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   flash, session, Response)
from werkzeug.security import check_password_hash

import database
import analytics

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = 'emp-mgmt-secret-key-change-in-production-2024'
app.config['SESSION_COOKIE_HTTPONLY'] = True


# ---------------------------------------------------------------------------
# Authentication decorator
# ---------------------------------------------------------------------------

def login_required(f):
    """Decorator that redirects unauthenticated users to the login page."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please log in to access the dashboard.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if 'admin_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')

        admin = database.get_admin_by_username(username)
        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['full_name']
            session['admin_username'] = admin['username']
            flash(f'Welcome back, {admin["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Clear session and redirect to login."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    """Main analytics dashboard with stats and charts."""
    stats = database.get_salary_stats()
    dept_stats = database.get_department_stats()
    all_employees = database.get_all_employees()

    # Generate charts
    salary_bar = analytics.generate_salary_bar_chart(dept_stats)
    dept_pie = analytics.generate_department_pie_chart(dept_stats)
    salary_hist = analytics.generate_salary_histogram(all_employees)

    return render_template('dashboard.html',
                           stats=stats,
                           dept_stats=dept_stats,
                           salary_bar_chart=salary_bar,
                           dept_pie_chart=dept_pie,
                           salary_histogram=salary_hist)


# ---------------------------------------------------------------------------
# Employee CRUD routes
# ---------------------------------------------------------------------------

@app.route('/employees')
@login_required
def employees():
    """Employee directory with search and filter."""
    search = request.args.get('search', '').strip()
    department = request.args.get('department', '').strip()
    status = request.args.get('status', '').strip()

    emp_list = database.get_all_employees(search, department, status)
    departments = database.get_all_departments()

    return render_template('employees.html',
                           employees=emp_list,
                           departments=departments,
                           search=search,
                           selected_dept=department,
                           selected_status=status)


@app.route('/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    """Add a new employee record."""
    if request.method == 'POST':
        try:
            data = _extract_employee_form(request.form)
            emp_id = database.add_employee(**data)
            flash(f'Employee {emp_id} added successfully!', 'success')
            return redirect(url_for('employees'))
        except ValueError as e:
            flash(f'Error: {e}', 'error')
        except Exception as e:
            flash(f'Unexpected error: {e}', 'error')

    next_id = database.get_next_emp_id()
    return render_template('employee_form.html', mode='add', next_id=next_id)


@app.route('/employees/edit/<emp_id>', methods=['GET', 'POST'])
@login_required
def edit_employee(emp_id):
    """Edit an existing employee record."""
    emp = database.get_employee(emp_id)
    if not emp:
        flash('Employee not found.', 'error')
        return redirect(url_for('employees'))

    if request.method == 'POST':
        try:
            data = _extract_employee_form(request.form)
            database.update_employee(emp_id, **data)
            flash(f'Employee {emp_id} updated successfully!', 'success')
            return redirect(url_for('employees'))
        except ValueError as e:
            flash(f'Error: {e}', 'error')
        except Exception as e:
            flash(f'Unexpected error: {e}', 'error')

    return render_template('employee_form.html', mode='edit', employee=emp)


@app.route('/employees/delete/<emp_id>', methods=['POST'])
@login_required
def delete_employee_route(emp_id):
    """Delete an employee record."""
    emp = database.get_employee(emp_id)
    if not emp:
        flash('Employee not found.', 'error')
    else:
        database.delete_employee(emp_id)
        flash(f'Employee {emp_id} deleted successfully.', 'success')
    return redirect(url_for('employees'))


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------

@app.route('/employees/export')
@login_required
def export_csv():
    """Export all employees to a downloadable CSV file."""
    employees_list = database.get_all_employees()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Employee ID', 'First Name', 'Last Name', 'Email', 'Phone',
        'Department', 'Designation', 'Salary', 'Date Joined', 'Status'
    ])

    # Rows
    for emp in employees_list:
        writer.writerow([
            emp['emp_id'], emp['first_name'], emp['last_name'],
            emp['email'], emp['phone'], emp['department'],
            emp['designation'], emp['salary'], emp['date_joined'],
            emp['status']
        ])

    csv_data = output.getvalue()
    output.close()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'employees_export_{timestamp}.csv'

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_employee_form(form):
    """Extract and validate employee data from a submitted form."""
    first_name  = form.get('first_name', '').strip()
    last_name   = form.get('last_name', '').strip()
    email       = form.get('email', '').strip()
    phone       = form.get('phone', '').strip()
    department  = form.get('department', '').strip()
    designation = form.get('designation', '').strip()
    salary_str  = form.get('salary', '').strip()
    date_joined = form.get('date_joined', '').strip()
    status      = form.get('status', 'Active').strip()

    # Validation
    errors = []
    if not first_name:
        errors.append('First name is required.')
    if not last_name:
        errors.append('Last name is required.')
    if not email or '@' not in email:
        errors.append('A valid email address is required.')
    if not department:
        errors.append('Department is required.')
    if not designation:
        errors.append('Designation is required.')

    try:
        salary = float(salary_str)
        if salary < 0:
            errors.append('Salary cannot be negative.')
    except (ValueError, TypeError):
        errors.append('Salary must be a valid number.')
        salary = 0

    if not date_joined:
        date_joined = datetime.now().strftime('%Y-%m-%d')

    if errors:
        raise ValueError(' '.join(errors))

    return {
        'first_name':  first_name,
        'last_name':   last_name,
        'email':       email,
        'phone':       phone,
        'department':  department,
        'designation': designation,
        'salary':      salary,
        'date_joined': date_joined,
        'status':      status,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    database.init_db()
    app.run(debug=True, port=5000)
