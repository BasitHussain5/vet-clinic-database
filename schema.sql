-- =====================================================================
-- Veterinary Clinic Management System - SQL DDL
-- Target: SQLite 3 (runs as-is); portable to MySQL / PostgreSQL with
-- the notes at the bottom of this file.
-- =====================================================================
PRAGMA foreign_keys = ON;

-- ---------- Reference / lookup tables --------------------------------
CREATE TABLE species (
    species_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    species_name    VARCHAR(40) NOT NULL UNIQUE
);

CREATE TABLE breed (
    breed_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id      INTEGER     NOT NULL,
    breed_name      VARCHAR(60) NOT NULL,
    CONSTRAINT uq_breed UNIQUE (species_id, breed_name),
    CONSTRAINT fk_breed_species FOREIGN KEY (species_id)
        REFERENCES species (species_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE service (
    service_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name    VARCHAR(80)  NOT NULL UNIQUE,
    category        VARCHAR(20)  NOT NULL
        CHECK (category IN ('Exam','Vaccination','Surgery','Dental','Laboratory','Imaging','Procedure')),
    description     VARCHAR(255),
    standard_price  DECIMAL(8,2) NOT NULL CHECK (standard_price >= 0),
    is_active       INTEGER      NOT NULL DEFAULT 1 CHECK (is_active IN (0,1))
);

CREATE TABLE medication (
    medication_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    medication_name VARCHAR(80)  NOT NULL,
    dosage_form     VARCHAR(30)  NOT NULL,
    strength        VARCHAR(30)  NOT NULL,
    unit_price      DECIMAL(8,2) NOT NULL CHECK (unit_price >= 0),
    CONSTRAINT uq_medication UNIQUE (medication_name, dosage_form, strength)
);

-- ---------- People ----------------------------------------------------
CREATE TABLE owner (
    owner_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name      VARCHAR(40)  NOT NULL,
    last_name       VARCHAR(40)  NOT NULL,
    phone           VARCHAR(20)  NOT NULL,
    email           VARCHAR(100) UNIQUE,
    street          VARCHAR(100),
    city            VARCHAR(50),
    state           CHAR(2),
    zip_code        VARCHAR(10),
    registered_date DATE         NOT NULL DEFAULT (date('now'))
);

CREATE TABLE veterinarian (
    vet_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name      VARCHAR(40)  NOT NULL,
    last_name       VARCHAR(40)  NOT NULL,
    license_no      VARCHAR(20)  NOT NULL UNIQUE,
    specialty       VARCHAR(60),
    phone           VARCHAR(20),
    email           VARCHAR(100) UNIQUE,
    hire_date       DATE         NOT NULL,
    is_active       INTEGER      NOT NULL DEFAULT 1 CHECK (is_active IN (0,1))
);

-- ---------- Patients --------------------------------------------------
CREATE TABLE pet (
    pet_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id        INTEGER      NOT NULL,          -- exactly one primary owner
    breed_id        INTEGER      NOT NULL,          -- species is reached through breed
    pet_name        VARCHAR(40)  NOT NULL,
    sex             CHAR(1)      NOT NULL CHECK (sex IN ('M','F')),
    birth_date      DATE,
    color           VARCHAR(40),
    weight_kg       DECIMAL(5,2) CHECK (weight_kg > 0),
    microchip_no    VARCHAR(20)  UNIQUE,
    status          VARCHAR(12)  NOT NULL DEFAULT 'Active'
        CHECK (status IN ('Active','Deceased','Transferred')),
    CONSTRAINT fk_pet_owner FOREIGN KEY (owner_id)
        REFERENCES owner (owner_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_pet_breed FOREIGN KEY (breed_id)
        REFERENCES breed (breed_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------- Visits ----------------------------------------------------
CREATE TABLE appointment (
    appointment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id          INTEGER      NOT NULL,
    vet_id          INTEGER      NOT NULL,
    appt_datetime   DATETIME     NOT NULL,          -- 'YYYY-MM-DD HH:MM'
    duration_min    INTEGER      NOT NULL DEFAULT 30 CHECK (duration_min > 0),
    reason          VARCHAR(200) NOT NULL,
    status          VARCHAR(12)  NOT NULL DEFAULT 'Scheduled'
        CHECK (status IN ('Scheduled','Completed','Cancelled','No-Show')),
    diagnosis       VARCHAR(255),
    notes           VARCHAR(500),
    CONSTRAINT uq_vet_slot UNIQUE (vet_id, appt_datetime),   -- no double-booking
    CONSTRAINT fk_appt_pet FOREIGN KEY (pet_id)
        REFERENCES pet (pet_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_appt_vet FOREIGN KEY (vet_id)
        REFERENCES veterinarian (vet_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE treatment (                            -- a service performed at a visit
    treatment_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id  INTEGER      NOT NULL,
    service_id      INTEGER      NOT NULL,
    notes           VARCHAR(255),
    CONSTRAINT fk_trt_appt FOREIGN KEY (appointment_id)
        REFERENCES appointment (appointment_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_trt_service FOREIGN KEY (service_id)
        REFERENCES service (service_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE prescription (                         -- a medication prescribed at a visit
    prescription_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id     INTEGER      NOT NULL,
    medication_id      INTEGER      NOT NULL,
    dosage_directions  VARCHAR(200) NOT NULL,
    duration_days      INTEGER      CHECK (duration_days > 0),
    quantity_dispensed INTEGER      NOT NULL CHECK (quantity_dispensed > 0),
    refills_allowed    INTEGER      NOT NULL DEFAULT 0 CHECK (refills_allowed BETWEEN 0 AND 12),
    CONSTRAINT fk_rx_appt FOREIGN KEY (appointment_id)
        REFERENCES appointment (appointment_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_rx_med FOREIGN KEY (medication_id)
        REFERENCES medication (medication_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------- Billing ---------------------------------------------------
CREATE TABLE invoice (
    invoice_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id  INTEGER      NOT NULL UNIQUE,   -- one invoice per visit
    owner_id        INTEGER      NOT NULL,          -- bill-to party at time of billing
    invoice_date    DATE         NOT NULL,
    due_date        DATE         NOT NULL,
    status          VARCHAR(10)  NOT NULL DEFAULT 'Issued' CHECK (status IN ('Issued','Void')),
    CONSTRAINT ck_due CHECK (due_date >= invoice_date),
    CONSTRAINT fk_inv_appt FOREIGN KEY (appointment_id)
        REFERENCES appointment (appointment_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_inv_owner FOREIGN KEY (owner_id)
        REFERENCES owner (owner_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE invoice_line (
    line_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id      INTEGER      NOT NULL,
    treatment_id    INTEGER      UNIQUE,            -- a treatment is billed at most once
    prescription_id INTEGER      UNIQUE,            -- a prescription is billed at most once
    quantity        INTEGER      NOT NULL DEFAULT 1 CHECK (quantity > 0),
    unit_price      DECIMAL(8,2) NOT NULL CHECK (unit_price >= 0),   -- price snapshot
    -- exactly one of the two billable items must be present (exclusive arc)
    CONSTRAINT ck_line_item CHECK (
        (treatment_id IS NOT NULL AND prescription_id IS NULL) OR
        (treatment_id IS NULL AND prescription_id IS NOT NULL)),
    CONSTRAINT fk_line_inv FOREIGN KEY (invoice_id)
        REFERENCES invoice (invoice_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_line_trt FOREIGN KEY (treatment_id)
        REFERENCES treatment (treatment_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_line_rx FOREIGN KEY (prescription_id)
        REFERENCES prescription (prescription_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE payment (
    payment_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id      INTEGER      NOT NULL,
    payment_date    DATE         NOT NULL,
    amount          DECIMAL(8,2) NOT NULL CHECK (amount > 0),
    method          VARCHAR(15)  NOT NULL
        CHECK (method IN ('Cash','Credit Card','Debit Card','Check','Online')),
    reference_no    VARCHAR(30),
    CONSTRAINT fk_pay_inv FOREIGN KEY (invoice_id)
        REFERENCES invoice (invoice_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------- Indexes on foreign keys / frequent searches ----------------
CREATE INDEX ix_owner_name   ON owner (last_name, first_name);
CREATE INDEX ix_pet_owner    ON pet (owner_id);
CREATE INDEX ix_pet_name     ON pet (pet_name);
CREATE INDEX ix_appt_pet     ON appointment (pet_id);
CREATE INDEX ix_appt_date    ON appointment (appt_datetime);
CREATE INDEX ix_trt_appt     ON treatment (appointment_id);
CREATE INDEX ix_rx_appt      ON prescription (appointment_id);
CREATE INDEX ix_line_invoice ON invoice_line (invoice_id);
CREATE INDEX ix_pay_invoice  ON payment (invoice_id);

-- ---------- Integrity triggers (rules a CHECK cannot express) ----------
-- A billed treatment / prescription must belong to the invoice's own visit.
CREATE TRIGGER trg_line_same_visit_trt
BEFORE INSERT ON invoice_line
WHEN NEW.treatment_id IS NOT NULL AND
     (SELECT t.appointment_id FROM treatment t WHERE t.treatment_id = NEW.treatment_id)
     <> (SELECT i.appointment_id FROM invoice i WHERE i.invoice_id = NEW.invoice_id)
BEGIN
    SELECT RAISE(ABORT, 'Treatment does not belong to the invoiced appointment');
END;

CREATE TRIGGER trg_line_same_visit_rx
BEFORE INSERT ON invoice_line
WHEN NEW.prescription_id IS NOT NULL AND
     (SELECT p.appointment_id FROM prescription p WHERE p.prescription_id = NEW.prescription_id)
     <> (SELECT i.appointment_id FROM invoice i WHERE i.invoice_id = NEW.invoice_id)
BEGIN
    SELECT RAISE(ABORT, 'Prescription does not belong to the invoiced appointment');
END;

-- A payment may not exceed the invoice's outstanding balance.
CREATE TRIGGER trg_payment_no_overpay
BEFORE INSERT ON payment
WHEN NEW.amount >
     (SELECT COALESCE(SUM(l.quantity * l.unit_price), 0) FROM invoice_line l WHERE l.invoice_id = NEW.invoice_id)
   - (SELECT COALESCE(SUM(p.amount), 0) FROM payment p WHERE p.invoice_id = NEW.invoice_id)
BEGIN
    SELECT RAISE(ABORT, 'Payment exceeds the outstanding invoice balance');
END;

-- ---------- Views (derived values are NOT stored in tables) ------------
CREATE VIEW v_invoice_summary AS
SELECT i.invoice_id, i.appointment_id, i.owner_id, i.invoice_date, i.due_date, i.status,
       COALESCE(l.total, 0)                         AS total_amount,
       COALESCE(p.paid, 0)                          AS amount_paid,
       COALESCE(l.total, 0) - COALESCE(p.paid, 0)   AS balance_due,
       CASE WHEN i.status = 'Void'                          THEN 'Void'
            WHEN COALESCE(l.total,0) = 0                    THEN 'No Charges'
            WHEN COALESCE(p.paid,0) >= COALESCE(l.total,0)  THEN 'Paid'
            WHEN COALESCE(p.paid,0) > 0                     THEN 'Partially Paid'
            ELSE 'Unpaid' END                       AS payment_status
FROM invoice i
LEFT JOIN (SELECT invoice_id, SUM(quantity * unit_price) AS total
           FROM invoice_line GROUP BY invoice_id) l ON l.invoice_id = i.invoice_id
LEFT JOIN (SELECT invoice_id, SUM(amount) AS paid
           FROM payment GROUP BY invoice_id) p ON p.invoice_id = i.invoice_id;

CREATE VIEW v_pet_profile AS
SELECT p.pet_id, p.pet_name, s.species_name, b.breed_name, p.sex, p.birth_date,
       p.weight_kg, p.status, o.owner_id, o.first_name || ' ' || o.last_name AS owner_name
FROM pet p
JOIN breed   b ON b.breed_id   = p.breed_id
JOIN species s ON s.species_id = b.species_id
JOIN owner   o ON o.owner_id   = p.owner_id;

-- Porting notes: MySQL -> AUTO_INCREMENT instead of AUTOINCREMENT, remove PRAGMA,
-- replace date('now') with CURRENT_DATE, rewrite triggers in MySQL syntax.
-- PostgreSQL -> use GENERATED ALWAYS AS IDENTITY, BOOLEAN for is_active, PL/pgSQL triggers.
