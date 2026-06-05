from flask import Flask, render_template, request, jsonify
import sqlite3, os, smtplib, threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)
DB_PATH    = os.environ.get("DB_PATH", "/data/blood_bank.db")
GMAIL_USER = os.environ.get("rs3887484@gmail", "")
GMAIL_PASS = os.environ.get("amyxgbqstlyonjrg", "")
NOTIFY_TO  = os.environ.get("NOTIFY_TO", GMAIL_USER)

def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, mobile TEXT NOT NULL,
        city TEXT NOT NULL, blood_group TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def send_email(name, mobile, city, blood_group):
    if not GMAIL_USER or not GMAIL_PASS:
        return
    try:
        conn  = get_db()
        total = conn.execute("SELECT COUNT(*) as t FROM donors").fetchone()["t"]
        conn.close()
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "New Donor: " + name + " (" + blood_group + ")"
        msg["From"]    = GMAIL_USER
        msg["To"]      = NOTIFY_TO
        now  = datetime.now().strftime("%d %b %Y, %I:%M %p")
        html = """<html><body style='font-family:Arial'>
        <div style='max-width:500px;margin:auto;border:1px solid #ddd;border-radius:10px;overflow:hidden'>
        <div style='background:#c0152a;padding:20px;text-align:center'>
        <h2 style='color:white;margin:0'>New Donor Registered</h2>
        <p style='color:rgba(255,255,255,0.8);margin:5px 0 0'>""" + now + """</p></div>
        <div style='padding:20px'>
        <p><b>Name:</b> """ + name + """</p>
        <p><b>Blood Group:</b> <span style='color:#c0152a;font-size:20px;font-weight:bold'>""" + blood_group + """</span></p>
        <p><b>City:</b> """ + city.title() + """</p>
        <p><b>Mobile:</b> <a href='tel:""" + mobile + """'>""" + mobile + """</a>
           &nbsp;|&nbsp;<a href='https://wa.me/91""" + mobile + """' style='color:green'>WhatsApp</a></p>
        </div>
        <div style='background:#f4f4f4;padding:10px;text-align:center;font-size:12px;color:#888'>
        Total donors: <b style='color:#c0152a'>""" + str(total) + """</b>
        </div></div></body></html>"""
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(GMAIL_USER, GMAIL_PASS)
            s.sendmail(GMAIL_USER, NOTIFY_TO, msg.as_string())
        print("[EMAIL] Sent for " + name)
    except Exception as e:
        print("[EMAIL] Error: " + str(e))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/register", methods=["POST"])
def register_donor():
    d  = request.get_json()
    name   = d.get("name", "").strip()
    mobile = d.get("mobile", "").strip()
    city   = d.get("city", "").strip()
    bg     = d.get("blood_group", "").strip()
    if not all([name, mobile, city, bg]):
        return jsonify({"success": False, "message": "All fields are required"}), 400
    if not mobile.isdigit() or len(mobile) != 10:
        return jsonify({"success": False, "message": "Mobile number must be exactly 10 digits"}), 400
    conn = get_db()
    conn.execute("INSERT INTO donors (name,mobile,city,blood_group) VALUES (?,?,?,?)",
                 (name, mobile, city.lower(), bg))
    conn.commit()
    conn.close()
    threading.Thread(target=send_email, args=(name, mobile, city, bg), daemon=True).start()
    return jsonify({"success": True, "message": "Thank you " + name + "! You have been added to our donor list."})

@app.route("/api/search", methods=["POST"])
def search_donors():
    d    = request.get_json()
    city = d.get("city", "").strip().lower()
    bg   = d.get("blood_group", "").strip()
    if not all([city, bg]):
        return jsonify({"success": False, "message": "Please enter both city and blood group"}), 400
    conn = get_db()
    rows = conn.execute(
        "SELECT name,mobile,city,blood_group FROM donors WHERE LOWER(city)=? AND blood_group=?",
        (city, bg)).fetchall()
    conn.close()
    donors = [{"name": r["name"], "mobile": r["mobile"],
               "city": r["city"].title(), "blood_group": r["blood_group"]} for r in rows]
    return jsonify({"success": True, "donors": donors, "count": len(donors)})

@app.route("/api/stats")
def stats():
    conn   = get_db()
    total  = conn.execute("SELECT COUNT(*) as t FROM donors").fetchone()["t"]
    cities = conn.execute("SELECT COUNT(DISTINCT city) as c FROM donors").fetchone()["c"]
    row    = conn.execute(
        "SELECT blood_group FROM donors GROUP BY blood_group ORDER BY COUNT(*) DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return jsonify({"total_donors": total, "cities_covered": cities,
                    "most_common": row["blood_group"] if row else "N/A"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
