import subprocess
E = {  # entity: [(attr, type, flag)]
 "OWNER":[("owner_id","INT","PK"),("first_name","VARCHAR(40)",""),("last_name","VARCHAR(40)",""),("phone","VARCHAR(20)",""),("email","VARCHAR(100)","U"),("street / city / state / zip_code","",""),("registered_date","DATE","")],
 "PET":[("pet_id","INT","PK"),("owner_id","INT","FK"),("breed_id","INT","FK"),("pet_name","VARCHAR(40)",""),("sex","CHAR(1)",""),("birth_date","DATE",""),("color / weight_kg","",""),("microchip_no","VARCHAR(20)","U"),("status","VARCHAR(12)","")],
 "SPECIES":[("species_id","INT","PK"),("species_name","VARCHAR(40)","U")],
 "BREED":[("breed_id","INT","PK"),("species_id","INT","FK"),("breed_name","VARCHAR(60)","")],
 "VETERINARIAN":[("vet_id","INT","PK"),("first_name","VARCHAR(40)",""),("last_name","VARCHAR(40)",""),("license_no","VARCHAR(20)","U"),("specialty","VARCHAR(60)",""),("phone / email","",""),("hire_date","DATE",""),("is_active","BOOL","")],
 "APPOINTMENT":[("appointment_id","INT","PK"),("pet_id","INT","FK"),("vet_id","INT","FK"),("appt_datetime","DATETIME",""),("duration_min","INT",""),("reason","VARCHAR(200)",""),("status","VARCHAR(12)",""),("diagnosis","VARCHAR(255)",""),("notes","VARCHAR(500)","")],
 "SERVICE":[("service_id","INT","PK"),("service_name","VARCHAR(80)","U"),("category","VARCHAR(20)",""),("description","VARCHAR(255)",""),("standard_price","DECIMAL(8,2)",""),("is_active","BOOL","")],
 "TREATMENT":[("treatment_id","INT","PK"),("appointment_id","INT","FK"),("service_id","INT","FK"),("notes","VARCHAR(255)","")],
 "MEDICATION":[("medication_id","INT","PK"),("medication_name","VARCHAR(80)",""),("dosage_form","VARCHAR(30)",""),("strength","VARCHAR(30)",""),("unit_price","DECIMAL(8,2)","")],
 "PRESCRIPTION":[("prescription_id","INT","PK"),("appointment_id","INT","FK"),("medication_id","INT","FK"),("dosage_directions","VARCHAR(200)",""),("duration_days","INT",""),("quantity_dispensed","INT",""),("refills_allowed","INT","")],
 "INVOICE":[("invoice_id","INT","PK"),("appointment_id","INT","FK, U"),("owner_id","INT","FK"),("invoice_date","DATE",""),("due_date","DATE",""),("status","VARCHAR(10)","")],
 "INVOICE_LINE":[("line_id","INT","PK"),("invoice_id","INT","FK"),("treatment_id","INT","FK, U"),("prescription_id","INT","FK, U"),("quantity","INT",""),("unit_price","DECIMAL(8,2)","")],
 "PAYMENT":[("payment_id","INT","PK"),("invoice_id","INT","FK"),("payment_date","DATE",""),("amount","DECIMAL(8,2)",""),("method","VARCHAR(15)",""),("reference_no","VARCHAR(30)","")],
}
COL={"PK":"#fff3c4","FK":"#dbeafe"}
def node(n,attrs):
    rows=f'<TR><TD COLSPAN="3" BGCOLOR="#1f7a6d"><FONT COLOR="white" POINT-SIZE="13"><B>{n}</B></FONT></TD></TR>'
    for a,t,f in attrs:
        bg=COL.get(f.split(",")[0],"white")
        rows+=f'<TR><TD ALIGN="LEFT" BGCOLOR="{bg}"><FONT POINT-SIZE="10"><B>{f or "&nbsp;&nbsp;"}</B></FONT></TD><TD ALIGN="LEFT" BGCOLOR="{bg}"><FONT POINT-SIZE="10.5">{a}</FONT></TD><TD ALIGN="LEFT" BGCOLOR="{bg}"><FONT POINT-SIZE="9" COLOR="#555555">{t or "&nbsp;"}</FONT></TD></TR>'
    return f'{n} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" COLOR="#333333">{rows}</TABLE>>];'
ONE="teetee"; ZOONE="teeodot"; MANY="crowodot"; ONEMANY="crowtee"
# (parent, child, marker at parent end, marker at child end, label)
R=[("SPECIES","BREED",ONE,MANY,"classifies"),("BREED","PET",ONE,MANY,"describes"),("OWNER","PET",ONE,MANY,"owns"),
   ("PET","APPOINTMENT",ONE,MANY,"is seen in"),("VETERINARIAN","APPOINTMENT",ONE,MANY,"conducts"),
   ("APPOINTMENT","TREATMENT",ONE,MANY,"includes"),("SERVICE","TREATMENT",ONE,MANY,"is performed as"),
   ("APPOINTMENT","PRESCRIPTION",ONE,MANY,"results in"),("MEDICATION","PRESCRIPTION",ONE,MANY,"is prescribed in"),
   ("APPOINTMENT","INVOICE",ONE,ZOONE,"is billed on"),("OWNER","INVOICE",ONE,MANY,"is billed"),
   ("INVOICE","INVOICE_LINE",ONE,MANY,"itemizes"),("TREATMENT","INVOICE_LINE",ZOONE,ZOONE,"is charged by"),
   ("PRESCRIPTION","INVOICE_LINE",ZOONE,ZOONE,"is charged by"),("INVOICE","PAYMENT",ONE,MANY,"is settled by")]
d='digraph ER{graph[rankdir=LR,nodesep=0.55,ranksep=1.25,fontname="Helvetica",splines=true,pad=0.3,bgcolor=white];node[shape=plaintext,fontname="Helvetica"];edge[fontname="Helvetica",fontsize=10,color="#333333",dir=both,arrowsize=1.1,labeldistance=1.5];\n'
d+="\n".join(node(n,a) for n,a in E.items())+"\n"
for p,c,pm,cm,l in R:
    # edge p -> c : arrowtail at parent end, arrowhead at child end
    d+=f'{p} -> {c} [arrowtail={pm},arrowhead={cm},xlabel=<<FONT POINT-SIZE="10" COLOR="#444444"><I>{l}</I></FONT>>];\n'
d+="}"
open("er.dot","w").write(d)
subprocess.run(["dot","-Tpng","-Gdpi=110","er.dot","-o","er_diagram.png"],check=True)
subprocess.run(["dot","-Tsvg","er.dot","-o","er_diagram.svg"],check=True)
