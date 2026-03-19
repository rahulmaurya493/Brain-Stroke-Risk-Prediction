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

st.markdown("""
    <style>
    /* Main Background remains as you liked */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    /* Glassmorphism Card */
    [data-testid="stVerticalBlock"] > div:nth-child(3) {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }

    /* Instruction Text Visibility Fix */
    .stAlert p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Button with Touch Animation */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        height: 3.5em;
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: white;
        border: none;
        transition: all 0.2s ease; /* Faster transition for snappier feel */
        font-weight: bold;
        font-size: 18px;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Hover Effect */
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.6); /* Cyan Glow */
    }

    /* TOUCH/CLICK ANIMATION: Shrinks slightly when clicked */
    .stButton>button:active {
        transform: scale(0.95);
        box-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }

    /* Smooth Fade-in for Content Loading */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main-result-container {
        animation: fadeIn 0.8s ease-out;
    }

    /* Metric Styling */
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# Ligten--- Custom Styling (The "Satisfying & Readable" Look) ---
# st.markdown("""
#     <style>
#     /* Main Background */
#     .stApp {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         color: white;
#     }

#     /* Glassmorphism Card for Inputs */
#     [data-testid="stVerticalBlock"] > div:nth-child(3) {
#         background: rgba(255, 255, 255, 0.1);
#         backdrop-filter: blur(10px);
#         border-radius: 20px;
#         padding: 30px;
#         border: 1px solid rgba(255, 255, 255, 0.2);
#         box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
#     }

#     /* Input Label Visibility */
#     .stMarkdown p, label, .stSelectbox label, .stNumberInput label, .stRadio label {
#         color: #ffffff !important;
#         font-weight: 600 !important;
#         text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
#     }

#     /* Button Styling */
#     .stButton>button {
#         width: 100%;
#         border-radius: 50px;
#         height: 3.5em;
#         background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
#         color: white;
#         border: none;
#         transition: 0.5s;
#         font-weight: bold;
#         font-size: 18px;
#         text-transform: uppercase;
#         letter-spacing: 1px;
#         box-shadow: 0 4px 15px rgba(0,0,0,0.2);
#     }
    
#     .stButton>button:hover {
#         transform: translateY(-3px);
#         box-shadow: 0 6px 20px rgba(0,0,0,0.4);
#         color: #fff;
#     }

#     /* Metric/Result Styling */
#     div[data-testid="stMetricValue"] {
#         color: #ffffff !important;
#         background: rgba(0,0,0,0.2);
#         border-radius: 10px;
#         padding: 10px;
#     }
#     </style>
#     """, unsafe_allow_html=True)


# DARK --- Custom Styling (Fixed Visibility) ---
# st.markdown("""
#     <style>
#     /* Main Background */
#     .stApp {
#         background: linear-gradient(135deg, #1e3a8a 0%, #4c1d95 100%);
#         color: white;
#     }

#     /* Glassmorphism Card for Inputs */
#     [data-testid="stVerticalBlock"] > div:nth-child(3) {
#         background: rgba(255, 255, 255, 0.05);
#         backdrop-filter: blur(15px);
#         border-radius: 20px;
#         padding: 30px;
#         border: 1px solid rgba(255, 255, 255, 0.1);
#     }

#     /* FIX: Visibility for "Please fill in the medical information" */
#     .stAlert p {
#         color: #ffffff !important;
#         font-size: 18px !important;
#         font-weight: 700 !important;
#     }
    
#     /* Make Alert box background slightly darker for contrast */
#     div[data-testid="stNotification"] {
#         background-color: rgba(0, 0, 0, 0.3) !important;
#         border: 1px solid rgba(255, 255, 255, 0.2);
#     }

#     /* Input Label Visibility */
#     label, .stSelectbox label, .stNumberInput label, .stRadio label {
#         color: #ffffff !important;
#         font-weight: 600 !important;
#     }

#     /* Button Styling */
#     .stButton>button {
#         width: 100%;
#         border-radius: 50px;
#         height: 3.5em;
#         background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
#         color: white;
#         border: none;
#         font-weight: bold;
#         transition: 0.3s;
#     }
    
#     .stButton>button:hover {
#         transform: scale(1.02);
#         box-shadow: 0 10px 20px rgba(0,0,0,0.3);
#     }
#     </style>
#     """, unsafe_allow_html=True)


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
