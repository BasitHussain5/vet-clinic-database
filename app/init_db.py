"""Create vet_clinic.db from schema.sql and sample_data.sql."""
import sqlite3, os
base = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(base)
db_path = os.path.join(root, "vet_clinic.db")
if os.path.exists(db_path):
    os.remove(db_path)
con = sqlite3.connect(db_path)
for f in ("schema.sql", "sample_data.sql"):
    con.executescript(open(os.path.join(root, f), encoding="utf-8").read())
con.commit()
print("Created", db_path)
for t in ["owner","pet","veterinarian","appointment","treatment","prescription","invoice","invoice_line","payment"]:
    print(f"  {t:13s}", con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
