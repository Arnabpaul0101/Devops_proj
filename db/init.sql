CREATE DATABASE IF NOT EXISTS foodbank;
USE foodbank;

CREATE TABLE IF NOT EXISTS contributors (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    age          INT NOT NULL,
    food_category   VARCHAR(50) NOT NULL,
    phone        VARCHAR(15) NOT NULL,
    email        VARCHAR(100),
    city         VARCHAR(50),
    last_contributed DATE,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS food_inventory (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    food_category VARCHAR(50) NOT NULL UNIQUE,
    units      INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agencies (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(150) NOT NULL,
    address    VARCHAR(255),
    phone      VARCHAR(15) NOT NULL,
    email      VARCHAR(100),
    city       VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS food_requests (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    beneficiary_name   VARCHAR(100) NOT NULL,
    food_category     VARCHAR(50) NOT NULL,
    units_required INT NOT NULL,
    agency       VARCHAR(150),
    agency_id    INT NULL,
    contact_phone  VARCHAR(15) NOT NULL,
    contact_email  VARCHAR(100),
    urgency        ENUM('normal', 'urgent', 'critical') DEFAULT 'normal',
    status         ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    requested_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at    TIMESTAMP NULL
);

CREATE TABLE IF NOT EXISTS inventory_history (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    food_category    VARCHAR(50) NOT NULL,
    change_amount INT NOT NULL,
    units_after   INT NOT NULL,
    reason        VARCHAR(150),
    recorded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO food_inventory (food_category, units) VALUES
    ('Rice', 20), ('Wheat', 18), ('Pulses', 15), ('Canned Food', 12),
    ('Cooking Oil', 10), ('Milk Powder', 8), ('Baby Food', 6), ('Hygiene Kits', 14);
