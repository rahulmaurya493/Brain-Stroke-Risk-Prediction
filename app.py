import streamlit as st
import numpy as np
import pickle
import xgboost as xgb

# --- Configure the Page ---
st.set_page_config(page_title="Brain Stroke Predictor", page_icon="🧠", layout="centered")

# --- Load the Model ---
@st.cache_resource
def load_model():
    with open('stroke_model.pkl', 'rb') as file:
        model = pickle.load(file)
    return model

model = load_model()

# --- Build the UI ---
st.title("🧠 Brain Stroke Prediction App")
st.write("Enter the patient's medical details below to predict the likelihood of a brain stroke. *Note: This is a machine learning demo, not professional medical advice.*")

st.markdown("---")

# Create input fields in columns for a cleaner UI
col1, col2 = st.columns(2)

with col1:
    # Assuming 0 = Female, 1 = Male based on standard datasets
    gender_input = st.selectbox("Gender", options=["Female", "Male"])
    gender = 1 if gender_input == "Male" else 0
    
    age = st.number_input("Age", min_value=0.0, max_value=120.0, value=50.0, step=1.0)
    
    hyper_input = st.selectbox("Hypertension (High Blood Pressure)", options=["No", "Yes"])
    hypertension = 1 if hyper_input == "Yes" else 0
    
    heart_input = st.selectbox("Heart Disease", options=["No", "Yes"])
    heart_disease = 1 if heart_input == "Yes" else 0

with col2:
    avg_glucose_level = st.number_input("Average Glucose Level", min_value=0.0, max_value=300.0, value=100.0)
    
    bmi = st.number_input("BMI (Body Mass Index)", min_value=0.0, max_value=100.0, value=25.0)
    
    # Dataset specific smoking status mappings (0, 1, 2, 3)
    smoking_input = st.selectbox("Smoking Status", options=[
        "Status 0 (e.g., Unknown)", 
        "Status 1 (e.g., Formerly Smoked)", 
        "Status 2 (e.g., Never Smoked)", 
        "Status 3 (e.g., Smokes)"
    ])
    # Extract just the integer from the selection
    smoking_status = int(smoking_input.split(" ")[1])

st.markdown("---")

# --- Prediction Logic ---
if st.button("Predict Stroke Risk", type="primary", use_container_width=True):
    # Format the inputs exactly as the model expects: 
    # [gender, age, hypertension, heart_disease, avg_glucose_level, bmi, smoking_status]
    input_features = np.array([[gender, age, hypertension, heart_disease, avg_glucose_level, bmi, smoking_status]])
    
    # Make prediction
    prediction = model.predict(input_features)
    
    # Display Results
    st.subheader("Prediction Result:")
    if prediction[0] == 1:
        st.error("⚠️ **High Risk of Stroke Detected.** Please consult a healthcare professional.")
    else:
        st.success("✅ **Low Risk of Stroke.** Keep maintaining a healthy lifestyle!")