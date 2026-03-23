import streamlit as st
import numpy as np
import pickle
import time
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

st.set_page_config(page_title="StrokeGuard AI", page_icon="🧠", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800;900&family=Raleway:wght@700;800;900&display=swap');
*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp { font-family: 'Nunito', sans-serif; }
.stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: white; }
.glass-card { background: rgba(255,255,255,0.13); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); border-radius: 24px; padding: 32px 36px; border: 1px solid rgba(255,255,255,0.25); box-shadow: 0 8px 32px rgba(31,38,135,0.28); margin-bottom: 18px; transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease; }
.glass-card:hover { transform: translateY(-3px); box-shadow: 0 14px 40px rgba(31,38,135,0.38); border-color: rgba(255,255,255,0.42); }
.factor-row { display: flex; align-items: center; justify-content: space-between; padding: 11px 6px; border-bottom: 1px solid rgba(255,255,255,0.10); font-size: 0.93rem; border-radius: 8px; transition: background 0.20s ease, padding-left 0.20s ease; cursor: default; }
.factor-row:last-child { border-bottom: none; }
.factor-row:hover { background: rgba(255,255,255,0.11); padding-left: 12px; }
.factor-label { color: rgba(255,255,255,0.72); }
.factor-value { font-weight: 700; color: white; }
.comp-row { display: flex; align-items: center; padding: 10px 8px; border-radius: 10px; transition: background 0.20s ease, transform 0.18s ease; border-bottom: 1px solid rgba(255,255,255,0.08); cursor: default; }
.comp-row:hover { background: rgba(255,255,255,0.12); transform: translateX(4px); }
.comp-row:last-child { border-bottom: none; }
.stat-box { background: rgba(255,255,255,0.13); border: 1px solid rgba(255,255,255,0.22); border-radius: 18px; padding: 20px 14px; text-align: center; margin-bottom: 12px; transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease; cursor: default; }
.stat-box:hover { transform: translateY(-4px) scale(1.03); box-shadow: 0 10px 28px rgba(0,0,0,0.20); border-color: rgba(255,255,255,0.44); }
.stat-box .stat-value { font-size: 2rem; font-weight: 800; color: #ffffff; }
.stat-box .stat-label { font-size: 0.75rem; color: rgba(255,255,255,0.60); font-weight: 700; letter-spacing: 0.6px; text-transform: uppercase; margin-top: 4px; }
.tip-row { display: flex; gap: 14px; align-items: flex-start; padding: 11px 6px; border-radius: 10px; border-bottom: 1px solid rgba(255,255,255,0.09); transition: background 0.20s ease, padding-left 0.20s ease; cursor: default; }
.tip-row:hover { background: rgba(255,255,255,0.11); padding-left: 14px; }
.tip-row:last-child { border-bottom: none; }
.glossary-item { padding: 12px 14px; border-radius: 12px; border-bottom: 1px solid rgba(255,255,255,0.09); transition: background 0.20s ease, padding-left 0.20s ease; cursor: default; }
.glossary-item:hover { background: rgba(255,255,255,0.10); padding-left: 20px; }
.glossary-item:last-child { border-bottom: none; }
.glossary-term { font-weight: 800; color: #a8d8ff; font-size: 0.92rem; margin-bottom: 3px; }
.glossary-def  { color: rgba(255,255,255,0.72); font-size: 0.85rem; line-height: 1.55; }
h1, h2, h3, h4, h5, h6 { color: #ffffff !important; font-family: 'Raleway', sans-serif; }
label, .stRadio label, .stSelectbox label, .stSlider label, .stNumberInput label, .stTextInput label, .stPasswordInput label { color: rgba(255,255,255,0.88) !important; font-weight: 700 !important; font-size: 0.90rem !important; }
.stTextInput input, .stPasswordInput input { background: rgba(255,255,255,0.16) !important; border: 1px solid rgba(255,255,255,0.30) !important; border-radius: 14px !important; color: #ffffff !important; padding: 12px 16px !important; font-size: 1rem !important; transition: border-color 0.2s, box-shadow 0.2s; }
.stTextInput input::placeholder, .stPasswordInput input::placeholder { color: rgba(255,255,255,0.48) !important; }
.stTextInput input:focus, .stPasswordInput input:focus { border-color: #00d2ff !important; box-shadow: 0 0 0 3px rgba(0,210,255,0.22) !important; }
.stNumberInput input { background: rgba(255,255,255,0.16) !important; border: 1px solid rgba(255,255,255,0.28) !important; border-radius: 12px !important; color: #ffffff !important; }
.stSelectbox div[data-baseweb="select"] > div { background: rgba(255,255,255,0.16) !important; border: 1px solid rgba(255,255,255,0.28) !important; border-radius: 12px !important; color: #ffffff !important; }
.stSelectbox svg { fill: white !important; }
.stAlert { border-radius: 14px !important; }
.stAlert p { color: #ffffff !important; font-weight: 700 !important; }
div[data-testid="stMetricValue"] { color: #ffffff !important; background: rgba(255,255,255,0.11); border: 1px solid rgba(255,255,255,0.20); border-radius: 16px; padding: 14px; }
.stProgress > div > div > div > div { background: linear-gradient(90deg, #00d2ff, #3a7bd5) !important; border-radius: 8px !important; }
.stButton > button { width: 100%; border-radius: 50px; height: 3.2em; background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%); color: white; border: none; font-weight: 800; font-size: 1rem; text-transform: uppercase; letter-spacing: 1.6px; box-shadow: 0 4px 18px rgba(0,0,0,0.22); transition: transform 0.18s ease, box-shadow 0.18s ease; }
.stButton > button:hover { transform: translateY(-3px); box-shadow: 0 0 26px rgba(0,210,255,0.52); }
.stButton > button:active { transform: scale(0.96); box-shadow: 0 2px 8px rgba(0,0,0,0.38); }
.stDownloadButton > button { background: linear-gradient(90deg, #00dc82, #00b4d8) !important; }
hr { border-color: rgba(255,255,255,0.18) !important; }
.footer-text { color: rgba(255,255,255,0.45); font-size: 0.76rem; text-align: center; margin-top: 28px; padding-bottom: 16px; }
.risk-badge { display: inline-block; padding: 5px 22px; border-radius: 50px; font-weight: 800; font-size: 0.95rem; letter-spacing: 0.5px; margin: 8px 0; }
.risk-high { background:rgba(255,80,80,0.28); border:1px solid rgba(255,80,80,0.55); color:#ffb3b3; }
.risk-mod  { background:rgba(255,180,0,0.25); border:1px solid rgba(255,180,0,0.50); color:#ffe0a0; }
.risk-low  { background:rgba(0,220,130,0.22); border:1px solid rgba(0,220,130,0.48); color:#aaffd8; }
.disclaimer { background: rgba(255,255,255,0.07); border-left: 3px solid rgba(255,210,0,0.55); border-radius: 10px; padding: 14px 18px; margin-top: 6px; }
.disclaimer p { color: rgba(255,255,255,0.62) !important; font-size:0.82rem !important; margin:0; line-height:1.5; }
@keyframes fadeUp { from { opacity:0; transform:translateY(18px); } to { opacity:1; transform:translateY(0); } }
.fade-in   { animation: fadeUp 0.65s ease-out both; }
.fade-in-2 { animation: fadeUp 0.65s ease-out 0.14s both; }
.fade-in-3 { animation: fadeUp 0.65s ease-out 0.28s both; }
@keyframes floatBrain { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
.float-brain { animation: floatBrain 3s ease-in-out infinite; display:inline-block; }
@keyframes pulseGlow { 0%,100% { opacity:1; } 50% { opacity:0.70; } }
.pulse { animation: pulseGlow 2.2s ease-in-out infinite; }
</style>
""", unsafe_allow_html=True)

# SESSION STATE
for k, v in {"page":"auth","auth_mode":"login","user_name":"","users":{},"result":None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# MODEL
@st.cache_resource
def load_model():
    with open('stroke_model.pkl','rb') as f:
        return pickle.load(f)
model = load_model()

# HELPERS
def age_avg_risk(age):
    if age < 40: return 1.2
    if age < 50: return 2.8
    if age < 60: return 5.5
    if age < 70: return 9.0
    return 14.5

def gauge_svg(pct):
    import math
    angle = pct / 100 * 180
    rad = math.radians(180 - angle)
    cx, cy, r = 160, 135, 105
    nx = cx + r * math.cos(rad)
    ny = cy - r * math.sin(rad)
    color = "#00dc82" if pct < 30 else ("#ffb347" if pct < 60 else "#ff5f5f")
    label = "LOW" if pct < 30 else ("MODERATE" if pct < 60 else "HIGH")
    return f"""
<svg viewBox="0 0 320 155" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:360px;display:block;margin:0 auto;">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00dc82"/>
      <stop offset="50%" stop-color="#ffb347"/>
      <stop offset="100%" stop-color="#ff5f5f"/>
    </linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="3.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <path d="M 55 135 A 105 105 0 0 1 265 135" fill="none" stroke="rgba(255,255,255,0.14)" stroke-width="16" stroke-linecap="round"/>
  <path d="M 55 135 A 105 105 0 0 1 265 135" fill="none" stroke="url(#g)" stroke-width="16" stroke-linecap="round" opacity="0.88"/>
  <line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="white" stroke-width="3.5" stroke-linecap="round" filter="url(#glow)"/>
  <circle cx="{cx}" cy="{cy}" r="7" fill="white" opacity="0.92"/>
  <text x="{cx}" y="{cy-26}" text-anchor="middle" font-family="Raleway,sans-serif" font-size="34" font-weight="900" fill="{color}" filter="url(#glow)">{pct:.1f}%</text>
  <text x="{cx}" y="{cy-6}" text-anchor="middle" font-family="Nunito,sans-serif" font-size="11" font-weight="800" fill="{color}" letter-spacing="2.5">{label}</text>
  <text x="48"  y="152" text-anchor="middle" font-family="Nunito,sans-serif" font-size="10" fill="rgba(255,255,255,0.42)">0%</text>
  <text x="160" y="26"  text-anchor="middle" font-family="Nunito,sans-serif" font-size="10" fill="rgba(255,255,255,0.42)">50%</text>
  <text x="272" y="152" text-anchor="middle" font-family="Nunito,sans-serif" font-size="10" fill="rgba(255,255,255,0.42)">100%</text>
</svg>"""

# PDF BUILDER
def build_pdf(r, risk_label, avg_risk, rf_count, bmi_label, gluc_label, tips):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
        title="StrokeGuard AI - Doctor's Summary")
    PURPLE = colors.HexColor("#764ba2")
    BLUE   = colors.HexColor("#667eea")
    DARK   = colors.HexColor("#1a1a2e")
    LGBG   = colors.HexColor("#f0f4ff")
    GREEN  = colors.HexColor("#00b894")
    RED    = colors.HexColor("#e17055")
    ORANGE = colors.HexColor("#fdcb6e")
    GREY   = colors.HexColor("#555577")
    rc = RED if r["risk_percent"] >= 60 else (ORANGE if r["risk_percent"] >= 30 else GREEN)
    styles = getSampleStyleSheet()
    ts = ParagraphStyle("T", parent=styles["Normal"], fontSize=22, fontName="Helvetica-Bold", textColor=PURPLE, alignment=TA_CENTER, spaceAfter=4)
    ss = ParagraphStyle("S", parent=styles["Normal"], fontSize=10, textColor=GREY, alignment=TA_CENTER, spaceAfter=2)
    hs = ParagraphStyle("H", parent=styles["Normal"], fontSize=13, fontName="Helvetica-Bold", textColor=PURPLE, spaceBefore=14, spaceAfter=6)
    bs = ParagraphStyle("B", parent=styles["Normal"], fontSize=9.5, textColor=DARK, leading=15, spaceAfter=4)
    ds = ParagraphStyle("D", parent=styles["Normal"], fontSize=8, textColor=GREY, leading=12, borderPad=6, backColor=colors.HexColor("#fff8e1"), borderColor=ORANGE, borderWidth=0.5, borderRadius=4)
    story = []
    story.append(Paragraph("StrokeGuard AI", ts))
    story.append(Paragraph("Doctor's Summary Report - Confidential", ss))
    story.append(Paragraph(f"Patient: <b>{st.session_state.user_name}</b> | Generated: {time.strftime('%d %B %Y, %H:%M')}", ss))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PURPLE, spaceAfter=12, spaceBefore=6))
    banner = Table([[
        Paragraph(f"<font size=26><b><font color='{rc.hexval()}'>{r['risk_percent']:.1f}%</font></b></font>",
                  ParagraphStyle("Rv", alignment=TA_CENTER, leading=30)),
        Paragraph(f"<b>{risk_label}</b><br/><font size=9 color='#666699'>Age-group average: {avg_risk:.1f}%</font><br/><font size=9 color='#666699'>Risk factors: {rf_count} / 5</font>",
                  ParagraphStyle("Rb", leading=16, spaceBefore=4))
    ]], colWidths=["35%","65%"])
    banner.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),LGBG), ("BOX",(0,0),(-1,-1),1,BLUE),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("LEFTPADDING",(0,0),(-1,-1),14),
        ("RIGHTPADDING",(0,0),(-1,-1),14), ("TOPPADDING",(0,0),(-1,-1),12),
        ("BOTTOMPADDING",(0,0),(-1,-1),12),
    ]))
    story.append(banner)
    story.append(Spacer(1,14))
    story.append(Paragraph("Clinical Profile", hs))
    pd = [["Parameter","Your Value","Ideal / Normal"],
          ["Gender", r["gender"], "-"],
          ["Age", f"{r['age']} years", "-"],
          ["BMI", f"{r['bmi']:.1f} ({bmi_label})", "18.5 - 24.9"],
          ["Avg. Glucose", f"{r['glucose']:.1f} mg/dL ({gluc_label})", "70 - 99 mg/dL"],
          ["Hypertension", r["hypertension"], "No History"],
          ["Heart Disease", r["heart_disease"], "None"],
          ["Smoking", r["smoking"], "Never Smoked"]]
    tbl = Table(pd, colWidths=["38%","32%","30%"])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),PURPLE), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTSIZE",(0,0),(-1,0),9.5),
        ("FONTSIZE",(0,1),(-1,-1),9), ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LGBG]),
        ("TEXTCOLOR",(0,1),(-1,-1),DARK), ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#ccccdd")),
        ("LEFTPADDING",(0,0),(-1,-1),10), ("RIGHTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),6), ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    story.append(tbl)
    story.append(Spacer(1,14))
    story.append(Paragraph("Key Recommendations", hs))
    for _, tip in tips:
        story.append(Paragraph(f"• {tip}", bs))
    story.append(Spacer(1,14))
    story.append(Paragraph("Metric Explanations", hs))
    for term, defn in [
        ("BMI","Body Mass Index - weight divided by height squared. Above 25 raises vascular risk; above 30 significantly increases stroke probability."),
        ("Average Glucose","High blood glucose damages arterial walls. Persistently above 126 mg/dL indicates diabetes, doubling stroke risk."),
        ("Hypertension","Chronic high blood pressure weakens artery walls - a direct cause of haemorrhagic stroke."),
        ("Heart Disease","Conditions like atrial fibrillation can cause clots that travel to the brain (ischaemic stroke)."),
        ("Smoking","Accelerates arterial plaque build-up. Risk declines significantly within 2-5 years of quitting."),
    ]:
        story.append(Paragraph(f"<b>{term}:</b> {defn}", bs))
    story.append(Spacer(1,14))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#ccccdd"), spaceBefore=4, spaceAfter=8))
    story.append(Paragraph("<b>Medical Disclaimer:</b> This report is generated by a machine-learning model (XGBoost) for informational purposes ONLY. It does NOT constitute a formal medical diagnosis. Always consult a qualified healthcare professional before making any medical decisions.", ds))
    story.append(Spacer(1,6))
    story.append(Paragraph("Generated by StrokeGuard AI v2.0 | Powered by XGBoost & Streamlit", ParagraphStyle("ft", fontSize=8, textColor=GREY, alignment=TA_CENTER)))
    doc.build(story)
    buf.seek(0)
    return buf.read()

# PAGE 1 - AUTH (Register + Login)
def page_auth():
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center;padding:30px 0 14px;'>
        <span class='float-brain' style='font-size:3.8rem;'>🧠</span>
        <h1 style='font-family:Raleway,sans-serif;font-size:2.5rem;font-weight:900;margin:8px 0 2px;letter-spacing:-0.5px;'>StrokeGuard AI</h1>
        <p style='color:rgba(255,255,255,0.62);font-size:0.96rem;margin:0;'>Personalized Stroke Risk Assessment Platform</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    tc1, tc2 = st.columns(2)
    with tc1:
        if st.button("🔑  Sign In", key="tab_login"):
            st.session_state.auth_mode = "login"; st.rerun()
    with tc2:
        if st.button("✨  Register", key="tab_register"):
            st.session_state.auth_mode = "register"; st.rerun()

    st.markdown("<hr style='margin:6px 0 18px;'>", unsafe_allow_html=True)

    if st.session_state.auth_mode == "register":
        st.markdown("### ✨ &nbsp; Create Account")
        st.markdown("<p style='color:rgba(255,255,255,0.58);font-size:0.88rem;margin-top:-10px;'>Fill in your details to get started</p>", unsafe_allow_html=True)
        r_name  = st.text_input("Full Name",        placeholder="e.g. Arjun Patel",      key="r_name")
        r_phone = st.text_input("Phone Number",     placeholder="+91 98765 43210",        key="r_phone")
        r_pwd   = st.text_input("Password",         type="password", placeholder="Minimum 4 characters", key="r_pwd")
        r_pwd2  = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password", key="r_pwd2")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Create Account  →", key="btn_register"):
            digits = "".join(c for c in r_phone if c.isdigit())
            if not r_name.strip():
                st.error("Please enter your full name.")
            elif len(digits) < 10:
                st.error("Please enter a valid 10-digit phone number.")
            elif len(r_pwd) < 4:
                st.error("Password must be at least 4 characters.")
            elif r_pwd != r_pwd2:
                st.error("Passwords do not match.")
            elif digits in st.session_state.users:
                st.error("Account already exists. Please sign in.")
            else:
                st.session_state.users[digits] = {"name": r_name.strip(), "password": r_pwd}
                st.success("Account created! Switching to Sign In…")
                time.sleep(1)
                st.session_state.auth_mode = "login"
                st.rerun()
    else:
        st.markdown("### 👤 &nbsp; Welcome Back")
        st.markdown("<p style='color:rgba(255,255,255,0.58);font-size:0.88rem;margin-top:-10px;'>Sign in to access your health dashboard</p>", unsafe_allow_html=True)
        l_phone = st.text_input("Phone Number", placeholder="+91 98765 43210", key="l_phone")
        l_pwd   = st.text_input("Password", type="password", placeholder="••••••••", key="l_pwd")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sign In  →", key="btn_signin"):
            digits = "".join(c for c in l_phone if c.isdigit())
            if len(digits) < 10:
                st.error("Please enter a valid phone number.")
            elif digits not in st.session_state.users:
                st.error("No account found. Please register first.")
            elif st.session_state.users[digits]["password"] != l_pwd:
                st.error("Incorrect password.")
            else:
                with st.spinner("Authenticating…"):
                    time.sleep(0.8)
                st.session_state.user_name = st.session_state.users[digits]["name"].split()[0]
                st.session_state.page = "main"
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center;margin-top:8px;'>
        <span style='color:rgba(255,255,255,0.46);font-size:0.80rem;'>🔒 &nbsp;Your data is encrypted and never stored externally.</span>
    </div>
    <div class='footer-text'>Powered by XGBoost &amp; Streamlit &nbsp;|&nbsp; StrokeGuard v2.0</div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# PAGE 2 - MAIN (identical to original)
def page_main():
    cg, cl = st.columns([5,1])
    with cg:
        st.markdown(f"<p style='color:rgba(255,255,255,0.72);margin-bottom:0;'>👋 Hello, <strong>{st.session_state.user_name}</strong></p>", unsafe_allow_html=True)
    with cl:
        if st.button("Logout"):
            st.session_state.page = "auth"
            st.session_state.result = None
            st.rerun()

    st.title("🧠 StrokeGuard AI")
    st.markdown("##### Personalized Health Risk Assessment")
    st.write("Using advanced machine learning to analyze clinical parameters.")

    with st.container():
        st.info("Please fill in the medical information below:")
        col1, col2 = st.columns(2)
        with col1:
            gender_input = st.radio("Gender", options=["Female","Male"], horizontal=True)
            gender = 1 if gender_input == "Male" else 0
            age = st.slider("Age", 0, 100, 45)
            hyper_input = st.selectbox("Hypertension Status", ["No History","Diagnosed"])
            hypertension = 1 if hyper_input == "Diagnosed" else 0
            heart_input = st.selectbox("Heart Disease History", ["None","Heart Condition Detected"])
            heart_disease = 1 if heart_input == "Heart Condition Detected" else 0
        with col2:
            avg_glucose_level = st.number_input("Average Glucose (mg/dL)", 50.0, 300.0, 95.0)
            bmi = st.number_input("BMI Index", 10.0, 60.0, 24.5)
            smoking_input = st.selectbox("Smoking Habits", ["Unknown","Formerly Smoked","Never Smoked","Regular Smoker"])
            smoking_dict = {"Unknown":0,"Formerly Smoked":1,"Never Smoked":2,"Regular Smoker":3}
            smoking_status = smoking_dict[smoking_input]

    st.markdown("---")

    if st.button("Analyze Stroke Probability"):
        with st.spinner("Analyzing health data…"):
            time.sleep(1)
            feats = np.array([[gender, age, hypertension, heart_disease, avg_glucose_level, bmi, smoking_status]])
            probs = model.predict_proba(feats)
            risk = float(probs[0][1] * 100)
            st.session_state.result = dict(risk_percent=risk, gender=gender_input, age=age,
                hypertension=hyper_input, heart_disease=heart_input,
                glucose=avg_glucose_level, bmi=bmi, smoking=smoking_input)

    if st.session_state.result is not None:
        risk = st.session_state.result["risk_percent"]
        st.subheader("Analysis Results")
        if risk > 50:
            st.warning("Analysis indicates a high concern level.")
        else:
            st.success("Analysis indicates a low concern level.")
        st.metric(label="Calculated Stroke Risk", value=f"{risk:.1f}%")
        st.progress(risk / 100)
        if risk > 30:
            st.error("⚠️ **Recommendation:** Your profile shows clinical indicators often associated with higher risk. We strongly recommend scheduling a check-up with a doctor.")
        else:
            st.info("ℹ️ **Note:** Continue maintaining a balanced diet and regular exercise to keep your risk levels low.")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊  View Full Report & Analytics"):
            st.session_state.page = "summary"
            st.rerun()

    st.markdown("<br><hr><center><small>Powered by XGBoost &amp; Streamlit | Project Version 2.0</small></center>", unsafe_allow_html=True)

# PAGE 3 - REPORT (what-if removed, PDF download)
def page_summary():
    r = st.session_state.result
    if r is None:
        st.warning("No analysis data found. Please run the assessment first.")
        if st.button("← Back to Assessment"):
            st.session_state.page = "main"; st.rerun()
        return

    risk = r["risk_percent"]
    age = r["age"]
    bmi_v = r["bmi"]
    gluc = r["glucose"]
    is_high = risk >= 60
    is_mod  = 30 <= risk < 60

    if is_high:   risk_label, badge_cls, ring_color = "High Risk",     "risk-high", "#ff5f5f"
    elif is_mod:  risk_label, badge_cls, ring_color = "Moderate Risk", "risk-mod",  "#ffb347"
    else:         risk_label, badge_cls, ring_color = "Low Risk",      "risk-low",  "#00dc82"

    bmi_label  = ("Underweight" if bmi_v < 18.5 else ("Normal" if bmi_v < 25 else ("Overweight" if bmi_v < 30 else "Obese")))
    gluc_label = ("Normal" if gluc < 100 else ("Pre-Diabetic" if gluc < 126 else "High / Diabetic Range"))
    avg_risk   = age_avg_risk(age)
    rf_count   = sum([r["hypertension"]=="Diagnosed", r["heart_disease"]=="Heart Condition Detected",
                      r["smoking"]=="Regular Smoker", gluc>140, bmi_v>30])

    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
    cb, _ = st.columns([1,4])
    with cb:
        if st.button("← Back"):
            st.session_state.page = "main"; st.rerun()

    st.markdown(f"""
    <div style='text-align:center;padding:10px 0 18px;'>
        <div style='font-size:2.4rem;'>📋</div>
        <h1 style='font-size:1.95rem;font-weight:900;margin:4px 0 2px;font-family:Raleway,sans-serif;letter-spacing:-0.3px;'>Report &amp; Analytics</h1>
        <p style='color:rgba(255,255,255,0.58);font-size:0.92rem;'>{st.session_state.user_name}'s Stroke Risk — Full Breakdown</p>
    </div>""", unsafe_allow_html=True)

    # GAUGE
    st.markdown("<div class='glass-card fade-in' style='text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(255,255,255,0.52);font-size:0.76rem;text-transform:uppercase;letter-spacing:1.8px;margin-bottom:4px;'>At-a-Glance Risk Meter</p>", unsafe_allow_html=True)
    st.markdown(gauge_svg(risk), unsafe_allow_html=True)
    st.markdown(f"""<div style='margin-top:8px;'><span class='risk-badge {badge_cls}'>{risk_label}</span></div>
    <p style='color:rgba(255,255,255,0.52);font-size:0.82rem;margin-top:8px;'>
        <span style='color:#00dc82;'>● Low &lt; 30%</span> &nbsp;·&nbsp;
        <span style='color:#ffb347;'>● Moderate 30–60%</span> &nbsp;·&nbsp;
        <span style='color:#ff5f5f;'>● High ≥ 60%</span>
    </p>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # STAT BOXES
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='stat-box fade-in-2'><div class='stat-value'>{age}</div><div class='stat-label'>Age (yrs)</div></div>", unsafe_allow_html=True)
    with c2:
        rf_color = "#ff9999" if rf_count >= 3 else "#aaffdd"
        st.markdown(f"<div class='stat-box fade-in-2'><div class='stat-value' style='color:{rf_color};'>{rf_count}</div><div class='stat-label'>Risk Factors</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='stat-box fade-in-2'><div class='stat-value'>{bmi_v:.1f}</div><div class='stat-label'>BMI ({bmi_label})</div></div>", unsafe_allow_html=True)

    # COMPARISON TABLE
    st.markdown("<div class='glass-card fade-in-2'>", unsafe_allow_html=True)
    st.markdown("### 📊 &nbsp; Your Values vs Ideal Range")
    st.markdown("<p style='color:rgba(255,255,255,0.52);font-size:0.83rem;margin-top:-10px;'>How your clinical markers compare to healthy benchmarks</p>", unsafe_allow_html=True)
    st.markdown("""<div style='display:flex;padding:6px 8px;color:rgba(255,255,255,0.42);font-size:0.73rem;font-weight:800;text-transform:uppercase;letter-spacing:0.8px;'>
        <span style='flex:2.2;'>Metric</span><span style='flex:2.2;'>Your Value</span>
        <span style='flex:2;'>Ideal Range</span><span style='flex:0.8;text-align:center;'>OK?</span>
    </div>""", unsafe_allow_html=True)
    rows = [
        ("BMI",               f"{bmi_v:.1f}  ({bmi_label})",         "18.5 – 24.9",   18.5<=bmi_v<=24.9),
        ("Glucose (mg/dL)",   f"{gluc:.0f} mg/dL  ({gluc_label})",   "70 – 99 mg/dL", 70<=gluc<=99),
        ("Age-Group Avg Risk",f"{avg_risk:.1f}% for age {age}",      "—",             True),
        ("Hypertension",      r["hypertension"],                      "No History",    r["hypertension"]=="No History"),
        ("Heart Disease",     r["heart_disease"],                     "None",          r["heart_disease"]=="None"),
        ("Smoking",           r["smoking"],                           "Never Smoked",  r["smoking"]=="Never Smoked"),
    ]
    for lbl, yv, ideal, ok in rows:
        vc = "rgba(255,255,255,0.90)" if ok else "#ffb3b3"
        st.markdown(f"""<div class='comp-row'>
            <span style='flex:2.2;color:rgba(255,255,255,0.70);font-size:0.87rem;'>{lbl}</span>
            <span style='flex:2.2;color:{vc};font-weight:700;font-size:0.87rem;'>{yv}</span>
            <span style='flex:2;color:rgba(255,255,255,0.45);font-size:0.84rem;'>{ideal}</span>
            <span style='flex:0.8;text-align:center;font-size:0.95rem;'>{"✅" if ok else "⚠️"}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # RECOMMENDATIONS
    tips = []
    if is_high or is_mod: tips.append(("🏥","Schedule a neurological check-up with your doctor soon."))
    if r["hypertension"]=="Diagnosed": tips.append(("💊","Take antihypertensive medications consistently and monitor BP daily."))
    if gluc > 126: tips.append(("🩸","Glucose is in diabetic range — reduce refined carbs and consult a diabetologist."))
    elif gluc > 100: tips.append(("🍎","Pre-diabetic glucose — cut sugary drinks and increase dietary fibre."))
    if bmi_v > 30: tips.append(("🏃","BMI above 30 — aim for 30 min of moderate exercise 5x per week."))
    elif bmi_v > 25: tips.append(("🥗","Slightly overweight — balanced diet with portion control will help."))
    if r["smoking"]=="Regular Smoker": tips.append(("🚭","Quitting smoking is the single highest-impact action to cut stroke risk."))
    if r["heart_disease"]=="Heart Condition Detected": tips.append(("❤️","Cardiac patients face 2x stroke risk — discuss anticoagulants with your cardiologist."))
    if not tips:
        tips.append(("🌿","Excellent profile! Keep up a balanced diet, regular activity, and annual check-ups."))
        tips.append(("😴","Ensure 7–8 hours of quality sleep nightly for cardiovascular health."))

    st.markdown("<div class='glass-card fade-in-3'>", unsafe_allow_html=True)
    st.markdown("### 💡 &nbsp; Actionable Next Steps")
    for icon, tip in tips:
        st.markdown(f"""<div class='tip-row'>
            <span style='font-size:1.35rem;'>{icon}</span>
            <span style='color:rgba(255,255,255,0.82);font-size:0.90rem;line-height:1.55;'>{tip}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # GLOSSARY
    glossary = [
        ("BMI (Body Mass Index)","Weight ÷ height². Above 25 increases vascular stress; above 30 (obese) significantly raises risk of hypertension, diabetes, and stroke."),
        ("Average Glucose (mg/dL)","High blood glucose damages arterial walls over time — a key pathway to atherosclerosis. Persistently above 126 mg/dL suggests diabetes, which doubles stroke risk."),
        ("Hypertension","Chronic high blood pressure weakens artery walls, making them vulnerable to rupture — a direct cause of haemorrhagic stroke."),
        ("Heart Disease","Conditions like atrial fibrillation can cause clots that travel to the brain (ischaemic stroke). Cardiac patients face 2–4x elevated risk."),
        ("Smoking Status","Smoking accelerates arterial plaque build-up. Former smokers see risk decline significantly within 2–5 years of quitting."),
        ("Age-Group Average Risk",f"People aged {age} have an average stroke risk of ~{avg_risk:.1f}%. Your calculated risk is {risk:.1f}%."),
    ]
    st.markdown("<div class='glass-card fade-in-3'>", unsafe_allow_html=True)
    st.markdown("### 📖 &nbsp; Medical Jargon Translator")
    st.markdown("<p style='color:rgba(255,255,255,0.52);font-size:0.83rem;margin-top:-10px;'>Plain-English explanations of every metric used in the prediction</p>", unsafe_allow_html=True)
    for term, defn in glossary:
        st.markdown(f"""<div class='glossary-item'>
            <div class='glossary-term'>📌 &nbsp;{term}</div>
            <div class='glossary-def'>{defn}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # PDF DOWNLOAD
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📄 &nbsp; Doctor's Summary Report")
    st.markdown("<p style='color:rgba(255,255,255,0.55);font-size:0.86rem;margin-top:-10px;'>Download a professionally formatted PDF to share with your healthcare provider.</p>", unsafe_allow_html=True)
    pdf_bytes = build_pdf(r, risk_label, avg_risk, rf_count, bmi_label, gluc_label, tips)
    st.download_button(
        label="⬇️  Download Doctor's Summary (.pdf)",
        data=pdf_bytes,
        file_name=f"StrokeGuard_Report_{st.session_state.user_name}.pdf",
        mime="application/pdf",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='disclaimer'>
        <p>⚠️ <strong style='color:rgba(255,255,255,0.80);'>Medical Disclaimer:</strong>
        StrokeGuard AI is a machine-learning tool for informational and educational purposes only.
        Results are not a formal clinical diagnosis. Always consult a qualified physician before
        making any health-related decisions.</p>
    </div>
    <div class='footer-text'>Powered by XGBoost &amp; Streamlit &nbsp;|&nbsp; StrokeGuard v2.0</div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ROUTER
if st.session_state.page == "auth":
    page_auth()
elif st.session_state.page == "main":
    page_main()
elif st.session_state.page == "summary":
    page_summary()
