from flask import Flask, render_template, request, url_for, redirect, session
import pypdf
from authlib.integrations.flask_client import OAuth
from flask_mysqldb import MySQL
import stripe

import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


# --- 💳 STRIPE CONFIGURATION WITH YOUR EXACT REVEALED KEYS ---

# 1. Secret Key (Jo 'sk_test_' se shuru ho rahi hai)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# 2. Publishable Key (Jo 'pk_test_' se shuru ho rahi hai)
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.getenv("SECRET_KEY")

# --- 🗄️ MYSQL DATABASE CONFIGURATION ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' # phpMyAdmin ka password agar nahi rakha toh khali chodein
app.config['MYSQL_DB'] = 'talentflow_db'
mysql = MySQL(app)

# --- GOOGLE OAUTH CONFIGURATION ---
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url=os.getenv("GOOGLE_SERVER_METADATA_URL"),
    client_kwargs={'scope': 'openid email profile'},
)

@app.route("/")
def home():
    user_data = session.get('user')
    return render_template('index.html', user=user_data)
@app.route("/about")
def about():
    # Agar user logged in hai toh navbar mein uska naam dikhane ke liye session se user bhejenge
    user_data = session.get('user', None)
    is_pro = session.get('is_pro', False)
    return render_template("about.html", user=user_data, is_pro=is_pro)
@app.route("/login")
def login():
    redirect_uri = url_for('auth_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/auth/callback")
def auth_callback():
    token = google.authorize_access_token()
    resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
    user_info = resp.json()
    session['user'] = user_info
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# --- 🔄 UPDATED: DASHBOARD ROUTE TO FETCH HISTORY ---
@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))  
        
    user_email = session['user']['email']
    
    # Database se scans ki history nikalna taaki pehli dafa page khulne par table khali na dikhe
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT candidate_name, required_skills, matched_skills, match_score, scanned_at FROM cv_scans WHERE user_email = %s ORDER BY scanned_at DESC", (user_email,))
    history = cursor.fetchall()
    cursor.close()
    
    return render_template('dashboard.html', 
                           user=session['user'], 
                           score=None, 
                           matched_skills=None, 
                           resume_text=None,
                           history=history) # Database se aayi hui list HTML ko bhej di

# --- 🎯 UPDATED: UPLOAD ROUTE WITH SAVE LOGIC ---
@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('home'))
        
    user_email = session['user']['email']
    file = request.files.get('resume')
    skill_input = request.form.get('required_skills', '') 
    
    if file and file.filename.endswith('.pdf'):
        file_path = f"{app.config['UPLOAD_FOLDER']}/{file.filename}"
        file.save(file_path)
        
        reader = pypdf.PdfReader(file_path)
        extracted_text = ""

        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

        # --- SKILL MATCHING LOGIC ---
        resume_lower = extracted_text.lower()
        required_skills_list = [s.strip().lower() for s in skill_input.split(',') if s.strip()]
        matched_skills = []
        
        for skill in required_skills_list:
            if skill in resume_lower:
                matched_skills.append(skill)
                
        total_required = len(required_skills_list)
        match_score = 0
        if total_required > 0:
            match_score = round((len(matched_skills) / total_required) * 100)

        # --- 💾 NEW: DATA SAVE IN DATABASE ---
        # File name se '.pdf' hata kar khoobsurat candidate name banana (e.g. ali_resume -> Ali resume)
        candidate_name = file.filename.replace('.pdf', '').replace('_', ' ').capitalize()
        matched_skills_str = ", ".join(matched_skills)
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO cv_scans (user_email, candidate_name, required_skills, matched_skills, match_score)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_email, candidate_name, skill_input, matched_skills_str, match_score))
        mysql.connection.commit()
        cursor.close()

        # Database se dubara updated list fetch karna taaki naya scan bhi foran table mein dikhe
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT candidate_name, required_skills, matched_skills, match_score, scanned_at FROM cv_scans WHERE user_email = %s ORDER BY scanned_at DESC", (user_email,))
        history = cursor.fetchall()
        cursor.close()

        return render_template('dashboard.html', 
                               user=session['user'], 
                               resume_text=extracted_text, 
                               required_skills=skill_input,
                               matched_skills=matched_skills, # Frontend processing box ke liye direct list
                               score=match_score,             
                               msg='Resume successfully parsed, matched, and saved to Database!',
                               history=history) # HTML table ko updated list bhej di
                               
    return "Error: Sirf PDF file upload karne ki ijazat hai!"


@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        # Yeh line Stripe ke servers par ek real test session banayegi
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'TalentFlow AI Pro Plan',
                            'description': 'Unlimited Resume Scans & Advanced Skill Matching',
                        },
                        'unit_amount': 900, # $9.00 ko cents mein likhte hain (900)
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            # Success hone par user is route par wapas aayega
            success_url=request.host_url + 'payment-success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'dashboard',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return str(e), 500
    


@app.route("/payment-success")
def payment_success():
    if 'user' not in session:
        return redirect(url_for('home'))
        
    session_id = request.args.get('session_id')
    if session_id:
        # Stripe se verify kiya ke payment waqai hui hai
        session_info = stripe.checkout.Session.retrieve(session_id)
        if session_info.payment_status == 'paid':
            # User ko session mein Pro bana diya
            session['is_pro'] = True
            
    # Dashboard ka data dubara fetch karenge taaki screen khali na dikhe
    user_email = session['user']['email']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT candidate_name, required_skills, matched_skills, match_score, scanned_at FROM cv_scans WHERE user_email = %s ORDER BY scanned_at DESC", (user_email,))
    history = cursor.fetchall()
    cursor.close()
    
    return render_template("dashboard.html", 
                           user=session['user'], 
                           score=None, 
                           matched_skills=None, 
                           resume_text=None,
                           history=history, 
                           is_pro=True,
                           msg="🎉 Premium Activated Successfully via Asli Stripe Sandbox!")


if __name__ == '__main__':
    app.run(debug=True)