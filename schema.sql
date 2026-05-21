-- ============================================================
-- Smart Employee Management System - Database Schema
-- ============================================================

-- Admin users table for secure login
CREATE TABLE IF NOT EXISTS admins (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT    UNIQUE NOT NULL,
    password_hash   TEXT    NOT NULL,
    full_name       TEXT    NOT NULL
);

-- Employee records table
CREATE TABLE IF NOT EXISTS employees (
    emp_id          TEXT    PRIMARY KEY,
    first_name      TEXT    NOT NULL,
    last_name       TEXT    NOT NULL,
    email           TEXT    UNIQUE NOT NULL,
    phone           TEXT,
    department      TEXT    NOT NULL,
    designation     TEXT    NOT NULL,
    salary          REAL    NOT NULL CHECK(salary >= 0),
    date_joined     DATE    DEFAULT (date('now')) NOT NULL,
    status          TEXT    DEFAULT 'Active'
                            CHECK(status IN ('Active', 'On Leave', 'Suspended', 'Terminated'))
);
