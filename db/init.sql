CREATE DATABASE IF NOT EXISTS bloodbank;
USE bloodbank;

CREATE TABLE IF NOT EXISTS donors (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    age          INT NOT NULL,
    blood_type   VARCHAR(5) NOT NULL,
    phone        VARCHAR(15) NOT NULL,
    email        VARCHAR(100),
    city         VARCHAR(50),
    last_donated DATE,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blood_inventory (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    blood_type VARCHAR(5) NOT NULL UNIQUE,
    units      INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blood_requests (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    patient_name   VARCHAR(100) NOT NULL,
    blood_type     VARCHAR(5) NOT NULL,
    units_required INT NOT NULL,
    hospital       VARCHAR(150),
    contact_phone  VARCHAR(15) NOT NULL,
    urgency        ENUM('normal', 'urgent', 'critical') DEFAULT 'normal',
    status         ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    requested_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at    TIMESTAMP NULL
);

INSERT INTO blood_inventory (blood_type, units) VALUES
    ('A+',  10),
    ('A-',  10),
    ('B+',  10),
    ('B-',  10),
    ('AB+', 10),
    ('AB-', 10),
    ('O+',  10),
    ('O-',  10);
