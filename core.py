import pandas as pd
import re
from subject_name_map import SUBJECT_NAME_MAP
from subject_credits import SUBJECT_CREDITS

def preprocess_excel(path):
    """Loads and performs initial cleaning on the results Excel file."""
    df = pd.read_excel(path)
    df.columns = [col.strip() for col in df.columns]

    if 'Subject' in df.columns:
        df['Subject'] = df['Subject'].astype(str)
    if 'Assessment' in df.columns:
        df['Assessment'] = df['Assessment'].astype(str)
    return df

def ugc_grade_point_from_percent(percent):

    if pd.isna(percent):
        return 0
    if percent >= 90: return 10
    if percent >= 80: return 9
    if percent >= 70: return 8
    if percent >= 60: return 7
    if percent >= 50: return 6
    if percent >= 40: return 5
    return 0

def predict_subjectwise_ugc(df_result, latest_semester_str, roll, prediction_mode):

    subject_credits_map = {k.strip().lower(): v for k, v in SUBJECT_CREDITS.items()}
    sem_df = df_result[df_result['Semester'] == latest_semester_str].copy()
    sem_df['Assessment'] = sem_df['Assessment'].str.strip().str.upper()
    
    subjects = sem_df['Subject'].unique()
    results = []

    for subject_code in subjects:
        predicted_internal = None
        subject_rows = sem_df[sem_df['Subject'] == subject_code]
        
        if prediction_mode == "USE_AVERAGE":
            mark1_row = subject_rows[subject_rows['Assessment'].str.contains("1ST")]
            mark2_row = subject_rows[subject_rows['Assessment'].str.contains("2ND")]
            if not mark1_row.empty and not mark2_row.empty:
                mark1 = mark1_row['Total (40)'].iloc[0]
                mark2 = mark2_row['Total (40)'].iloc[0]
                predicted_internal = (mark1 + mark2) / 2.0
        
        elif prediction_mode == "ESTIMATE_2ND":
            mark1_row = subject_rows[subject_rows['Assessment'].str.contains("1ST")]
            if not mark1_row.empty:
                mark1 = mark1_row['Total (40)'].iloc[0]
                estimated_mark2 = min(mark1 * 1.10, 40)
                predicted_internal = (mark1 + estimated_mark2) / 2.0

        predicted_external = None
        if predicted_internal is not None:
            predicted_external = (predicted_internal / 40.0) * 60.0
        else:
            predicted_external = 0 

        total_marks = None
        grade_point = None
        if predicted_internal is not None and predicted_external is not None:
            total_marks = min(predicted_internal + predicted_external, 100.0)
            percent = total_marks
            grade_point = ugc_grade_point_from_percent(percent)

        credits = subject_credits_map.get(subject_code.strip().lower(), 0)

        results.append({
            'subject': subject_code,
            'predicted_internal': round(predicted_internal, 2) if predicted_internal is not None else 'N/A',
            'predicted_external': round(predicted_external, 2) if predicted_external is not None else 'N/A',
            'total_marks': round(total_marks, 2) if total_marks is not None else 'N/A',
            'grade_point': grade_point,
            'credits': credits
        })
        
    return results

def calculate_predicted_sgpa_ugc(subjects_data):
    """Calculates the final SGPA from the subject-wise prediction data."""
    total_credits = 0
    weighted_sum = 0
    for subject_data in subjects_data:
        credits = subject_data.get('credits', 0)
        grade_point = subject_data.get('grade_point')
        
        try:
            credits = float(credits)
            grade_point = float(grade_point)
        except (TypeError, ValueError):
            continue # Skip if data is invalid
            
        if credits > 0 and not pd.isna(grade_point):
            total_credits += credits
            weighted_sum += credits * grade_point
            
    return weighted_sum / total_credits if total_credits > 0 else 0.0

