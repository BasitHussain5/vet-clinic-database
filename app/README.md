# Paws & Claws Veterinary Clinic - Database Application

Python 3.10+ and Flask. The database is SQLite (no server needed).

    pip install -r requirements.txt
    python init_db.py      # builds ../vet_clinic.db from schema.sql + sample_data.sql
    python app.py          # open http://127.0.0.1:5000

Features: owner and pet CRUD, appointment scheduling and schedule view, treatments,
prescriptions, invoice generation, payments, global search, pet medical history, reports.
