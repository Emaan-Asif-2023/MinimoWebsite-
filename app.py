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
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        age = request.form.get('age')
        city = request.form.get('city')
        status = request.form.get('status')
        institute = request.form.get('institute')
        reason = request.form.get('reason')

        # --- Save volunteer info in database ---
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO volunteers (name, email, phone, age, city, status, institute, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, age, city, status, institute, reason))
        conn.commit()
        conn.close()

        # --- Send confirmation email ---
        send_confirmation_email(email, name)


        flash("Thank you for joining us! A confirmation email has been sent to your inbox.")
        return redirect(url_for('home'))

    return render_template('form.html')


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
                q_text = item["question"].lower()

                # Token-based similarity (word overlap)
                user_words = set(user_question.split())
                q_words = set(q_text.split())

                overlap = len(user_words & q_words)
                total = len(user_words | q_words)
                score = overlap / total if total else 0

                if score > best_score:
                    best_score = score
                    best_match = item

            # Only answer if similarity is high enough
            if best_score >= 0.4:  # ← adjust threshold here (0.4–0.5 recommended)
                answer = best_match["answer"]
            else:
                # Fallback polite response
                answer = (
                    "Hmm, I’m not sure about that yet.<br>"
                    "Please contact us at "
                    "<a href='mailto:minimocares@gmail.com' style='color:#72107a; font-weight:600;'>"
                    "minimocares@gmail.com</a> "
                    "and our team will be happy to assist you!"
                )

    return render_template("faq.html", answer=answer, question=user_question)

def send_confirmation_email(to_email, name):
    sender_email = "minimocares.noreply@gmail.com"
    sender_password = "ebjspcyuaugqmmqq"

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


if __name__ == "__main__":
    app.run(debug=True)
