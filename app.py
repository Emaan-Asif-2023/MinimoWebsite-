import sqlite3
from flask import Flask, request, render_template, redirect, url_for, flash, session
import json
import difflib
import smtplib
from email.mime.text import MIMEText


app = Flask(__name__)
app.secret_key = "your_secret_key"

DATABASE = "dbprojectNew.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------- INITIALIZE DATABASE -------------------- #
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


# -------------------- ROUTES -------------------- #

@app.route('/')
def splash():
    return render_template("logo.html")

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/aboutus')
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


# -------------------- VOLUNTEER FORM -------------------- #

@app.route('/volunteerform', methods=['GET', 'POST'])
def volunteer_form():
    if request.method == 'POST':
        print("Form submission received!")

        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        age = request.form.get('age')
        city = request.form.get('city')
        status = request.form.get('status')
        institute = request.form.get('institute')
        reason = request.form.get('reason')

        # Save to DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO volunteers (name, email, phone, age, city, status, institute, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, age, city, status, institute, reason))
        conn.commit()
        conn.close()

        # Confirmation email to volunteer
        send_confirmation_email(email, name)

        # NEW --- Forward details to admin
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
        send_admin_notification(volunteer)

        flash("Thank you for joining us! A confirmation email has been sent to you.")
        return redirect(url_for('home'))

    return render_template('form.html')

def calculate_similarity(user_input, faq_question):
    user_words = set(user_input.split())
    q_words = set(faq_question.split())

    # Word overlap score
    overlap_score = len(user_words & q_words) / len(user_words | q_words)

    # Partial word match: donation/donate, help/helping
    partial_score = 0
    for uw in user_words:
        for qw in q_words:
            if uw in qw or qw in uw:
                partial_score += 0.1

    # Keyword bonus scoring
    keywords = ["donate", "help", "join", "volunteer", "mission"]
    keyword_score = sum(0.15 for w in user_words if w in keywords)

    # Weighted scoring
    final_score = (overlap_score * 0.6) + (partial_score * 0.3) + (keyword_score * 0.1)

    return final_score


@app.route('/faq', methods=['GET', 'POST'])
def faq():
    answer = None
    user_question = None

    # Load the FAQ data
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

            if best_score >= 0.35:   # threshold is now more flexible
                answer = best_match["answer"]
            else:
                answer = (
                    "I’m not fully sure about this yet.<br>"
                    "Kindly contact us at "
                    "<a href='mailto:minimocares@gmail.com'>minimocares@gmail.com</a>"
                )

    return render_template("faq.html", answer=answer, question=user_question)

def send_confirmation_email(to_email, name):
    sender_email = "minimocares.noreply@gmail.com"
    sender_password = "foohlopybcodvupi"

    subject = "Welcome to Minimo Cares!"
    body = f"""Dear {name},
Thank you for signing up as a volunteer with Minimo Cares!
We are excited to have you join our mission of spreading care, compassion, and kindness.

Our team will get in touch with you soon regarding upcoming welfare activities.

Warm regards,
The Minimo Cares Team
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f" Failed to send email: {e}")

def send_admin_notification(volunteer):
    official_email = "minimocares@gmail.com"   # Your official inbox
    sender_email = "minimocares.noreply@gmail.com"
    sender_password = "foohlopybcodvupi"       # App password

    subject = f"New Volunteer Registration: {volunteer['name']}"

    body = f"""
A new volunteer has submitted their information.

Name: {volunteer['name']}
Email: {volunteer['email']}
Phone: {volunteer['phone']}
Age: {volunteer['age']}
City: {volunteer['city']}
Status: {volunteer['status']}
Institute: {volunteer['institute']}

Reason for Volunteering:
{volunteer['reason']}

"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = official_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Admin notified at {official_email}")
    except Exception as e:
        print(f"Failed to send admin notification: {e}")

if __name__ == "__main__":
    app.run(debug=True)
