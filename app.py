import streamlit as st
import numpy as np
import pickle
import xgboost as xgb
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="StrokeGuard AI", 
    page_icon="🧠", 
    layout="centered"
)

# --- Custom Styling (The "Satisfying" Look) ---
# --- Custom Styling (The "Satisfying" Look) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #4A90E2;
        color: white;
        border: none;
        transition: 0.3s;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #357ABD;
        transform: scale(1.02);
    }
    div[data-testid="stMetricValue"] {
        font-size: 40px;
        color: #4A90E2;
    }
    </style>
    """, unsafe_allow_html=True) # Changed from unsafe_all_header_strings

# --- Load the Model ---
@st.cache_resource
def load_model():
    # Ensure this file exists in your GitHub repository
    with open('stroke_model.pkl', 'rb') as file:
        model = pickle.load(file)
    return model

model = load_model()

# --- Header Section ---
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
        # Map labels to the numeric values your model was trained on
        smoking_dict = {"Unknown": 0, "Formerly Smoked": 1, "Never Smoked": 2, "Regular Smoker": 3}
        smoking_status = smoking_dict[smoking_input]

st.markdown("---")

# --- Prediction Logic ---
if st.button("Analyze Stroke Probability"):
    with st.spinner('Analyzing health data...'):
        time.sleep(1) # Visual effect for "satisfying" feel
        
        # Prepare Features
        input_features = np.array([[gender, age, hypertension, heart_disease, avg_glucose_level, bmi, smoking_status]])
        
        # Get Probability (This gives [Prob of Class 0, Prob of Class 1])
        probabilities = model.predict_proba(input_features)
        risk_percent = float(probabilities[0][1] * 100)
        
        # Display Output
        st.subheader("Analysis Results")
        
        # Visual Progress Bar
        if risk_percent > 50:
            st.warning(f"Analysis indicates a high concern level.")
            color = "red"
        else:
            st.success(f"Analysis indicates a low concern level.")
            color = "green"

        # Metric and Progress
        st.metric(label="Calculated Stroke Risk", value=f"{risk_percent:.1f}%")
        st.progress(risk_percent / 100)
        
        # Detailed Guidance
        if risk_percent > 30:
            st.error("⚠️ **Recommendation:** Your profile shows clinical indicators often associated with higher risk. We strongly recommend scheduling a check-up with a doctor.")
        else:
            st.info("ℹ️ **Note:** Continue maintaining a balanced diet and regular exercise to keep your risk levels low.")

# --- Footer ---
st.markdown("<br><hr><center><small>Powered by XGBoost & Streamlit | Project Version 2.0</small></center>", unsafe_allow_html=True)
