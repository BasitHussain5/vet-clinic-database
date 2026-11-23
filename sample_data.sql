-- =====================================================================
-- Veterinary Clinic Management System - Sample Data
-- Load AFTER schema.sql.  All people and pets are fictional.
-- =====================================================================
PRAGMA foreign_keys = ON;

INSERT INTO species (species_id, species_name) VALUES
 (1,'Dog'),(2,'Cat'),(3,'Rabbit'),(4,'Bird');

INSERT INTO breed (breed_id, species_id, breed_name) VALUES
 (1,1,'Labrador Retriever'),(2,1,'German Shepherd'),(3,1,'Golden Retriever'),(4,1,'Beagle'),
 (5,1,'Dachshund'),(6,1,'Boxer'),(7,1,'Mixed Breed'),
 (8,2,'Domestic Shorthair'),(9,2,'Persian'),(10,2,'Maine Coon'),
 (11,3,'Holland Lop'),(12,4,'Cockatiel');

INSERT INTO owner (owner_id, first_name, last_name, phone, email, street, city, state, zip_code, registered_date) VALUES
 (1,'Emily','Carter','205-555-0101','emily.carter@example.com','412 Oak Street','Birmingham','AL','35203','2022-03-14'),
 (2,'Marcus','Johnson','205-555-0102','marcus.j@example.com','88 Magnolia Ave','Hoover','AL','35244','2021-07-02'),
 (3,'Priya','Patel','205-555-0103','priya.patel@example.com','1500 Highland Dr','Birmingham','AL','35205','2023-01-20'),
 (4,'Daniel','Nguyen','205-555-0104','dan.nguyen@example.com','230 Pine Ridge Rd','Vestavia Hills','AL','35216','2020-11-09'),
 (5,'Sofia','Ramirez','205-555-0105','sofia.r@example.com','77 Lakeshore Pkwy','Homewood','AL','35209','2024-02-11'),
 (6,'James','O''Neal','205-555-0106','j.oneal@example.com','9 Cedar Court','Mountain Brook','AL','35213','2022-09-30'),
 (7,'Hannah','Brooks','205-555-0107','hannah.brooks@example.com','615 Elm Street','Birmingham','AL','35204','2025-05-18'),
 (8,'Robert','Williams','205-555-0108',NULL,'301 Valley View Ln','Bessemer','AL','35020','2019-06-25');

INSERT INTO veterinarian (vet_id, first_name, last_name, license_no, specialty, phone, email, hire_date, is_active) VALUES
 (1,'Alicia','Moreno','AL-VET-10231','General Practice','205-555-0201','a.moreno@pawsclinic.example','2016-04-01',1),
 (2,'Benjamin','Hart','AL-VET-10587','Surgery','205-555-0202','b.hart@pawsclinic.example','2018-08-15',1),
 (3,'Chen','Wei','AL-VET-11044','Dentistry and Dermatology','205-555-0203','c.wei@pawsclinic.example','2020-01-06',1),
 (4,'Danielle','Foster','AL-VET-11392','Exotic Animals','205-555-0204','d.foster@pawsclinic.example','2022-06-20',1);

INSERT INTO pet (pet_id, owner_id, breed_id, pet_name, sex, birth_date, color, weight_kg, microchip_no, status) VALUES
 (1,1,1,'Buddy','M','2019-05-10','Yellow',31.50,'985112000000001','Active'),
 (2,1,8,'Luna','F','2021-02-14','Gray tabby',4.20,'985112000000002','Active'),
 (3,2,2,'Max','M','2017-09-01','Black and tan',38.00,'985112000000003','Active'),
 (4,3,3,'Bella','F','2020-06-23','Golden',29.80,'985112000000004','Active'),
 (5,3,9,'Milo','M','2018-12-05','White',4.90,'985112000000005','Active'),
 (6,4,4,'Charlie','M','2022-03-30','Tricolor',11.20,'985112000000006','Active'),
 (7,5,7,'Coco','F','2023-08-17','Brown',14.60,'985112000000007','Active'),
 (8,6,10,'Oliver','M','2020-10-12','Brown tabby',7.10,'985112000000008','Active'),
 (9,7,5,'Daisy','F','2019-04-04','Red',7.80,'985112000000009','Active'),
 (10,8,6,'Rocky','M','2018-01-19','Fawn',32.40,'985112000000010','Active'),
 (11,7,11,'Peanut','F','2024-09-09','Gray',1.80,NULL,'Active'),
 (12,5,12,'Kiwi','M','2023-03-03','Gray and yellow',0.09,NULL,'Active');

INSERT INTO service (service_id, service_name, category, description, standard_price, is_active) VALUES
 (1,'Wellness Exam','Exam','Routine physical examination',55.00,1),
 (2,'Emergency Exam','Exam','Urgent or after-hours examination',130.00,1),
 (3,'Rabies Vaccination','Vaccination','Rabies vaccine, 1 or 3 year',28.00,1),
 (4,'DHPP Vaccination','Vaccination','Canine distemper/parvo combination',35.00,1),
 (5,'FVRCP Vaccination','Vaccination','Feline combination vaccine',32.00,1),
 (6,'Dental Cleaning','Dental','Scaling and polishing under anesthesia',220.00,1),
 (7,'Spay / Neuter Surgery','Surgery','Sterilization surgery with monitoring',280.00,1),
 (8,'Blood Panel','Laboratory','Complete blood count and chemistry',95.00,1),
 (9,'X-Ray','Imaging','Radiograph, up to 2 views',120.00,1),
 (10,'Skin Scraping','Laboratory','Skin cytology / scraping',45.00,1),
 (11,'Ear Infection Treatment','Procedure','Ear cleaning and cytology',65.00,1),
 (12,'Microchip Implant','Procedure','ISO microchip implantation',50.00,1),
 (13,'Wound Care','Procedure','Wound cleaning and dressing',75.00,1),
 (14,'Fecal Test','Laboratory','Intestinal parasite screening',30.00,1);

INSERT INTO medication (medication_id, medication_name, dosage_form, strength, unit_price) VALUES
 (1,'Amoxicillin','Tablet','250 mg',0.85),
 (2,'Carprofen','Tablet','75 mg',1.20),
 (3,'Gabapentin','Capsule','100 mg',0.70),
 (4,'Otomax','Ointment','15 g tube',38.00),
 (5,'Heartgard Plus','Chewable','Medium dog',11.50),
 (6,'Apoquel','Tablet','16 mg',3.10),
 (7,'Metronidazole','Tablet','250 mg',0.65),
 (8,'Revolution Plus','Topical','Cat 2.8-5.5 kg',24.00);

INSERT INTO appointment (appointment_id, pet_id, vet_id, appt_datetime, duration_min, reason, status, diagnosis, notes) VALUES
 (1,1,1,'2026-09-08 09:00',30,'Annual wellness exam','Completed','Healthy adult dog','Weight stable'),
 (2,2,1,'2026-09-08 09:30',30,'Vaccination booster','Completed','Healthy',NULL),
 (3,3,2,'2026-09-15 10:00',45,'Limping on rear left leg','Completed','Suspected hip dysplasia','Rest and anti-inflammatory; recheck in 10 days'),
 (4,4,1,'2026-09-22 14:00',30,'Itchy skin and hair loss','Completed','Allergic dermatitis','Environmental allergy suspected'),
 (5,5,3,'2026-10-01 11:00',30,'Bad breath, drooling','Completed','Periodontal disease, stage 2','Dental cleaning recommended'),
 (6,6,1,'2026-10-06 08:30',30,'Head shaking, ear odor','Completed','Bacterial ear infection',NULL),
 (7,7,2,'2026-10-13 09:00',90,'Spay surgery','Completed','Routine sterilization','No complications'),
 (8,8,1,'2026-10-20 15:00',45,'Vomiting for two days','Completed','Gastroenteritis','Bland diet for 5 days'),
 (9,11,4,'2026-10-27 13:00',30,'Rabbit wellness check','Completed','Healthy',NULL),
 (10,10,2,'2026-11-03 10:30',30,'Cut on front paw','Completed','Laceration, left front paw','Bandage changes every 3 days'),
 (11,12,4,'2026-11-10 09:30',30,'Feather plucking','Completed','Stress-related behavior','Enrichment advice given'),
 (12,9,3,'2026-11-12 16:00',60,'Dental cleaning','Completed','Tartar build-up, cleaned',NULL),
 (13,1,1,'2026-11-17 10:00',30,'Rabies and DHPP vaccinations','Completed','Healthy',NULL),
 (14,4,1,'2026-11-10 14:00',30,'Skin recheck','Cancelled',NULL,'Owner rescheduled'),
 (15,10,2,'2026-11-18 11:00',30,'Paw bandage recheck','No-Show',NULL,'Owner did not arrive'),
 (16,3,2,'2026-11-24 10:00',30,'Hip dysplasia follow-up','Scheduled',NULL,NULL),
 (17,7,2,'2026-11-25 09:00',20,'Suture check','Scheduled',NULL,NULL),
 (18,5,3,'2026-11-30 11:00',60,'Dental cleaning','Scheduled',NULL,NULL),
 (19,2,1,'2026-12-02 09:00',30,'Annual wellness exam','Scheduled',NULL,NULL),
 (20,6,1,'2026-12-03 08:30',20,'Ear infection recheck','Scheduled',NULL,NULL);

INSERT INTO treatment (treatment_id, appointment_id, service_id, notes) VALUES
 (1,1,1,'Normal exam'),(2,1,14,'Negative'),
 (3,2,5,'Booster given'),
 (4,3,1,'Pain on hip extension'),(5,3,9,'Two views of pelvis'),
 (6,4,1,NULL),(7,4,10,'Mites ruled out'),
 (8,5,1,NULL),
 (9,6,11,'Cytology showed bacteria'),
 (10,7,7,'Surgery 52 minutes'),
 (11,8,2,'Dehydration check'),(12,8,8,'Mild elevation in liver enzymes'),
 (13,9,1,NULL),
 (14,10,13,'Sutured with 3 stitches'),
 (15,11,1,NULL),
 (16,12,6,'Two extractions not required'),
 (17,13,3,NULL),(18,13,4,NULL);

INSERT INTO prescription (prescription_id, appointment_id, medication_id, dosage_directions, duration_days, quantity_dispensed, refills_allowed) VALUES
 (1,1,5,'1 chew by mouth once monthly',6,6,0),
 (2,3,2,'1 tablet by mouth twice daily with food',14,28,1),
 (3,4,6,'1 tablet by mouth once daily',30,30,2),
 (4,5,1,'1 tablet by mouth twice daily',7,14,0),
 (5,6,4,'Apply 4 drops in affected ear twice daily',7,1,0),
 (6,7,3,'1 capsule by mouth every 12 hours for pain',5,10,0),
 (7,8,7,'1 tablet by mouth twice daily',7,14,0),
 (8,10,1,'1 tablet by mouth twice daily',10,20,0),
 (9,12,1,'1 tablet by mouth twice daily after dental work',5,10,0);

-- Invoices are issued for every completed visit (invoice_id = appointment_id here)
INSERT INTO invoice (invoice_id, appointment_id, owner_id, invoice_date, due_date, status)
SELECT a.appointment_id, a.appointment_id, p.owner_id, date(a.appt_datetime), date(a.appt_datetime, '+30 day'), 'Issued'
FROM appointment a JOIN pet p ON p.pet_id = a.pet_id
WHERE a.status = 'Completed'
ORDER BY a.appointment_id;

-- Bill every treatment at the current catalog price (price snapshot)
INSERT INTO invoice_line (invoice_id, treatment_id, quantity, unit_price)
SELECT i.invoice_id, t.treatment_id, 1, s.standard_price
FROM invoice i
JOIN treatment t ON t.appointment_id = i.appointment_id
JOIN service   s ON s.service_id     = t.service_id
ORDER BY t.treatment_id;

-- Bill every prescription: dispensed quantity x medication unit price
INSERT INTO invoice_line (invoice_id, prescription_id, quantity, unit_price)
SELECT i.invoice_id, r.prescription_id, r.quantity_dispensed, m.unit_price
FROM invoice i
JOIN prescription r ON r.appointment_id = i.appointment_id
JOIN medication   m ON m.medication_id  = r.medication_id
ORDER BY r.prescription_id;

-- Payments: full, split, partial and unpaid invoices
INSERT INTO payment (payment_id, invoice_id, payment_date, amount, method, reference_no) VALUES
 (1,1,'2026-09-08',154.00,'Credit Card','CC-4821'),
 (2,2,'2026-09-08',32.00,'Cash',NULL),
 (3,3,'2026-09-15',100.00,'Credit Card','CC-4902'),
 (4,3,'2026-10-01',108.60,'Check','CHK-1187'),
 (5,4,'2026-09-22',193.00,'Debit Card','DC-7731'),
 (6,5,'2026-10-01',66.90,'Credit Card','CC-5120'),
 (7,6,'2026-10-06',103.00,'Cash',NULL),
 (8,7,'2026-10-13',150.00,'Credit Card','CC-5288'),
 (9,7,'2026-10-20',137.00,'Online','WEB-30417'),
 (10,8,'2026-10-20',234.10,'Debit Card','DC-7894'),
 (11,9,'2026-10-27',55.00,'Credit Card','CC-5360'),
 (12,10,'2026-11-03',50.00,'Cash',NULL),
 (13,12,'2026-11-12',100.00,'Credit Card','CC-5511');
-- Invoices 10, 12 are partially paid; 11 and 13 are unpaid.
