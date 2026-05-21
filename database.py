"""
database.py - Database operations for Smart Employee Management System
Handles all CRUD operations, statistics, and database initialization.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'employees.db')
SCHEMA   = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def get_db():
    """Create and return a database connection with Row factory."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def init_db():
    """Initialize the database: create tables and seed default admin."""
    conn = get_db()
    with open(SCHEMA, 'r') as f:
        conn.executescript(f.read())

    # Seed default admin if none exists
    admin = conn.execute("SELECT id FROM admins LIMIT 1").fetchone()
    if admin is None:
        conn.execute(
            "INSERT INTO admins (username, password_hash, full_name) VALUES (?, ?, ?)",
            ('admin', generate_password_hash('admin123'), 'System Administrator')
        )
        conn.commit()
        print("[DB] Default admin created -> username: admin | password: admin123")
    conn.close()


# ---------------------------------------------------------------------------
# Admin operations
# ---------------------------------------------------------------------------

def get_admin_by_username(username):
    """Fetch an admin record by username."""
    conn = get_db()
    admin = conn.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
    conn.close()
    return admin


# ---------------------------------------------------------------------------
# Employee ID generation
# ---------------------------------------------------------------------------

def get_next_emp_id():
    """Generate the next employee ID in the format EMP0001, EMP0002, ..."""
    conn = get_db()
    row = conn.execute(
        "SELECT emp_id FROM employees ORDER BY emp_id DESC LIMIT 1"
    ).fetchone()
    conn.close()

    if row is None:
        return "EMP0001"

    last_num = int(row['emp_id'].replace('EMP', ''))
    return f"EMP{last_num + 1:04d}"


# ---------------------------------------------------------------------------
# CRUD - Create
# ---------------------------------------------------------------------------

def add_employee(first_name, last_name, email, phone, department,
                 designation, salary, date_joined, status='Active'):
    """Insert a new employee record. Returns the generated emp_id."""
    emp_id = get_next_emp_id()
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO employees
               (emp_id, first_name, last_name, email, phone,
                department, designation, salary, date_joined, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (emp_id, first_name, last_name, email, phone,
             department, designation, salary, date_joined, status)
        )
        conn.commit()
        return emp_id
    except sqlite3.IntegrityError as e:
        raise ValueError(str(e))
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CRUD - Read
# ---------------------------------------------------------------------------

def get_employee(emp_id):
    """Fetch a single employee by ID."""
    conn = get_db()
    emp = conn.execute("SELECT * FROM employees WHERE emp_id = ?", (emp_id,)).fetchone()
    conn.close()
    return emp


def get_all_employees(search='', department='', status=''):
    """
    Fetch employees with optional search & filter.
    Search matches against emp_id, first_name, last_name, email.
    """
    conn = get_db()
    query = "SELECT * FROM employees WHERE 1=1"
    params = []

    if search:
        query += """ AND (emp_id LIKE ? OR first_name LIKE ?
                     OR last_name LIKE ? OR email LIKE ?)"""
        like = f"%{search}%"
        params.extend([like, like, like, like])

    if department:
        query += " AND department = ?"
        params.append(department)

    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY emp_id ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_all_departments():
    """Return a list of distinct department names."""
    conn = get_db()
    rows = conn.execute(
        "SELECT DISTINCT department FROM employees ORDER BY department"
    ).fetchall()
    conn.close()
    return [r['department'] for r in rows]


# ---------------------------------------------------------------------------
# CRUD - Update
# ---------------------------------------------------------------------------

def update_employee(emp_id, first_name, last_name, email, phone,
                    department, designation, salary, date_joined, status):
    """Update an existing employee record."""
    conn = get_db()
    try:
        conn.execute(
            """UPDATE employees SET
                first_name=?, last_name=?, email=?, phone=?,
                department=?, designation=?, salary=?, date_joined=?, status=?
               WHERE emp_id=?""",
            (first_name, last_name, email, phone,
             department, designation, salary, date_joined, status, emp_id)
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise ValueError(str(e))
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CRUD - Delete
# ---------------------------------------------------------------------------

def delete_employee(emp_id):
    """Delete an employee record permanently."""
    conn = get_db()
    conn.execute("DELETE FROM employees WHERE emp_id = ?", (emp_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Statistics & Analytics
# ---------------------------------------------------------------------------

def get_salary_stats():
    """Return salary analytics: highest, lowest, average, total count."""
    conn = get_db()
    stats = conn.execute("""
        SELECT
            COUNT(*)                    AS total_count,
            COALESCE(MAX(salary), 0)    AS max_salary,
            COALESCE(MIN(salary), 0)    AS min_salary,
            COALESCE(AVG(salary), 0)    AS avg_salary,
            COALESCE(SUM(salary), 0)    AS total_salary
        FROM employees
    """).fetchone()

    highest = conn.execute(
        "SELECT * FROM employees ORDER BY salary DESC LIMIT 1"
    ).fetchone()

    lowest = conn.execute(
        "SELECT * FROM employees WHERE salary > 0 ORDER BY salary ASC LIMIT 1"
    ).fetchone()

    conn.close()
    return {
        'total_count':  stats['total_count'],
        'max_salary':   stats['max_salary'],
        'min_salary':   stats['min_salary'],
        'avg_salary':   round(stats['avg_salary'], 2),
        'total_salary': stats['total_salary'],
        'highest_paid': dict(highest) if highest else None,
        'lowest_paid':  dict(lowest) if lowest else None,
    }


def get_department_stats():
    """Return employee count and average salary per department."""
    conn = get_db()
    rows = conn.execute("""
        SELECT
            department,
            COUNT(*)        AS emp_count,
            AVG(salary)     AS avg_salary,
            SUM(salary)     AS total_salary,
            MAX(salary)     AS max_salary,
            MIN(salary)     AS min_salary
        FROM employees
        GROUP BY department
        ORDER BY emp_count DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
