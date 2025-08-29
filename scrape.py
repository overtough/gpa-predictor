import streamlit as st
import subprocess
import pandas as pd
import os
import json
import re
from core import preprocess_excel, predict_subjectwise_ugc, calculate_predicted_sgpa_ugc
from subject_name_map import SUBJECT_NAME_MAP

st.set_page_config(page_title="GPA Predictor", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        body, .stApp {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(to right top, #1e2a3a, #2b3e50, #3a5367, #4a697f, #5b8098);
            color: #ffffff;
        }

        .card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        }

        .main-title {
            font-size: 3rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 20px;
            color: #ffffff;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        }
        h1, h2, h3, h4, h5, h6 {
            color: #e0e0e0;
        }

        .stTextInput input {
            background-color: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 10px 15px;
            font-size: 1rem;
            text-align: center;
        }

        .stButton button {
            background-color: #ff4b4b;
            color: white;
            border-radius: 10px;
            border: none;
            padding: 10px 20px;
            transition: background-color 0.3s ease;
        }
        .stButton button:hover {
            background-color: #ff6b6b;
        }

        .stDataFrame {
            background-color: transparent;
        }
        [data-testid="stMetric"] {
            background-color: rgba(0, 255, 127, 0.1);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(0, 255, 127, 0.2);
        }
        [data-testid="stMetricLabel"] {
            font-size: 1.1rem;
            color: #a0a0a0;
        }
        [data-testid="stMetricValue"] {
            font-size: 2.5rem;
            font-weight: 700;
            color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<p class='main-title'>🎓 GPA Predictor</p>", unsafe_allow_html=True)

roll_input = st.text_input(
    "Enter your roll number to begin", 
    key="roll_input", 
    label_visibility="collapsed", 
    placeholder="Enter your roll number..."
)

if not roll_input:
    st.info("Please enter a roll number to fetch your academic data.")
    st.stop()

roll = roll_input.strip().upper()
excel_path = f"{roll}_Results.xlsx"
info_path = f"{roll}_Info.json"

if not os.path.exists(excel_path):
    with st.spinner(f"🚀 Scraping data for {roll}... This might take a moment."):
        script_path = os.path.join(os.path.dirname(__file__), "scrape.py")
        try:
            result = subprocess.run(
                ["python", script_path, roll],
                capture_output=True, text=True, timeout=90
            )
            if result.returncode != 0:
                st.error("❌ Failed to scrape data. The process may have timed out or the roll number is invalid.")
                st.code(result.stderr)
                st.stop()
            st.success("✅ Scraping complete!")
        except subprocess.TimeoutExpired:
            st.error("⏳ Scraping took too long and was stopped. Please try again.")
            st.stop()

try:
    df_result = preprocess_excel(excel_path)
    with open(info_path, 'r', encoding='utf-8') as f:
        profile_info = json.load(f)
except FileNotFoundError:
    st.error("📂 Could not find scraped data files. The scraping process may have failed.")
    st.stop()

with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header(f"👋 Welcome, {profile_info.get('name', 'Student')}!")
    col1, col2 = st.columns(2)
    col1.markdown(f"**Department:** {profile_info.get('department', 'N/A')}")
    col2.markdown(f"**Section:** {profile_info.get('section', 'N/A')}")
    st.markdown('</div>', unsafe_allow_html=True)


if not df_result.empty:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        latest_semester_str = df_result['Semester'].dropna().astype(str).max()
        
        latest_sem_df = df_result[df_result['Semester'] == latest_semester_str].copy()
        
        if 'Assessment' in latest_sem_df.columns:
            latest_sem_df['Assessment'] = latest_sem_df['Assessment'].astype(str).str.strip().str.upper()
            available_assessments = latest_sem_df['Assessment'].unique().tolist()
        else:
            available_assessments = []

        available_internals = sorted([asm for asm in available_assessments if "INTERNAL" in asm])
        has_1st_available = any("1ST" in s for s in available_internals)
        has_2nd_available = any("2ND" in s for s in available_internals)

        prediction_mode = None
        if has_1st_available and has_2nd_available:
            prediction_mode = "USE_AVERAGE"
        elif has_1st_available and not has_2nd_available:
            prediction_mode = "ESTIMATE_2ND"
        
        if prediction_mode:
            st.header(f"📈 Predictions for {latest_semester_str}")
            
            if prediction_mode == "USE_AVERAGE":
                st.info("✅ Both 1st and 2nd internal marks are available. The prediction will be based on their average.")
            elif prediction_mode == "ESTIMATE_2ND":
                st.info("⚠️ Only 1st internal marks are available. The 2nd internal will be estimated to create a forecast.")

            if st.button("Calculate Predicted SGPA", type="primary"):
                with st.spinner("🧠 Calculating predictions..."):
                    subjectwise_ugc = predict_subjectwise_ugc(df_result, latest_semester_str, roll, prediction_mode)
                    predicted_sgpa_ugc = calculate_predicted_sgpa_ugc(subjectwise_ugc)

                    st.metric(label="Predicted SGPA", value=f"{predicted_sgpa_ugc:.2f}")

                    st.markdown("---")
                    st.subheader("Subject-wise Breakdown")
                    predictions_df_ugc = pd.DataFrame(subjectwise_ugc)
                    predictions_df_ugc['Subject'] = predictions_df_ugc['subject'].map(SUBJECT_NAME_MAP).fillna(predictions_df_ugc['subject'])
                    
                    st.dataframe(predictions_df_ugc[[
                        "Subject", "predicted_internal", "predicted_external",
                        "total_marks", "grade_point", "credits"
                    ]], use_container_width=True)
        else:
            st.warning("No internal assessment data found for the latest semester to make predictions.")
            
        st.markdown('</div>', unsafe_allow_html=True)


with st.expander("📄 View All Scraped Marks"):
    st.dataframe(df_result, use_container_width=True)

if st.button("🗑️ Logout and Clear Data"):
    for file_path in [excel_path, info_path]:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                st.error(f"Error removing file {file_path}: {e}")
    st.success("Logged out and all data has been cleared.")
    st.rerun()

