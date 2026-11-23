"""Paws & Claws Veterinary Clinic - simple database application (Flask + SQLite)."""
import os, sqlite3
from datetime import date as _date
from flask import Flask, g, render_template, request, redirect, url_for, flash

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vet_clinic.db")
app = Flask(__name__)
app.secret_key = "vet-clinic-demo"


class date:  # "today" can be pinned for demos: set VET_TODAY=2026-11-22
    @staticmethod
    def today():
        v = os.environ.get("VET_TODAY")
        return _date.fromisoformat(v) if v else _date.today()


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_):
    d = g.pop("db", None)
    if d:
        d.close()


def q(sql, args=(), one=False):
    cur = db().execute(sql, args)
    rows = cur.fetchall()
    return (rows[0] if rows else None) if one else rows


def run(sql, args=()):
    """Execute a write; return (ok, lastrowid_or_error_message)."""
    try:
        cur = db().execute(sql, args)
        db().commit()
        return True, cur.lastrowid
    except sqlite3.Error as e:
        db().rollback()
        return False, str(e)


@app.template_filter("money")
def money(v):
    return f"${(v or 0):,.2f}"


def form(*names):
    return [(request.form.get(n) or "").strip() or None for n in names]


# ------------------------------------------------------------ dashboard / reports
@app.route("/")
def dashboard():
    today = date.today().isoformat()
    stats = {
        "owners": q("SELECT COUNT(*) c FROM owner", one=True)["c"],
        "pets": q("SELECT COUNT(*) c FROM pet WHERE status='Active'", one=True)["c"],
        "upcoming": q("SELECT COUNT(*) c FROM appointment WHERE status='Scheduled' AND date(appt_datetime)>=?", (today,), True)["c"],
        "outstanding": q("SELECT COALESCE(SUM(balance_due),0) c FROM v_invoice_summary WHERE status='Issued'", one=True)["c"],
    }
    upcoming = q("""SELECT a.*, p.pet_name, v.last_name vet FROM appointment a
                    JOIN pet p USING(pet_id) JOIN veterinarian v USING(vet_id)
                    WHERE a.status='Scheduled' AND date(a.appt_datetime)>=? ORDER BY a.appt_datetime LIMIT 6""", (today,))
    return render_template("dashboard.html", stats=stats, upcoming=upcoming)


@app.route("/reports")
def reports():
    today = date.today().isoformat()
    upcoming = q("""SELECT a.appointment_id, a.appt_datetime, a.reason, p.pet_name,
                    o.first_name||' '||o.last_name owner, 'Dr. '||v.last_name vet
                    FROM appointment a JOIN pet p USING(pet_id) JOIN owner o USING(owner_id)
                    JOIN veterinarian v USING(vet_id)
                    WHERE a.status='Scheduled' AND date(a.appt_datetime)>=? ORDER BY a.appt_datetime""", (today,))
    revenue = q("""SELECT substr(payment_date,1,7) month, COUNT(*) payments, SUM(amount) total
                   FROM payment GROUP BY month ORDER BY month""")
    billed = q("""SELECT substr(invoice_date,1,7) month, SUM(total_amount) billed
                  FROM v_invoice_summary WHERE status='Issued' GROUP BY month ORDER BY month""")
    common = q("""SELECT s.service_name, s.category, COUNT(*) times, SUM(l.quantity*l.unit_price) revenue
                  FROM treatment t JOIN service s USING(service_id)
                  LEFT JOIN invoice_line l ON l.treatment_id=t.treatment_id
                  GROUP BY s.service_id ORDER BY times DESC, revenue DESC LIMIT 8""")
    unpaid = q("""SELECT i.invoice_id, i.due_date, o.first_name||' '||o.last_name owner, i.balance_due
                  FROM v_invoice_summary i JOIN owner o USING(owner_id)
                  WHERE i.balance_due>0 AND i.status='Issued' ORDER BY i.due_date""")
    vets = q("""SELECT 'Dr. '||v.first_name||' '||v.last_name vet, COUNT(*) visits
                FROM appointment a JOIN veterinarian v USING(vet_id)
                WHERE a.status='Completed' GROUP BY v.vet_id ORDER BY visits DESC""")
    return render_template("reports.html", upcoming=upcoming, revenue=revenue, billed=billed,
                           common=common, unpaid=unpaid, vets=vets)


# ------------------------------------------------------------ owners (CRUD)
@app.route("/owners")
def owners():
    s = request.args.get("q", "").strip()
    like = f"%{s}%"
    rows = q("""SELECT o.*, (SELECT COUNT(*) FROM pet p WHERE p.owner_id=o.owner_id) pets FROM owner o
                WHERE ?='' OR first_name LIKE ? OR last_name LIKE ? OR phone LIKE ? OR email LIKE ?
                ORDER BY last_name, first_name""", (s, like, like, like, like))
    return render_template("owners.html", rows=rows, s=s)


@app.route("/owners/new", methods=["GET", "POST"])
@app.route("/owners/<int:oid>/edit", methods=["GET", "POST"])
def owner_form(oid=None):
    row = q("SELECT * FROM owner WHERE owner_id=?", (oid,), True) if oid else None
    if request.method == "POST":
        v = form("first_name", "last_name", "phone", "email", "street", "city", "state", "zip_code")
        if not (v[0] and v[1] and v[2]):
            flash("First name, last name and phone are required.", "error")
        elif oid:
            ok, r = run("""UPDATE owner SET first_name=?,last_name=?,phone=?,email=?,street=?,city=?,state=?,zip_code=?
                           WHERE owner_id=?""", (*v, oid))
            if ok:
                flash("Owner updated.", "ok"); return redirect(url_for("owner_detail", oid=oid))
            flash(r, "error")
        else:
            ok, r = run("""INSERT INTO owner(first_name,last_name,phone,email,street,city,state,zip_code,registered_date)
                           VALUES (?,?,?,?,?,?,?,?,date('now'))""", v)
            if ok:
                flash("Owner added.", "ok"); return redirect(url_for("owner_detail", oid=r))
            flash(r, "error")
        row = request.form
    return render_template("owner_form.html", o=row)


@app.route("/owners/<int:oid>")
def owner_detail(oid):
    o = q("SELECT * FROM owner WHERE owner_id=?", (oid,), True)
    if not o:
        return "Owner not found", 404
    pets = q("SELECT * FROM v_pet_profile WHERE owner_id=?", (oid,))
    invs = q("SELECT * FROM v_invoice_summary WHERE owner_id=? ORDER BY invoice_date DESC", (oid,))
    return render_template("owner_detail.html", o=o, pets=pets, invs=invs)


@app.post("/owners/<int:oid>/delete")
def owner_delete(oid):
    ok, r = run("DELETE FROM owner WHERE owner_id=?", (oid,))
    if ok:
        flash("Owner deleted.", "ok"); return redirect(url_for("owners"))
    flash("Cannot delete this owner: they still have pets or billing history. (" + r + ")", "error")
    return redirect(url_for("owner_detail", oid=oid))


# ------------------------------------------------------------ pets (CRUD) + history
@app.route("/pets")
def pets():
    s = request.args.get("q", "").strip()
    like = f"%{s}%"
    rows = q("""SELECT * FROM v_pet_profile WHERE ?='' OR pet_name LIKE ? OR owner_name LIKE ?
                OR species_name LIKE ? OR breed_name LIKE ? ORDER BY pet_name""", (s, like, like, like, like))
    return render_template("pets.html", rows=rows, s=s)


@app.route("/pets/new", methods=["GET", "POST"])
@app.route("/pets/<int:pid>/edit", methods=["GET", "POST"])
def pet_form(pid=None):
    row = q("SELECT * FROM pet WHERE pet_id=?", (pid,), True) if pid else None
    if request.method == "POST":
        v = form("owner_id", "breed_id", "pet_name", "sex", "birth_date", "color", "weight_kg", "microchip_no", "status")
        v[8] = v[8] or "Active"
        if not (v[0] and v[1] and v[2] and v[3]):
            flash("Owner, breed, name and sex are required.", "error")
        elif pid:
            ok, r = run("""UPDATE pet SET owner_id=?,breed_id=?,pet_name=?,sex=?,birth_date=?,color=?,weight_kg=?,
                           microchip_no=?,status=? WHERE pet_id=?""", (*v, pid))
            if ok:
                flash("Pet updated.", "ok"); return redirect(url_for("pet_detail", pid=pid))
            flash(r, "error")
        else:
            ok, r = run("""INSERT INTO pet(owner_id,breed_id,pet_name,sex,birth_date,color,weight_kg,microchip_no,status)
                           VALUES (?,?,?,?,?,?,?,?,?)""", v)
            if ok:
                flash("Pet added.", "ok"); return redirect(url_for("pet_detail", pid=r))
            flash(r, "error")
        row = request.form
    owners_ = q("SELECT owner_id, first_name||' '||last_name name FROM owner ORDER BY last_name")
    breeds = q("SELECT b.breed_id, s.species_name||' - '||b.breed_name name FROM breed b JOIN species s USING(species_id) ORDER BY 2")
    pre = request.args.get("owner_id")
    return render_template("pet_form.html", p=row, owners=owners_, breeds=breeds, pre=pre)


@app.route("/pets/<int:pid>")
def pet_detail(pid):
    p = q("SELECT * FROM v_pet_profile WHERE pet_id=?", (pid,), True)
    if not p:
        return "Pet not found", 404
    visits = q("""SELECT a.*, 'Dr. '||v.last_name vet FROM appointment a JOIN veterinarian v USING(vet_id)
                  WHERE pet_id=? ORDER BY appt_datetime DESC""", (pid,))
    history = []
    for a in visits:
        t = q("SELECT s.service_name, t.notes FROM treatment t JOIN service s USING(service_id) WHERE appointment_id=?", (a["appointment_id"],))
        r = q("""SELECT m.medication_name||' '||m.strength med, r.dosage_directions, r.quantity_dispensed qty, r.duration_days
                 FROM prescription r JOIN medication m USING(medication_id) WHERE appointment_id=?""", (a["appointment_id"],))
        history.append((a, t, r))
    return render_template("pet_detail.html", p=p, history=history)


@app.post("/pets/<int:pid>/delete")
def pet_delete(pid):
    ok, r = run("DELETE FROM pet WHERE pet_id=?", (pid,))
    if ok:
        flash("Pet deleted.", "ok"); return redirect(url_for("pets"))
    flash("Cannot delete: this pet has appointments on record. Set its status to Deceased/Transferred instead.", "error")
    return redirect(url_for("pet_detail", pid=pid))


# ------------------------------------------------------------ appointments
@app.route("/appointments")
def appointments():
    s = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    vet = request.args.get("vet", "")
    like = f"%{s}%"
    rows = q("""SELECT a.*, p.pet_name, o.first_name||' '||o.last_name owner, 'Dr. '||v.last_name vet_name
                FROM appointment a JOIN pet p USING(pet_id) JOIN owner o USING(owner_id) JOIN veterinarian v USING(vet_id)
                WHERE (?='' OR p.pet_name LIKE ? OR o.last_name LIKE ? OR a.reason LIKE ? OR a.diagnosis LIKE ?)
                  AND (?='' OR a.status=?) AND (?='' OR a.vet_id=?)
                ORDER BY a.appt_datetime DESC""", (s, like, like, like, like, status, status, vet, vet))
    vets = q("SELECT vet_id, 'Dr. '||last_name name FROM veterinarian ORDER BY last_name")
    return render_template("appointments.html", rows=rows, s=s, status=status, vet=vet, vets=vets)


@app.route("/appointments/new", methods=["GET", "POST"])
def appointment_new():
    if request.method == "POST":
        v = form("pet_id", "vet_id", "date", "time", "duration_min", "reason")
        if not all([v[0], v[1], v[2], v[3], v[5]]):
            flash("Pet, veterinarian, date, time and reason are required.", "error")
        else:
            ok, r = run("""INSERT INTO appointment(pet_id,vet_id,appt_datetime,duration_min,reason,status)
                           VALUES (?,?,?,?,?,'Scheduled')""", (v[0], v[1], f"{v[2]} {v[3]}", v[4] or 30, v[5]))
            if ok:
                flash("Appointment scheduled.", "ok"); return redirect(url_for("appointment_detail", aid=r))
            flash("That veterinarian is already booked at this time." if "UNIQUE" in r else r, "error")
    pets_ = q("SELECT pet_id, pet_name||' ('||owner_name||')' name FROM v_pet_profile WHERE status='Active' ORDER BY pet_name")
    vets = q("SELECT vet_id, 'Dr. '||first_name||' '||last_name||' - '||COALESCE(specialty,'') name FROM veterinarian WHERE is_active=1")
    return render_template("appointment_new.html", pets=pets_, vets=vets, pre=request.args.get("pet_id"))


def appt_bundle(aid):
    a = q("""SELECT a.*, p.pet_name, p.owner_id, o.first_name||' '||o.last_name owner, 'Dr. '||v.first_name||' '||v.last_name vet_name
             FROM appointment a JOIN pet p USING(pet_id) JOIN owner o USING(owner_id) JOIN veterinarian v USING(vet_id)
             WHERE a.appointment_id=?""", (aid,), True)
    return a


@app.route("/appointments/<int:aid>")
def appointment_detail(aid):
    a = appt_bundle(aid)
    if not a:
        return "Appointment not found", 404
    treatments = q("""SELECT t.*, s.service_name, s.standard_price FROM treatment t JOIN service s USING(service_id)
                      WHERE appointment_id=?""", (aid,))
    rx = q("""SELECT r.*, m.medication_name||' '||m.strength med, m.unit_price FROM prescription r
              JOIN medication m USING(medication_id) WHERE appointment_id=?""", (aid,))
    inv = q("SELECT * FROM v_invoice_summary WHERE appointment_id=?", (aid,), True)
    services = q("SELECT * FROM service WHERE is_active=1 ORDER BY category, service_name")
    meds = q("SELECT * FROM medication ORDER BY medication_name")
    return render_template("appointment_detail.html", a=a, treatments=treatments, rx=rx, inv=inv,
                           services=services, meds=meds)


@app.post("/appointments/<int:aid>/update")
def appointment_update(aid):
    status, diagnosis, notes = form("status", "diagnosis", "notes")
    ok, r = run("UPDATE appointment SET status=?, diagnosis=?, notes=? WHERE appointment_id=?", (status, diagnosis, notes, aid))
    flash("Visit updated." if ok else r, "ok" if ok else "error")
    return redirect(url_for("appointment_detail", aid=aid))


@app.post("/appointments/<int:aid>/treatments")
def add_treatment(aid):
    sid, notes = form("service_id", "notes")
    ok, r = run("INSERT INTO treatment(appointment_id, service_id, notes) VALUES (?,?,?)", (aid, sid, notes))
    flash("Treatment recorded." if ok else r, "ok" if ok else "error")
    return redirect(url_for("appointment_detail", aid=aid))


@app.post("/appointments/<int:aid>/prescriptions")
def add_prescription(aid):
    v = form("medication_id", "dosage_directions", "duration_days", "quantity_dispensed", "refills_allowed")
    ok, r = run("""INSERT INTO prescription(appointment_id, medication_id, dosage_directions, duration_days,
                   quantity_dispensed, refills_allowed) VALUES (?,?,?,?,?,?)""",
                (aid, v[0], v[1], v[2], v[3], v[4] or 0))
    flash("Prescription recorded." if ok else r, "ok" if ok else "error")
    return redirect(url_for("appointment_detail", aid=aid))


# ------------------------------------------------------------ billing
@app.post("/appointments/<int:aid>/invoice")
def make_invoice(aid):
    """Generate an invoice from every unbilled treatment and prescription of the visit."""
    a = appt_bundle(aid)
    con = db()
    try:
        inv = q("SELECT invoice_id FROM invoice WHERE appointment_id=?", (aid,), True)
        if inv:
            iid = inv["invoice_id"]
        else:
            cur = con.execute("""INSERT INTO invoice(appointment_id, owner_id, invoice_date, due_date, status)
                                 VALUES (?,?,date('now'),date('now','+30 day'),'Issued')""", (aid, a["owner_id"]))
            iid = cur.lastrowid
        n1 = con.execute("""INSERT INTO invoice_line(invoice_id, treatment_id, quantity, unit_price)
                            SELECT ?, t.treatment_id, 1, s.standard_price FROM treatment t JOIN service s USING(service_id)
                            WHERE t.appointment_id=? AND t.treatment_id NOT IN
                                  (SELECT treatment_id FROM invoice_line WHERE treatment_id IS NOT NULL)""", (iid, aid)).rowcount
        n2 = con.execute("""INSERT INTO invoice_line(invoice_id, prescription_id, quantity, unit_price)
                            SELECT ?, r.prescription_id, r.quantity_dispensed, m.unit_price FROM prescription r
                            JOIN medication m USING(medication_id)
                            WHERE r.appointment_id=? AND r.prescription_id NOT IN
                                  (SELECT prescription_id FROM invoice_line WHERE prescription_id IS NOT NULL)""", (iid, aid)).rowcount
        con.commit()
        flash(f"Invoice #{iid} ready ({n1 + n2} new line(s) added).", "ok")
        return redirect(url_for("invoice_detail", iid=iid))
    except sqlite3.Error as e:
        con.rollback(); flash(str(e), "error")
        return redirect(url_for("appointment_detail", aid=aid))


@app.route("/invoices")
def invoices():
    rows = q("""SELECT i.*, o.first_name||' '||o.last_name owner FROM v_invoice_summary i JOIN owner o USING(owner_id)
                ORDER BY i.invoice_date DESC, i.invoice_id DESC""")
    return render_template("invoices.html", rows=rows)


@app.route("/invoices/<int:iid>")
def invoice_detail(iid):
    inv = q("""SELECT i.*, o.first_name||' '||o.last_name owner, o.street, o.city, o.state, o.zip_code, p.pet_name
               FROM v_invoice_summary i JOIN owner o USING(owner_id)
               JOIN appointment a ON a.appointment_id=i.appointment_id JOIN pet p ON p.pet_id=a.pet_id
               WHERE i.invoice_id=?""", (iid,), True)
    if not inv:
        return "Invoice not found", 404
    lines = q("""SELECT l.*, l.quantity*l.unit_price amount,
                 COALESCE(s.service_name, m.medication_name||' '||m.strength) description
                 FROM invoice_line l
                 LEFT JOIN treatment t ON t.treatment_id=l.treatment_id LEFT JOIN service s ON s.service_id=t.service_id
                 LEFT JOIN prescription r ON r.prescription_id=l.prescription_id LEFT JOIN medication m ON m.medication_id=r.medication_id
                 WHERE l.invoice_id=? ORDER BY l.line_id""", (iid,))
    pays = q("SELECT * FROM payment WHERE invoice_id=? ORDER BY payment_date, payment_id", (iid,))
    return render_template("invoice_detail.html", inv=inv, lines=lines, pays=pays, today=date.today().isoformat())


@app.post("/invoices/<int:iid>/payments")
def add_payment(iid):
    pdate, amount, method, ref = form("payment_date", "amount", "method", "reference_no")
    ok, r = run("INSERT INTO payment(invoice_id,payment_date,amount,method,reference_no) VALUES (?,?,?,?,?)",
                (iid, pdate, amount, method, ref))
    flash("Payment recorded." if ok else r, "ok" if ok else "error")
    return redirect(url_for("invoice_detail", iid=iid))


# ------------------------------------------------------------ global search
@app.route("/search")
def search():
    s = request.args.get("q", "").strip()
    like = f"%{s}%"
    res = {"owners": [], "pets": [], "appointments": []}
    if s:
        res["owners"] = q("""SELECT owner_id, first_name||' '||last_name name, phone, email FROM owner
                             WHERE first_name LIKE ? OR last_name LIKE ? OR phone LIKE ? OR email LIKE ?""", (like,) * 4)
        res["pets"] = q("""SELECT pet_id, pet_name, species_name, breed_name, owner_name FROM v_pet_profile
                           WHERE pet_name LIKE ? OR breed_name LIKE ? OR owner_name LIKE ?""", (like,) * 3)
        res["appointments"] = q("""SELECT a.appointment_id, a.appt_datetime, a.status, a.reason, p.pet_name
                                   FROM appointment a JOIN pet p USING(pet_id)
                                   WHERE p.pet_name LIKE ? OR a.reason LIKE ? OR a.diagnosis LIKE ?
                                   ORDER BY a.appt_datetime DESC""", (like,) * 3)
    return render_template("search.html", s=s, res=res)


if __name__ == "__main__":
    if not os.path.exists(DB):
        raise SystemExit("Database not found. Run: python init_db.py")
    app.run(debug=False, port=5000)
