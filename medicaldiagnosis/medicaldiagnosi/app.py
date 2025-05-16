# app.py

import os
import sqlite3
import hashlib
from datetime import datetime
from pyswip import Prolog
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import matplotlib
matplotlib.use('Agg') # Non-interactive backend for Matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, send_from_directory, make_response, g)

# --- Flask App Initialization ---
app = Flask(__name__)
app.secret_key = os.urandom(24) # Important for session management
app.config['REPORTS_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'diagnosis_reports')
app.config['PROLOG_FILE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'diagnosis.pl')
app.config['DATABASE_FILE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'diagnosis_history.db')

# Ensure reports directory exists
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

# --- Constants & Global Lists (from your original code) ---
# (Keep bg_color, frame_color etc. if you plan to use them for CSS variable inspiration)
symptom_categories = {
    "General": ["fever", "fatigue", "chills", "body ache", "weight loss", "night sweats", "loss of appetite", "high fever", "tiredness", "weakness", "pale skin", "cold hands/feet", "joint pain"],
    "Head & Neck": ["headache", "sore throat", "sneezing", "runny nose", "loss of taste", "dizziness", "blurred vision", "facial pain", "nasal congestion", "itchy eyes", "light sensitivity", "aura"],
    "Respiratory": ["cough", "shortness of breath", "wheezing", "chest tightness", "difficulty breathing", "persistent cough", "mucus", "bleeding"],
    "Digestive": ["nausea", "vomiting", "abdominal pain", "constipation", "jaundice", "dark urine", "diarrhea", "abdominal cramps", "infrequent bowel", "hard stool", "bloating"],
    "Skin": ["rash"],
    "Urinary": ["frequent urination", "increased thirst", "burning urination", "pelvic pain"]
}
all_symptoms_for_vars = sorted(list(set(symptom for sublist in symptom_categories.values() for symptom in sublist)))

all_risk_factors = [
    "obesity", "family_history", "sedentary lifestyle", "poor diet", "stress", "high salt intake",
    "alcohol", "smoking", "crowded places", "no mask", "poor immunity", "mosquito bites",
    "stagnant water", "malnutrition", "hiv positive", "overcrowding", "unprotected sex",
    "shared needles", "blood transfusion", "iron deficiency", "chronic disease", "blood loss",
    "allergies", "cold weather", "contaminated food", "poor hygiene", "dust", "pollen",
    "animal dander", "low fiber diet", "dehydration", "inactivity"
]
unique_risk_factors = sorted(list(set(all_risk_factors)))

# Matplotlib Styling (can be set globally if needed for server-side generation)
mpl.rcParams.update({'font.size': 10, 'axes.titlesize': 14, 'axes.labelsize': 12, 'xtick.labelsize': 10, 'ytick.labelsize': 10})
plt.style.use('seaborn-v0_8-pastel')

# Add this to app.py for current year in footer
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}
# --- Database Handling ---
def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE_FILE'])
        g.db.row_factory = sqlite3.Row # Access columns by name
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database schema."""
    db = get_db()
    cursor = db.cursor()
    # User table schema
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     email TEXT NOT NULL UNIQUE,
                     password_hash TEXT NOT NULL,
                     age INTEGER,
                     weight INTEGER,
                     medical_conditions TEXT)''')
    # History table schema
    cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER,
                     datetime TEXT,
                     symptoms TEXT,
                     diagnosis TEXT,
                     confidence REAL,
                     report_filename TEXT,
                     FOREIGN KEY(user_id) REFERENCES users(id))''')
    db.commit()
    print("Database initialized or schema checked.")

# Run schema update check on startup (Flask specific way)
with app.app_context():
    init_db()
    # You can keep your more detailed update_schema logic here if complex migrations are needed,
    # but for simplicity, init_db with CREATE IF NOT EXISTS is often enough for starting.

# --- Password Hashing Functions (from your original code) ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, provided_password):
    return stored_hash == hash_password(provided_password)

# --- Database Functions (adapted for Flask, using get_db()) ---
def add_user_db(name, email, password, age=None, weight=None, medical_conditions=None):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE email=?", (email,))
        if cursor.fetchone():
            return None # Email already registered
        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO users (name, email, password_hash, age, weight, medical_conditions) VALUES (?, ?, ?, ?, ?, ?)",
                       (name, email, hashed_pw, age, weight, medical_conditions))
        db.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        db.rollback()
        return None # Should be caught by the email check, but good fallback
    except Exception:
        db.rollback()
        return None

def update_user_details_db(user_id, age, weight, medical_conditions):
    db = get_db()
    cursor = db.cursor()
    try:
        conditions_to_store = medical_conditions if medical_conditions else "None"
        cursor.execute("UPDATE users SET age = ?, weight = ?, medical_conditions = ? WHERE id = ?",
                       (age, weight, conditions_to_store, user_id))
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False

def authenticate_user_db(email, password):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id, password_hash FROM users WHERE email=?", (email,))
        result = cursor.fetchone()
        if result:
            user_id, stored_hash = result['id'], result['password_hash']
            if verify_password(stored_hash, password):
                return user_id
        return None # Incorrect email or password
    except Exception:
        return None

def get_user_details_db(user_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id, name, email, age, weight, medical_conditions FROM users WHERE id=?", (user_id,))
        return cursor.fetchone() # Returns a Row object or None
    except Exception:
        return None

def add_diagnosis_db(user_id, symptoms, diagnosis, confidence, report_filename):
    db = get_db()
    cursor = db.cursor()
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO history (user_id, datetime, symptoms, diagnosis, confidence, report_filename) VALUES (?, ?, ?, ?, ?, ?)",
                       (user_id, current_time, symptoms, diagnosis, confidence, report_filename))
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False

def get_user_history_db(user_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id, datetime, symptoms, diagnosis, confidence, report_filename FROM history WHERE user_id = ? ORDER BY datetime DESC", (user_id,))
        return cursor.fetchall() # Returns a list of Row objects
    except Exception:
        return []

# --- PDF Generation (largely the same, but use app.config and no messagebox) ---
# --- PDF Generation (largely the same, but use app.config and no messagebox) ---
# --- PDF Generation (compatible with original PyFPDF API) ---
def generate_pdf_report(filename_base, user_details_row, diagnosis_info):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Helvetica", size=12)

    # Title
    pdf.set_font("Helvetica", 'B', 16)
    # ln=1 moves to the beginning of the next line after this cell
    pdf.cell(0, 10, txt="Medical Diagnosis Report", align='C', ln=1)
    pdf.ln(5)  # Additional spacing

    # Report Generated Time
    pdf.set_font("Helvetica", size=10)
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 10, txt=f"Report Generated: {report_time}", align='R', ln=1)
    pdf.ln(5)  # Additional spacing

    # Patient Information Section Title
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, txt="Patient Information", ln=1)
    pdf.set_font("Helvetica", size=12)

    if user_details_row:
        name = user_details_row['name']
        age = user_details_row['age']
        weight = user_details_row['weight']
        conditions = user_details_row['medical_conditions']

        pdf.cell(0, 8, txt=f"Name: {name}", ln=1)
        pdf.cell(0, 8, txt=f"Age: {age or 'N/A'}", ln=1)
        pdf.cell(0, 8, txt=f"Weight: {f'{weight} kg' if weight else 'N/A'}", ln=1)

        conditions_display = 'None'
        if conditions and conditions.strip().lower() == 'normal':
            conditions_display = 'Normal (No pre-existing)'
        elif conditions and conditions.strip().lower() != 'none': # Ensure this logic is as intended
            conditions_display = conditions.strip()
        # PyFPDF multi_cell: ln=1 is default, moves to next line, left margin.
        # Removed new_x, new_y from multi_cell as they are fpdf2 specific.
        # align='L' (left) is a common explicit choice if 'J' (justify) isn't desired. PyFPDF defaults to 'J'.
        pdf.multi_cell(0, 8, txt=f"Reported Conditions: {conditions_display}", border=0, align='L')
    else:
        pdf.cell(0, 8, txt="User details not found.", ln=1)

    pdf.ln(5) # This provides spacing *after* the patient details block or "not found" message.

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, txt="Reported Symptoms", ln=1)
    pdf.set_font("Helvetica", size=12)
    symptoms_list = diagnosis_info.get('symptoms', [])
    symptoms_str = ", ".join(s.replace("_", " ").title() for s in symptoms_list) if isinstance(symptoms_list, list) else "Symptoms data invalid."
    pdf.multi_cell(0, 8, txt=symptoms_str, align='L') # Using align='L' for consistency
    pdf.ln(5)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, txt="Diagnosis Outcome", ln=1)
    pdf.set_font("Helvetica", size=12)
    disease = str(diagnosis_info.get('disease', 'N/A')).replace('_', ' ').title()
    confidence = diagnosis_info.get('confidence', 0.0)
    test_rec = str(diagnosis_info.get('test', 'N/A')).replace('_', ' ').title()

    pdf.cell(0, 8, txt=f"Possible Diagnosis: {disease}", ln=1)
    pdf.cell(0, 8, txt=f"Confidence: {float(confidence):.2f}%", ln=1)
    pdf.cell(0, 8, txt=f"Recommended Test: {test_rec}", ln=1)
    pdf.ln(5)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, txt="Suggested Treatment", ln=1)
    pdf.set_font("Helvetica", size=12)
    treatment_list = diagnosis_info.get('treatment', [])
    treatment_items = [str(item).replace('_', ' ').title() for item in treatment_list] if isinstance(treatment_list, list) else []
    treatment_str = "- " + "\n- ".join(treatment_items) if treatment_items else "N/A"
    pdf.multi_cell(0, 8, txt=treatment_str, align='L')
    pdf.ln(5)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, txt="General Advice", ln=1)
    pdf.set_font("Helvetica", size=12)
    advice_txt_val = diagnosis_info.get('advice', 'Follow general medical advice.') # Renamed variable to avoid potential confusion
    pdf.multi_cell(0, 8, txt=str(advice_txt_val), align='L')
    pdf.ln(5)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, txt="Personalized Advice", ln=1)
    pdf.set_font("Helvetica", size=12)
    personalized = diagnosis_info.get('personalized_advice', '').strip()
    pdf.multi_cell(0, 8, txt=str(personalized), align='L')
    pdf.ln(10)

    pdf.set_font("Helvetica", 'I', 10)
    disclaimer_text = ("Disclaimer: This system provides potential diagnoses based on symptoms and is not a substitute for professional medical advice. Always consult a qualified healthcare provider for any health concerns.")
    pdf.multi_cell(0, 8, txt=disclaimer_text, align='L')

    safe_base_filename = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in os.path.basename(filename_base))
    full_path = os.path.join(app.config['REPORTS_FOLDER'], safe_base_filename)
    try:
        pdf.output(name=full_path) # For PyFPDF, 'name' is correct. For fpdf2, it also accepts 'dest'.
        return full_path
    except Exception as e:
        print(f"PDF Error: {e}") # Log error
        return None
# --- Personalized Advice (can be used as is, ensure user_id is passed) ---
def personalized_advice(user_id, diagnosis_atom_str):
    user_details = get_user_details_db(user_id)
    advice_list = []
    if user_details and user_details['medical_conditions'] and user_details['medical_conditions'].lower() != 'none':
        conditions = user_details['medical_conditions'].lower()
        diag_lower = str(diagnosis_atom_str).lower()
        if 'diabetes' in conditions and 'sugar' not in diag_lower: advice_list.append("With diabetes, monitor blood sugar.")
        if 'hypertension' in conditions: advice_list.append("With hypertension, track blood pressure.")
        if 'asthma' in conditions and ('breath' in diag_lower or 'wheezing' in diag_lower): advice_list.append("With asthma, keep inhaler handy.")
    if advice_list: return "\nPersonalized Notes:\n- " + "\n- ".join(advice_list)
    else: return "\nNo specific personalized notes. Follow general advice."


# --- Helper for Prolog Interaction ---
# --- Helper for Prolog Interaction ---
# --- Helper for Prolog Interaction ---
def query_prolog(query_string):
    prolog = Prolog() # A new instance for each query is generally safer for web apps
    prolog_file_path = app.config['PROLOG_FILE']

    if not os.path.exists(prolog_file_path):
        flash("Critical Error: Prolog knowledge base file not found.", "danger")
        print(f"CRITICAL ERROR: Prolog file not found at '{prolog_file_path}'")
        return None

    # Convert path to use forward slashes, suitable for Prolog strings
    prolog_consult_path = prolog_file_path.replace("\\", "/")
    # Escape single quotes in the path for the Prolog string, just in case (though unlikely for paths)
    prolog_consult_path_for_goal = prolog_consult_path.replace("'", "''")

    consult_goal = f"consult('{prolog_consult_path_for_goal}')"
    consult_successful = False

    try:
        print(f"Attempting Prolog consult with goal: {consult_goal}")
        # Execute the consult as a query. list() consumes the generator.
        # If consult fails, it should raise an exception caught below.
        list(prolog.query(consult_goal))
        consult_successful = True # If no exception, assume consult worked

        # Now execute the actual query
        print(f"Consult appeared successful. Executing query: {query_string}")
        results = list(prolog.query(query_string))
        return results

    except Exception as e:
        # This will catch exceptions from both consult and the subsequent query
        error_message = f"Prolog error. Consult goal: '{consult_goal}'. Query: '{query_string}'. Exception: {e}"
        print(error_message)
        if not consult_successful:
            flash("Critical error: Could not load the Prolog knowledge base. Please check server logs.", "danger")
        else: # Error was in the main query after a successful consult
            flash("Error processing your request with the knowledge base. Please check server logs.", "danger")
        return None

# --- Flask Routes ---

# Decorator for routes that require login
from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to be logged in to access this page.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('diagnose_form'))
    return redirect(url_for('welcome'))

@app.route('/welcome')
def welcome():
    if 'user_id' in session: # If already logged in, redirect to diagnosis
        return redirect(url_for('diagnose_form'))
    return render_template('welcome.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('diagnose_form'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not all([name, email, password, confirm_password]):
            flash("All fields are required.", "danger")
            return render_template('register.html', name=name, email=email)
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html', name=name, email=email)
        if "@" not in email or "." not in email.split('@')[-1]: # Basic email validation
            flash("Invalid email format.", "danger")
            return render_template('register.html', name=name, email=email)

        user_id = add_user_db(name, email, password)
        if user_id:
            flash(f"User '{name}' registered successfully! Please login.", "success")
            return redirect(url_for('login'))
        else:
            flash("Email already registered or database error.", "danger")
            return render_template('register.html', name=name, email=email)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('diagnose_form'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash("Email and Password are required.", "danger")
            return render_template('login.html', email=email)

        user_id = authenticate_user_db(email, password)
        if user_id:
            session['user_id'] = user_id
            user_details = get_user_details_db(user_id)
            session['user_name'] = user_details['name'] if user_details else "User"
            flash(f"Welcome back, {session['user_name']}!", "success")

            # Check if age or weight are missing, redirect to complete profile
            if user_details and (user_details['age'] is None or user_details['weight'] is None):
                flash("Please complete your profile information.", "info")
                return redirect(url_for('complete_profile'))
            return redirect(url_for('diagnose_form'))
        else:
            flash("Invalid email or password.", "danger")
            return render_template('login.html', email=email)
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('welcome'))

@app.route('/profile/complete', methods=['GET', 'POST'])
@login_required
def complete_profile():
    user_id = session['user_id']
    user_details = get_user_details_db(user_id)
    if not user_details:
        flash("User not found.", "danger")
        return redirect(url_for('logout'))

    # If profile is already complete, redirect away
    if user_details['age'] is not None and user_details['weight'] is not None:
         return redirect(url_for('diagnose_form'))

    if request.method == 'POST':
        try:
            age = int(request.form.get('age', '').strip())
            weight = int(request.form.get('weight', '').strip())
            medical_conditions = request.form.get('medical_conditions', '').strip()
            if age <= 0 or weight <= 0:
                flash("Age and Weight must be positive numbers.", "danger")
                raise ValueError("Invalid age or weight")
        except ValueError:
            flash("Invalid input for Age or Weight.", "danger")
            return render_template('complete_profile.html', user_name=user_details['name'])

        if update_user_details_db(user_id, age, weight, medical_conditions if medical_conditions else "None"):
            flash("Profile details saved successfully!", "success")
            return redirect(url_for('diagnose_form'))
        else:
            flash("Failed to update profile. Please try again.", "danger")
    return render_template('complete_profile.html', user_name=user_details['name'])


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user_id = session['user_id']
    user_details = get_user_details_db(user_id)
    if not user_details:
        flash("User not found. Please login again.", "danger")
        return redirect(url_for('logout'))

    if request.method == 'POST':
        try:
            age = int(request.form.get('age', '').strip())
            weight = int(request.form.get('weight', '').strip())
            medical_conditions = request.form.get('medical_conditions', '').strip()
            if age <= 0 or weight <= 0:
                flash("Age and Weight must be positive numbers.", "danger")
                raise ValueError("Invalid age or weight")
        except ValueError:
            flash("Invalid input for Age or Weight.", "danger")
            return render_template('edit_profile.html', user=user_details)

        if update_user_details_db(user_id, age, weight, medical_conditions if medical_conditions else "None"):
            flash("Profile updated successfully!", "success")
            return redirect(url_for('diagnose_form')) # Or a dedicated profile view page
        else:
            flash("Failed to update profile. Please try again.", "danger")
    return render_template('edit_profile.html', user=user_details)


# --- Placeholder for Diagnosis routes (to be implemented next) ---
@app.route('/diagnose', methods=['GET', 'POST'])
@login_required
def diagnose_form():
    # GET: Display the form with symptoms and risk factors
    # POST: Handle initial submission, get initial diagnosis & follow-up questions
    # This will be complex, we'll build it step-by-step
    user_details = get_user_details_db(session['user_id'])
    if user_details and (user_details['age'] is None or user_details['weight'] is None):
        flash("Please complete your profile before starting a diagnosis.", "warning")
        return redirect(url_for('complete_profile'))

    if request.method == 'POST':
        selected_symptoms = request.form.getlist('symptoms') # Name of checkbox group
        selected_risk_factors = request.form.getlist('risk_factors')

        if not selected_symptoms:
            flash("Please select at least one symptom.", "warning")
            return render_template('diagnose.html',
                                   symptom_categories=symptom_categories,
                                   unique_risk_factors=unique_risk_factors,
                                   user_name=session.get('user_name', 'User'))

        # Store selected symptoms and risks in session to carry over to follow-up
        session['current_symptoms'] = selected_symptoms
        session['current_risk_factors'] = selected_risk_factors

        # Format for Prolog
        symptoms_prolog_list_str = "[" + ",".join([f"'{s.replace('_', ' ')}'" for s in selected_symptoms]) + "]"
        risk_factors_prolog_list_str = "[" + ",".join([f"'{rf}'" if ' ' in rf else rf for rf in selected_risk_factors]) + "]"
        initial_answers_prolog_list_str = "[]" # No answers for the first pass

        initial_query_str = (f"findall([D, C], symptom_match({symptoms_prolog_list_str}, "
                             f"{risk_factors_prolog_list_str}, {initial_answers_prolog_list_str}, D, C), Results).")

        query_results = query_prolog(initial_query_str)
        initial_top_results_data = []
        follow_up_questions_to_ask = set() # Use set to store unique questions

        if query_results and query_results[0]['Results']:
            initial_sorted = sorted(query_results[0]['Results'], key=lambda x: float(x[1]), reverse=True)
            initial_top_results_data = initial_sorted[:3] # Consider top 3 for follow-ups

            for disease_atom, _confidence in initial_top_results_data:
                q_query_str = f"findall(Q, follow_up_question('{disease_atom}', Q), Questions)."
                q_results = query_prolog(q_query_str)
                if q_results and q_results[0]['Questions']:
                    for q_text_bytes in q_results[0]['Questions']:
                        # Pyswip can return byte strings, decode them
                        follow_up_questions_to_ask.add(q_text_bytes.decode('utf-8') if isinstance(q_text_bytes, bytes) else str(q_text_bytes))
        else:
            flash("Could not determine any likely diagnosis based on initial symptoms. Please consult a healthcare professional or try different symptoms.", "warning")
            return redirect(url_for('diagnose_form'))

        if follow_up_questions_to_ask:
            session['follow_up_questions'] = sorted(list(follow_up_questions_to_ask))
            return redirect(url_for('ask_followup'))
        else:
            # No follow-up questions, proceed to show results directly
            # This means we need to prepare final_top_match_details_data here
            session.pop('follow_up_questions', None) # Clear any old ones
            # For now, let's redirect to a results page that can handle this scenario
            # We'll pass the initial_top_results_data
            session['final_results_data'] = initial_top_results_data
            session['final_top_match_details'] = None # Will build this in results route if needed

            if initial_top_results_data:
                 # Get details for the top match
                top_disease_atom_bytes, top_confidence_float = initial_top_results_data[0]
                top_disease_atom = top_disease_atom_bytes.decode('utf-8') if isinstance(top_disease_atom_bytes, bytes) else str(top_disease_atom_bytes)

                test_res = query_prolog(f"requires_test('{top_disease_atom}', Test).")
                test_raw_bytes = test_res[0]['Test'] if test_res and 'Test' in test_res[0] else b"N/S"
                test_raw = test_raw_bytes.decode('utf-8') if isinstance(test_raw_bytes, bytes) else str(test_raw_bytes)


                treat_res = query_prolog(f"treatment('{top_disease_atom}', T).")
                treatment_raw_list_bytes = treat_res[0]['T'] if treat_res and 'T' in treat_res[0] and isinstance(treat_res[0]['T'], list) else ([treat_res[0]['T']] if treat_res and 'T' in treat_res[0] else [b"N/S info"])
                treatment_raw = [item.decode('utf-8') if isinstance(item, bytes) else str(item) for item in treatment_raw_list_bytes]


                advice_res = query_prolog(f"advice('{top_disease_atom}', A).")
                advice_raw_bytes = advice_res[0]['A'] if advice_res and 'A' in advice_res[0] else b"General advice."
                advice_raw = advice_raw_bytes.decode('utf-8') if isinstance(advice_raw_bytes, bytes) else str(advice_raw_bytes)

                personalized_raw = personalized_advice(session['user_id'], top_disease_atom)

                session['final_top_match_details'] = {
                    'disease_display': top_disease_atom.replace('_',' ').title(),
                    'test': test_raw.replace('_',' ').title(),
                    'treatment_str': "- " + "\n- ".join([str(item).replace('_', ' ').title() for item in treatment_raw]),
                    'advice': advice_raw,
                    'personalized': personalized_raw,
                    'raw_symptoms': session.get('current_symptoms', []),
                    'raw_disease': top_disease_atom,
                    'raw_confidence': float(top_confidence_float),
                    'raw_test': test_raw,
                    'raw_treatment': treatment_raw,
                    'raw_advice': advice_raw,
                    'raw_personalized': personalized_raw
                }
            return redirect(url_for('view_results'))

    # GET request
    return render_template('diagnose.html',
                           symptom_categories=symptom_categories,
                           unique_risk_factors=unique_risk_factors,
                           user_name=session.get('user_name', 'User'))

@app.route('/diagnose/followup', methods=['GET', 'POST'])
@login_required
def ask_followup():
    follow_up_questions = session.get('follow_up_questions')
    if not follow_up_questions:
        flash("No follow-up questions to ask, or session expired.", "warning")
        return redirect(url_for('diagnose_form'))

    if request.method == 'POST':
        collected_answers_raw = []
        for question_text in follow_up_questions:
            answer = request.form.get(question_text) # Names of inputs should be the question_text
            if answer in ['yes', 'no']:
                collected_answers_raw.append((question_text, answer))
            # else: user chose not to answer or an invalid value was submitted

        # Format answers for Prolog
        # Ensure the question text sent back matches exactly what Prolog expects (stored in session)
        formatted_answers_prolog = ["('{}',{})".format(q.replace("'", "''"), a) for q, a in collected_answers_raw]
        answers_prolog_list_str = "[" + ",".join(formatted_answers_prolog) + "]"

        symptoms_prolog_list_str = "[" + ",".join([f"'{s.replace('_', ' ')}'" for s in session.get('current_symptoms', [])]) + "]"
        risk_factors_prolog_list_str = "[" + ",".join([f"'{rf}'" if ' ' in rf else rf for rf in session.get('current_risk_factors', [])]) + "]"

        refined_query_str = (f"findall([D, C], symptom_match({symptoms_prolog_list_str}, "
                             f"{risk_factors_prolog_list_str}, {answers_prolog_list_str}, D, C), Results).")

        query_results = query_prolog(refined_query_str)
        final_top_results_data = []
        final_top_match_details_data = None

        if query_results and query_results[0]['Results']:
            refined_sorted = sorted(query_results[0]['Results'], key=lambda x: float(x[1]), reverse=True)
            final_top_results_data = refined_sorted[:3]

            if final_top_results_data:
                top_disease_atom_bytes, top_confidence_float = final_top_results_data[0]
                top_disease_atom = top_disease_atom_bytes.decode('utf-8') if isinstance(top_disease_atom_bytes, bytes) else str(top_disease_atom_bytes)


                test_res = query_prolog(f"requires_test('{top_disease_atom}', Test).")
                test_raw_bytes = test_res[0]['Test'] if test_res and 'Test' in test_res[0] else b"N/S"
                test_raw = test_raw_bytes.decode('utf-8') if isinstance(test_raw_bytes, bytes) else str(test_raw_bytes)


                treat_res = query_prolog(f"treatment('{top_disease_atom}', T).")
                treatment_raw_list_bytes = treat_res[0]['T'] if treat_res and 'T' in treat_res[0] and isinstance(treat_res[0]['T'], list) else ([treat_res[0]['T']] if treat_res and 'T' in treat_res[0] else [b"N/S info"])
                treatment_raw = [item.decode('utf-8') if isinstance(item, bytes) else str(item) for item in treatment_raw_list_bytes]

                advice_res = query_prolog(f"advice('{top_disease_atom}', A).")
                advice_raw_bytes = advice_res[0]['A'] if advice_res and 'A' in advice_res[0] else b"General advice."
                advice_raw = advice_raw_bytes.decode('utf-8') if isinstance(advice_raw_bytes, bytes) else str(advice_raw_bytes)

                personalized_raw = personalized_advice(session['user_id'], top_disease_atom)

                final_top_match_details_data = {
                    'disease_display': top_disease_atom.replace('_',' ').title(),
                    'test': test_raw.replace('_',' ').title(),
                    'treatment_str': "- " + "\n- ".join([str(item).replace('_', ' ').title() for item in treatment_raw]),
                    'advice': advice_raw,
                    'personalized': personalized_raw,
                    'raw_symptoms': session.get('current_symptoms', []),
                    'raw_disease': top_disease_atom,
                    'raw_confidence': float(top_confidence_float),
                    'raw_test': test_raw,
                    'raw_treatment': treatment_raw,
                    'raw_advice': advice_raw,
                    'raw_personalized': personalized_raw
                }
        else:
            flash("Could not determine a refined diagnosis after follow-up. Please consult a healthcare professional.", "warning")
            # Optionally, you could show the initial results if no refined results are found
            # For now, redirecting to diagnose form
            return redirect(url_for('diagnose_form'))

        session['final_results_data'] = final_top_results_data
        session['final_top_match_details'] = final_top_match_details_data
        session['questions_asked_for_display'] = follow_up_questions # For display on results page
        # Clear session variables used during diagnosis process
        session.pop('follow_up_questions', None)
        # session.pop('current_symptoms', None) # Keep for report
        # session.pop('current_risk_factors', None) # Keep for report

        return redirect(url_for('view_results'))

    return render_template('followup_questions.html', questions=follow_up_questions)

@app.route('/diagnose/results')
@login_required
def view_results():
    top_results = session.get('final_results_data')
    top_match_details = session.get('final_top_match_details')
    follow_up_questions_asked = session.get('questions_asked_for_display')

    if top_results is None and top_match_details is None: # Check if any results exist
        flash("No diagnosis results found in session. Please start a new diagnosis.", "warning")
        return redirect(url_for('diagnose_form'))

    # Decode byte strings if they exist in top_results
    decoded_top_results = []
    if top_results:
        for item in top_results:
            disease_bytes, conf = item
            disease_str = disease_bytes.decode('utf-8') if isinstance(disease_bytes, bytes) else str(disease_bytes)
            decoded_top_results.append((disease_str, conf))


    # Clean up session data that is only for this view
    # session.pop('final_results_data', None)
    # session.pop('final_top_match_details', None) # Keep this for report generation
    session.pop('questions_asked_for_display', None)

    return render_template('results.html',
                           top_results=decoded_top_results,
                           top_match_details=top_match_details,
                           follow_up_questions_asked=follow_up_questions_asked,
                           user_id=session['user_id'])


@app.route('/report/generate', methods=['POST']) # Changed to POST to avoid accidental generation
@login_required
def generate_and_save_report():
    user_id = session['user_id']
    # Retrieve details from session, which should have been set by view_results
    top_match_details = session.get('final_top_match_details')

    if not top_match_details:
        flash("No diagnosis data available to generate a report.", "warning")
        return redirect(url_for('view_results')) # Or wherever appropriate

    user_details_row = get_user_details_db(user_id)
    if not user_details_row:
        flash("User details not found. Cannot generate report.", "danger")
        return redirect(url_for('view_results'))

    diagnosis_data_for_pdf = {
        'symptoms': top_match_details['raw_symptoms'],
        'disease': top_match_details['raw_disease'], # atom
        'confidence': top_match_details['raw_confidence'], # float
        'test': top_match_details['raw_test'], # atom or string
        'treatment': top_match_details['raw_treatment'], # list of atoms/strings
        'advice': top_match_details['raw_advice'], # string
        'personalized_advice': top_match_details['raw_personalized'] # string
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_disease_name = "".join(c if c.isalnum() else "_" for c in str(top_match_details['raw_disease']))
    base_pdf_filename = f"Report_{user_id}_{safe_disease_name}_{timestamp}.pdf"

    pdf_filepath = generate_pdf_report(base_pdf_filename, user_details_row, diagnosis_data_for_pdf)

    if pdf_filepath:
        symptoms_str = ','.join(top_match_details['raw_symptoms'])
        if add_diagnosis_db(user_id, symptoms_str, top_match_details['raw_disease'], top_match_details['raw_confidence'], pdf_filepath):
            flash(f"Diagnosis report saved: {os.path.basename(pdf_filepath)} and added to history.", "success")
            # Make the PDF downloadable immediately after generation
            session['last_report_path'] = pdf_filepath # Store for download link
        else:
            flash("Report PDF saved, but failed to update history. Please contact support.", "danger")
    else:
        flash("Failed to generate PDF report.", "danger")

    return redirect(url_for('view_results')) # Redirect back to results page

@app.route('/report/download/last')
@login_required
def download_last_report():
    report_path = session.get('last_report_path')
    if report_path and os.path.exists(report_path):
        try:
            # Clear it after use so it's not accidentally re-downloaded without new generation
            session.pop('last_report_path', None)
            return send_from_directory(directory=os.path.dirname(report_path),
                                       path=os.path.basename(report_path), # Use path instead of filename
                                       as_attachment=True)
        except Exception as e:
            flash(f"Error sending report: {e}", "danger")
            return redirect(url_for('view_results'))
    flash("No report available for download or file not found.", "warning")
    return redirect(url_for('view_results'))

@app.route('/report/download_history/<int:history_id>')
@login_required
def download_history_report(history_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT report_filename FROM history WHERE id = ? AND user_id = ?", (history_id, session['user_id']))
    record = cursor.fetchone()

    if record and record['report_filename'] and os.path.exists(record['report_filename']):
        try:
            return send_from_directory(directory=os.path.dirname(record['report_filename']),
                                       path=os.path.basename(record['report_filename']),
                                       as_attachment=True)
        except Exception as e:
            flash(f"Error sending report: {e}", "danger")
            return redirect(url_for('history'))
    else:
        flash("Report not found or access denied.", "warning")
        return redirect(url_for('history'))


@app.route('/history')
@login_required
def history_page():
    user_id = session['user_id']
    history_data_rows = get_user_history_db(user_id)
    # Convert Row objects to dictionaries for easier template access
    history_data = [dict(row) for row in history_data_rows]
    for item in history_data: # Make report filename just the basename for display
        if item.get('report_filename'):
            item['report_basename'] = os.path.basename(item['report_filename'])
    return render_template('history.html', history_data=history_data)

@app.route('/statistics')
@login_required
def statistics_page():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""SELECT diagnosis, COUNT(*) as count FROM history
                          WHERE diagnosis IS NOT NULL AND diagnosis != ''
                          GROUP BY diagnosis ORDER BY COUNT(*) DESC""")
        data = cursor.fetchall()
    except Exception as e:
        flash(f"Could not retrieve statistics: {e}", "danger")
        return render_template('statistics.html', chart_url=None, error=True)

    if not data:
        return render_template('statistics.html', chart_url=None, no_data=True)

    labels_bytes = [x['diagnosis'] for x in data]
    labels = [str(label).replace('_', ' ').title() for label in labels_bytes]
    counts = [x['count'] for x in data]

    fig, ax = plt.subplots(figsize=(7, 6)) # Adjusted size for better fit
    wedges, texts, autotexts = ax.pie(counts, labels=None, autopct='%1.1f%%', startangle=90,
                                      pctdistance=0.85, wedgeprops=dict(width=0.4))
    ax.set_title("Distribution of Diagnoses", fontsize=16, pad=20)
    # Legend outside the pie for clarity
    ax.legend(wedges, labels, title="Diagnoses", loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1), fontsize='small')
    plt.tight_layout(rect=[0, 0, 0.8, 1]) # Adjust layout to make space for legend

    # Save chart to a static file
    charts_dir = os.path.join(app.static_folder, 'charts')
    os.makedirs(charts_dir, exist_ok=True)
    chart_filename = f"diagnosis_stats_{session['user_id']}_{datetime.now().timestamp()}.png"
    chart_path = os.path.join(charts_dir, chart_filename)
    try:
        fig.savefig(chart_path)
        plt.close(fig) # Close the figure to free memory
    except Exception as e:
        flash(f"Error saving chart: {e}", "danger")
        return render_template('statistics.html', chart_url=None, error=True)

    chart_url = url_for('static', filename=f'charts/{chart_filename}')
    return render_template('statistics.html', chart_url=chart_url)


if __name__ == '__main__':
    if not os.path.exists(app.config['PROLOG_FILE']):
        print(f"CRITICAL ERROR: Prolog file '{app.config['PROLOG_FILE']}' not found.")
        print("The application cannot start without the Prolog knowledge base.")
    else:
        app.run(debug=True) # debug=True is for development