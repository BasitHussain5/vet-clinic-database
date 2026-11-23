# Veterinary Clinic Management System

Database design project: a relational database (13 tables, 3NF) for a veterinary clinic,
plus a Flask web application to use it.

## Contents
- `schema.sql` – table definitions, indexes, triggers, views
- `sample_data.sql` – sample data
- `vet_clinic.db` – ready-built SQLite database
- `app/` – Flask application
- `diagrams/` – ER diagram and conceptual model
- `screenshots/` – application screenshots

## Run the application
Requires Python 3.10+.

```
pip install flask
python app/init_db.py
python app/app.py
```
Then open http://127.0.0.1:5000

To match the demo screenshots (PowerShell):
```
$env:VET_TODAY="2026-11-22"; python app/app.py
```

## Team
- Basit Hussain
