import streamlit as st
import numpy as np
import pickle
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="StrokeGuard AI",
    page_icon="🧠",
    layout="centered"
)

# ─────────────────────────────────────────────
#  SHARED GLOBAL CSS  (gradient bg + glass card)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&display=swap');

/* ── Base ── */
* { font-family: 'Nunito', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: white;
}

/* ── Glass card helper ── */
.glass-card {
    background: rgba(255,255,255,0.13);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 24px;
    padding: 36px 40px;
    border: 1px solid rgba(255,255,255,0.25);
    box-shadow: 0 8px 32px rgba(31,38,135,0.30);
    margin-bottom: 20px;
}

/* ── Headings ── */
h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }

/* ── Input labels ── */
label, .stRadio label, .stSelectbox label,
.stSlider label, .stNumberInput label,
.stTextInput label, .stPasswordInput label {
    color: rgba(255,255,255,0.90) !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
}

/* ── Text inputs & password ── */
.stTextInput input, .stPasswordInput input {
    background: rgba(255,255,255,0.18) !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: 14px !important;
    color: #ffffff !important;
    padding: 12px 16px !important;
    font-size: 1rem !important;
}
.stTextInput input::placeholder,
.stPasswordInput input::placeholder {
    color: rgba(255,255,255,0.55) !important;
}
.stTextInput input:focus,
.stPasswordInput input:focus {
    border-color: #00d2ff !important;
    box-shadow: 0 0 0 2px rgba(0,210,255,0.25) !important;
    outline: none !important;
}

/* ── Number input ── */
.stNumberInput input {
    background: rgba(255,255,255,0.18) !important;
    border: 1px solid rgba(255,255,255,0.30) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
}

/* ── Selectbox ── */
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.18) !important;
    border: 1px solid rgba(255,255,255,0.30) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
}
.stSelectbox svg { fill: white !important; }

/* ── Slider ── */
.stSlider .stSlider-track { background: rgba(255,255,255,0.25) !important; }

/* ── Radio ── */
.stRadio div[role="radiogroup"] label span { color: white !important; }

/* ── Primary button ── */
.stButton > button {
    width: 100%;
    border-radius: 50px;
    height: 3.2em;
    background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
    color: white;
    border: none;
    font-weight: 700;
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.25);
    transition: all 0.2s ease;
    cursor: pointer;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 22px rgba(0,210,255,0.55);
}
.stButton > button:active {
    transform: scale(0.96);
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}

/* ── Secondary / outline button ── */
.secondary-btn > button {
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    color: white !important;
}
.secondary-btn > button:hover {
    background: rgba(255,255,255,0.25) !important;
    box-shadow: none !important;
}

/* ── Alert / info boxes ── */
.stAlert { border-radius: 14px !important; }
.stAlert p { color: #ffffff !important; font-weight: 600 !important; }

/* ── Metric ── */
div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 16px;
    padding: 14px;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #00d2ff, #3a7bd5) !important;
    border-radius: 8px !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.20) !important; }

/* ── Footer ── */
.footer-text {
    color: rgba(255,255,255,0.55);
    font-size: 0.78rem;
    text-align: center;
    margin-top: 32px;
}

/* ── Fade-in animation ── */
@keyframes fadeUp {
    from { opacity:0; transform:translateY(16px); }
    to   { opacity:1; transform:translateY(0); }
}
.fade-in { animation: fadeUp 0.7s ease-out both; }

/* ── Analytics stat box ── */
.stat-box {
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 18px;
    padding: 20px 18px;
    text-align: center;
    margin-bottom: 12px;
}
.stat-box .stat-value {
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
}
.stat-box .stat-label {
    font-size: 0.80rem;
    color: rgba(255,255,255,0.65);
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* ── Risk badge ── */
.risk-badge {
    display: inline-block;
    padding: 6px 20px;
    border-radius: 50px;
    font-weight: 800;
    font-size: 1rem;
    letter-spacing: 0.5px;
    margin: 8px 0;
}
.risk-high { background: rgba(255,80,80,0.30); border:1px solid rgba(255,80,80,0.6); color:#ffaaaa; }
.risk-low  { background: rgba(0,220,130,0.25); border:1px solid rgba(0,220,130,0.5); color:#aaffdd; }

/* ── Factor row ── */
.factor-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.10);
    font-size: 0.93rem;
}
.factor-row:last-child { border-bottom: none; }
.factor-label { color: rgba(255,255,255,0.75); }
.factor-value { font-weight: 700; color: white; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SESSION STATE DEFAULTS
# ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "result" not in st.session_state:
    st.session_state.result = None   # dict with all result data


# ─────────────────────────────────────────────
#  MODEL LOADER
# ─────────────────────────────────────────────
@st.cache_resource
def load_model():
    with open('stroke_model.pkl', 'rb') as file:
        model = pickle.load(file)
    return model

model = load_model()


# ═════════════════════════════════════════════
#  PAGE 1 — LOGIN
# ═════════════════════════════════════════════
def page_login():
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)

    # Centered logo / title
    st.markdown("""
    <div style='text-align:center; padding: 28px 0 10px;'>
        <div style='font-size:3.6rem;'>🧠</div>
        <h1 style='font-size:2.4rem; font-weight:800; margin:6px 0 2px;'>StrokeGuard AI</h1>
        <p style='color:rgba(255,255,255,0.70); font-size:1rem; margin:0;'>
            Personalized Stroke Risk Assessment Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 👤 &nbsp; Welcome Back")
    st.markdown("<p style='color:rgba(255,255,255,0.65); font-size:0.9rem; margin-top:-8px;'>Sign in to access your health dashboard</p>", unsafe_allow_html=True)

    name = st.text_input("Full Name", placeholder="e.g. Arjun Patel")
    email = st.text_input("Email Address", placeholder="you@example.com")
    password = st.text_input("Password", type="password", placeholder="••••••••")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Sign In  →"):
        if not name.strip():
            st.error("Please enter your full name.")
        elif not email.strip() or "@" not in email:
            st.error("Please enter a valid email address.")
        elif len(password) < 4:
            st.error("Password must be at least 4 characters.")
        else:
            with st.spinner("Authenticating…"):
                time.sleep(0.8)
            st.session_state.user_name = name.strip().split()[0]
            st.session_state.page = "main"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; margin-top:10px;'>
        <span style='color:rgba(255,255,255,0.55); font-size:0.82rem;'>
            🔒 &nbsp;Your data is encrypted and never stored externally.
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='footer-text'>Powered by XGBoost &amp; Streamlit &nbsp;|&nbsp; StrokeGuard v2.0</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════
#  PAGE 2 — MAIN ASSESSMENT (your original UI)
# ═════════════════════════════════════════════
def page_main():
    # ── top bar with greeting + logout ──
    col_greet, col_logout = st.columns([5, 1])
    with col_greet:
        st.markdown(f"<p style='color:rgba(255,255,255,0.75); margin-bottom:0;'>👋 Hello, <strong>{st.session_state.user_name}</strong></p>", unsafe_allow_html=True)
    with col_logout:
        if st.button("Logout"):
            st.session_state.page = "login"
            st.session_state.result = None
            st.rerun()

    st.title("🧠 StrokeGuard AI")
    st.markdown("##### Personalized Health Risk Assessment")
    st.write("Using advanced machine learning to analyze clinical parameters.")

    # --- Input Area inside a "Card" ---
    with st.container():
        st.info("Please fill in the medical information below:")

        col1, col2 = st.columns(2)

        with col1:
            gender_input = st.radio("Gender", options=["Female", "Male"], horizontal=True)
            gender = 1 if gender_input == "Male" else 0

            age = st.slider("Age", 0, 100, 45)

            hyper_input = st.selectbox("Hypertension Status", options=["No History", "Diagnosed"])
            hypertension = 1 if hyper_input == "Diagnosed" else 0

            heart_input = st.selectbox("Heart Disease History", options=["None", "Heart Condition Detected"])
            heart_disease = 1 if heart_input == "Heart Condition Detected" else 0

        with col2:
            avg_glucose_level = st.number_input("Average Glucose (mg/dL)", 50.0, 300.0, 105.0)

            bmi = st.number_input("BMI Index", 10.0, 60.0, 24.5)

            smoking_input = st.selectbox("Smoking Habits", options=[
                "Unknown", "Formerly Smoked", "Never Smoked", "Regular Smoker"
            ])
            smoking_dict = {"Unknown": 0, "Formerly Smoked": 1, "Never Smoked": 2, "Regular Smoker": 3}
            smoking_status = smoking_dict[smoking_input]

    st.markdown("---")

    # --- Prediction Logic ---
    if st.button("Analyze Stroke Probability"):
        with st.spinner('Analyzing health data...'):
            time.sleep(1)

            input_features = np.array([[gender, age, hypertension, heart_disease, avg_glucose_level, bmi, smoking_status]])
            probabilities = model.predict_proba(input_features)
            risk_percent = float(probabilities[0][1] * 100)

            # Save result to session state for the summary page
            st.session_state.result = {
                "risk_percent": risk_percent,
                "gender": gender_input,
                "age": age,
                "hypertension": hyper_input,
                "heart_disease": heart_input,
                "glucose": avg_glucose_level,
                "bmi": bmi,
                "smoking": smoking_input,
            }

        st.subheader("Analysis Results")

        if risk_percent > 50:
            st.warning(f"Analysis indicates a high concern level.")
        else:
            st.success(f"Analysis indicates a low concern level.")

        st.metric(label="Calculated Stroke Risk", value=f"{risk_percent:.1f}%")
        st.progress(risk_percent / 100)

        if risk_percent > 30:
            st.error("⚠️ **Recommendation:** Your profile shows clinical indicators often associated with higher risk. We strongly recommend scheduling a check-up with a doctor.")
        else:
            st.info("ℹ️ **Note:** Continue maintaining a balanced diet and regular exercise to keep your risk levels low.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊  View Full Summary & Analytics"):
            st.session_state.page = "summary"
            st.rerun()

    st.markdown("<br><hr><center><small>Powered by XGBoost & Streamlit | Project Version 2.0</small></center>", unsafe_allow_html=True)


# ═════════════════════════════════════════════
#  PAGE 3 — SUMMARY / ANALYTICS
# ═════════════════════════════════════════════
def page_summary():
    r = st.session_state.result

    if r is None:
        st.warning("No analysis data found. Please run the assessment first.")
        if st.button("← Go to Assessment"):
            st.session_state.page = "main"
            st.rerun()
        return

    risk = r["risk_percent"]
    is_high = risk > 50

    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)

    # ── Back button ──
    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← Back"):
            st.session_state.page = "main"
            st.rerun()

    # ── Title ──
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px;'>
        <div style='font-size:2.6rem;'>📊</div>
        <h1 style='font-size:2rem; font-weight:800; margin:4px 0;'>Your Health Summary</h1>
        <p style='color:rgba(255,255,255,0.65); font-size:0.95rem;'>
            Detailed breakdown of your stroke risk analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Risk Score Card ──
    badge_class = "risk-high" if is_high else "risk-low"
    badge_text  = "⚠️  High Risk" if is_high else "✅  Low Risk"
    ring_color  = "#ff6b6b" if is_high else "#00dc82"

    st.markdown(f"""
    <div class='glass-card' style='text-align:center;'>
        <p style='color:rgba(255,255,255,0.60); font-size:0.85rem; text-transform:uppercase;
                  letter-spacing:1px; margin-bottom:6px;'>Overall Stroke Risk Score</p>
        <div style='font-size:4.5rem; font-weight:800; color:{ring_color};
                    text-shadow: 0 0 24px {ring_color}44;'>
            {risk:.1f}<span style='font-size:2rem;'>%</span>
        </div>
        <div class='risk-badge {badge_class}'>{badge_text}</div>
        <div style='margin-top:16px; background:rgba(255,255,255,0.12); border-radius:12px;
                    overflow:hidden; height:10px;'>
            <div style='height:100%; width:{min(risk,100):.1f}%;
                        background:linear-gradient(90deg,{ring_color},{ring_color}99);
                        border-radius:12px; transition:width 1s ease;'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 3 stat boxes ──
    col1, col2, col3 = st.columns(3)
    risk_factors = sum([
        r["hypertension"] == "Diagnosed",
        r["heart_disease"] == "Heart Condition Detected",
        r["smoking"] == "Regular Smoker",
        r["glucose"] > 140,
        r["bmi"] > 30,
    ])
    bmi_label = "Underweight" if r["bmi"] < 18.5 else ("Normal" if r["bmi"] < 25 else ("Overweight" if r["bmi"] < 30 else "Obese"))
    glucose_label = "Normal" if r["glucose"] < 100 else ("Borderline" if r["glucose"] < 140 else "High")

    with col1:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-value'>{r['age']}</div>
            <div class='stat-label'>Age (Years)</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-value'>{risk_factors}</div>
            <div class='stat-label'>Risk Factors</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-value'>{r['bmi']:.1f}</div>
            <div class='stat-label'>BMI ({bmi_label})</div>
        </div>""", unsafe_allow_html=True)

    # ── Clinical Details Card ──
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🩺 &nbsp; Clinical Profile")

    details = [
        ("Gender",         r["gender"],      "👤"),
        ("Age",            f"{r['age']} yrs", "🎂"),
        ("Hypertension",   r["hypertension"], "💊"),
        ("Heart Disease",  r["heart_disease"],"❤️"),
        ("Avg. Glucose",   f"{r['glucose']:.1f} mg/dL &nbsp;<span style='color:{'#ffaaaa' if r['glucose']>140 else '#aaffdd'};font-size:0.75rem;'>({glucose_label})</span>", "🩸"),
        ("BMI",            f"{r['bmi']:.1f} &nbsp;<span style='color:rgba(255,255,255,0.60);font-size:0.75rem;'>({bmi_label})</span>", "⚖️"),
        ("Smoking",        r["smoking"],      "🚬"),
    ]

    for label, value, icon in details:
        st.markdown(f"""
        <div class='factor-row'>
            <span class='factor-label'>{icon} &nbsp; {label}</span>
            <span class='factor-value'>{value}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Recommendations Card ──
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 💡 &nbsp; Personalised Recommendations")

    tips = []
    if is_high:
        tips.append(("🏥", "Schedule a full neurological check-up with your doctor as soon as possible."))
    if r["hypertension"] == "Diagnosed":
        tips.append(("💊", "Take prescribed antihypertensive medications consistently and monitor BP daily."))
    if r["glucose"] > 140:
        tips.append(("🩸", "Your glucose is elevated — reduce refined sugars and consult a diabetologist."))
    if r["bmi"] > 30:
        tips.append(("🏃", "A BMI above 30 raises risk significantly — aim for 30 min of exercise 5× per week."))
    if r["smoking"] == "Regular Smoker":
        tips.append(("🚭", "Quitting smoking is the single highest-impact action you can take to reduce stroke risk."))
    if not tips:
        tips.append(("🌿", "Great profile! Keep maintaining a balanced diet, regular exercise, and annual check-ups."))
        tips.append(("😴", "Ensure 7–8 hours of quality sleep nightly to support cardiovascular health."))

    for icon, tip in tips:
        st.markdown(f"""
        <div style='display:flex; gap:14px; align-items:flex-start; padding:10px 0;
                    border-bottom:1px solid rgba(255,255,255,0.10);'>
            <span style='font-size:1.4rem;'>{icon}</span>
            <span style='color:rgba(255,255,255,0.85); font-size:0.92rem; line-height:1.5;'>{tip}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Disclaimer ──
    st.markdown("""
    <div style='background:rgba(255,255,255,0.08); border-left:3px solid rgba(255,255,255,0.35);
                border-radius:10px; padding:14px 18px; margin-top:4px;'>
        <span style='font-size:0.82rem; color:rgba(255,255,255,0.60);'>
            ⚠️ <strong style='color:rgba(255,255,255,0.80);'>Medical Disclaimer:</strong>
            This tool is for informational purposes only and does not constitute medical advice.
            Always consult a qualified healthcare professional for diagnosis and treatment.
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='footer-text' style='margin-top:24px;'>Powered by XGBoost &amp; Streamlit &nbsp;|&nbsp; StrokeGuard v2.0</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════
#  ROUTER
# ═════════════════════════════════════════════
if st.session_state.page == "login":
    page_login()
elif st.session_state.page == "main":
    page_main()
elif st.session_state.page == "summary":
    page_summary()
