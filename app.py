import sqlite3
from flask import Flask, request, render_template, redirect, url_for, flash, session
import json
import threading
import os
import requests

RESEND_KEY = "re_GqUcJzPC_4dE5HsVPwGaGgfMncYh3HR4o"
print("RESEND_KEY is:", RESEND_KEY)


app = Flask(__name__)
app.secret_key = "your_secret_key"

DATABASE = "dbprojectNew.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# DATABASE
def init_db():
    """Run the schema.sql once to create tables."""
    with app.app_context():
        conn = get_db_connection()
        with open("schema.sql", "r") as f:
            conn.executescript(f.read())
        conn.close()

@app.route("/initdb")
def run_initdb():
    """Initialize database only once."""
    init_db()
    flash("Database initialized successfully!")
    return redirect(url_for("view_db"))

@app.route("/viewdb")
def view_db():
    """View all tables and data (without dropping tables)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    table_data = {}
    for table in tables:
        table_name = table['name']
        cursor.execute(f"SELECT * FROM {table_name};")
        data = cursor.fetchall()
        table_data[table_name] = data

    conn.close()
    return render_template("initdb.html", table_data=table_data)

# ROUTES

@app.route('/')
def splash():
    return render_template("logo.html")

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/about-us')
def about():
    return render_template("aboutus.html")

@app.route('/ourmission')
def mission():
    return render_template("mission.html")

@app.route('/project1')
def project1():
    return render_template("project1.html")

@app.route('/project2')
def project2():
    return render_template("project2.html")

@app.route('/project3')
def project3():
    return render_template("project3.html")

@app.route('/project4')
def project4():
    return render_template("project4.html")

@app.route('/project5')
def project5():
    return render_template("project5.html")

# EMAIL FUNCTIONS USING SENDGRID
RESEND_KEY = os.environ.get("RESEND_KEY")

def send_email(to, subject, html):
    url = "https://api.resend.com/emails"

    payload = {
        "from": "Minimo Cares <minimocares.noreply@gmail.com>",
        "to": to,
        "subject": subject,
        "html": html
    }

    headers = {
        "Authorization": f"Bearer {RESEND_KEY}",
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(url, json=payload, headers=headers)
        print("Email status:", r.status_code, r.text)
    except Exception as e:
        print("Error sending email:", e)


def send_confirmation_email(to_email, name):
    subject = "Welcome to Minimo Cares!"
    body = f"""
    Dear {name},<br><br>
    Thank you for signing up as a volunteer with Minimo Cares!<br>
    We are excited to have you join our mission.<br><br>
    Warm regards,<br>
    The Minimo Cares Team
    """
    send_email(to_email, subject, body)


def send_admin_notification(volunteer):
    subject = f"New Volunteer Registration: {volunteer['name']}"
    body = f"""
    <b>Name:</b> {volunteer['name']}<br>
    <b>Email:</b> {volunteer['email']}<br>
    <b>Phone:</b> {volunteer['phone']}<br>
    <b>Age:</b> {volunteer['age']}<br>
    <b>City:</b> {volunteer['city']}<br>
    <b>Status:</b> {volunteer['status']}<br>
    <b>Institute:</b> {volunteer['institute']}<br><br>
    <b>Reason:</b><br>{volunteer['reason']}
    """
    send_email("minimocares@gmail.com", subject, body)


# VOLUNTEER FORM
@app.route('/volunteerform', methods=['GET', 'POST'])
def volunteer_form():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        age = request.form.get('age')
        city = request.form.get('city')
        status = request.form.get('status')
        institute = request.form.get('institute')
        reason = request.form.get('reason')

        # Save to DB
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO volunteers (name, email, phone, age, city, status, institute, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, email, phone, age, city, status, institute, reason))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
            flash("There was an error saving your data. Please try again.")
            return redirect(url_for('volunteer_form'))

        # Create volunteer dict
        volunteer = {
            "name": name,
            "email": email,
            "phone": phone,
            "age": age,
            "city": city,
            "status": status,
            "institute": institute,
            "reason": reason
        }

        # Send emails asynchronously
        threading.Thread(target=send_confirmation_email, args=(email, name)).start()
        threading.Thread(target=send_admin_notification, args=(volunteer,)).start()

        flash("Thank you for joining us! A confirmation email will be sent shortly.")
        return redirect(url_for('home'))

    return render_template('form.html')

# -------------------- FAQ ROUTE -------------------- #
def calculate_similarity(user_input, faq_question):
    user_words = set(user_input.split())
    q_words = set(faq_question.split())

    overlap_score = len(user_words & q_words) / len(user_words | q_words)

    partial_score = 0
    for uw in user_words:
        for qw in q_words:
            if uw in qw or qw in uw:
                partial_score += 0.1

    keywords = ["donate", "help", "join", "volunteer", "mission"]
    keyword_score = sum(0.15 for w in user_words if w in keywords)

    final_score = (overlap_score * 0.6) + (partial_score * 0.3) + (keyword_score * 0.1)
    return final_score

@app.route('/faq', methods=['GET', 'POST'])
def faq():
    answer = None
    user_question = None

    with open("faq_data.json", "r", encoding="utf-8") as f:
        faq_data = json.load(f)

    if request.method == 'POST':
        user_question = request.form.get('question', '').strip().lower()
        if user_question:
            best_match = None
            best_score = 0
            for item in faq_data:
                score = calculate_similarity(user_question, item["question"].lower())
                if score > best_score:
                    best_score = score
                    best_match = item
            if best_score >= 0.35:
                answer = best_match["answer"]
            else:
                answer = (
                    "I’m not fully sure about this yet.<br>"
                    "Kindly contact us at minimocares@gmail.com"
                )

    return render_template("faq.html", answer=answer, question=user_question)

if __name__ == "__main__":
    #app.run(debug=True)
    app.run(debug=True, use_reloader=False)