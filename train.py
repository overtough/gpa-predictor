import os
import pandas as pd
from scrape import scrape_student
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from manual_clusters import SUBJECT_TO_CLUSTER_TYPE, SUBJECT_TO_CLUSTER_NAME
from subject_name_map import SUBJECT_NAME_MAP, FULLNAME_TO_CODE
import glob

SAVE_DIR = "."
os.makedirs(SAVE_DIR, exist_ok=True)

import os
import pandas as pd
from scrape import scrape_student
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from manual_clusters import SUBJECT_TO_CLUSTER_TYPE, SUBJECT_TO_CLUSTER_NAME
from subject_name_map import SUBJECT_NAME_MAP, FULLNAME_TO_CODE
import glob

SAVE_DIR = "."
os.makedirs(SAVE_DIR, exist_ok=True)

ROLL_NUMBERS = [
    "24BD1A0521", "24BD1A0522", "24BD1A0523", "24BD1A0524", "24BD1A0525", "24BD1A0526", "24BD1A0527", "24BD1A0528", "24BD1A0529",
    "24BD1A052A", "24BD1A052B", "24BD1A052C", "24BD1A052D", "24BD1A052E", "24BD1A052F", "24BD1A052G", "24BD1A052H", "24BD1A052J", "24BD1A052K", "24BD1A052L", "24BD1A052M", "24BD1A052N", "24BD1A052P", "24BD1A052Q", "24BD1A052R", "24BD1A052T", "24BD1A052U", "24BD1A052V", "24BD1A052W", "24BD1A052X", "24BD1A052Y", "24BD1A052Z",
    "24BD1A0531", "24BD1A0532", "24BD1A0533", "24BD1A0534", "24BD1A0535", "24BD1A0536", "24BD1A0537", "24BD1A0538", "24BD1A0539",
    "24BD1A053A", "24BD1A053B", "24BD1A053C", "24BD1A053D", "24BD1A053E", "24BD1A053F", "24BD1A053G", "24BD1A053H", "24BD1A053J", "24BD1A053K", "24BD1A053L", "24BD1A053M", "24BD1A053N", "24BD1A053P", "24BD1A053Q", "24BD1A053R", "24BD1A053T", "24BD1A053U", "24BD1A053V", "24BD1A053W", "24BD1A053X", "24BD1A053Y", "24BD1A053Z"
]

all_data = []

for roll in ROLL_NUMBERS:
    save_path = os.path.join(SAVE_DIR, f"{roll}_Results.xlsx")
    if not os.path.exists(save_path):
        print(f"Scraping data for {roll}...")
        scrape_student(roll)
    
    if os.path.exists(save_path):
        try:
            df = pd.read_excel(save_path)
            df['Roll'] = roll
            all_data.append(df)
        except Exception as e:
            print(f"Error reading {save_path}: {e}")

if not all_data:
    print("No data available to train models.")
    exit()

combined_df = pd.concat(all_data, ignore_index=True)
combined_df['Subject'] = combined_df['Subject'].str.strip().str.upper()
combined_df['ClusterType'] = combined_df['Subject'].map(SUBJECT_TO_CLUSTER_TYPE).fillna('Unknown')
combined_df['ClusterName'] = combined_df['Subject'].map(SUBJECT_TO_CLUSTER_NAME).fillna('Unknown')

for cluster_type in ['Theory', 'Lab']:
    df_type = combined_df[combined_df['ClusterType'] == cluster_type].dropna()
    if df_type.empty:
        continue
        
    features = df_type[["Assignment (10)", "Subjective (20)", "Quiz (10)", "DTD", "Test"]]
    subjects = df_type[["Subject"]]
    clusters = df_type[["ClusterName"]]
    target = df_type["Total (40)"]
    
    subject_ohe = OneHotEncoder(handle_unknown='ignore')
    subject_features = subject_ohe.fit_transform(subjects)
    
    cluster_ohe = OneHotEncoder(handle_unknown='ignore')
    cluster_features = cluster_ohe.fit_transform(clusters)
    
    X = np.hstack([features.values, subject_features.toarray(), cluster_features.toarray()])
    y = target.values
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    joblib.dump((model, subject_ohe, cluster_ohe), f"rf_model_{cluster_type}.pkl")
    print(f"Model for {cluster_type} trained and saved.")

external_dfs = []
for ext_file in glob.glob('*_ExternalResults.xlsx'):
    df = pd.read_excel(ext_file)
    roll = ext_file.split('_')[0]
    df['Roll'] = roll
    internal_df = combined_df[combined_df['Roll'] == roll]
    
    external_dfs.append(df)

if external_dfs:
    all_external_df = pd.concat(external_dfs, ignore_index=True)
    print(f"Loaded {len(all_external_df)} external records.")

print("Training script finished.")


all_data = []

for roll in ROLL_NUMBERS:
    save_path = os.path.join(SAVE_DIR, f"{roll}_Results.xlsx")
    if not os.path.exists(save_path):
        print(f"Scraping data for {roll}...")
        scrape_student(roll)
    
    if os.path.exists(save_path):
        try:
            df = pd.read_excel(save_path)
            df['Roll'] = roll
            all_data.append(df)
        except Exception as e:
            print(f"Error reading {save_path}: {e}")

if not all_data:
    print("No data available to train models.")
    exit()

combined_df = pd.concat(all_data, ignore_index=True)
combined_df['Subject'] = combined_df['Subject'].str.strip().str.upper()
combined_df['ClusterType'] = combined_df['Subject'].map(SUBJECT_TO_CLUSTER_TYPE).fillna('Unknown')
combined_df['ClusterName'] = combined_df['Subject'].map(SUBJECT_TO_CLUSTER_NAME).fillna('Unknown')


for cluster_type in ['Theory', 'Lab']:
    df_type = combined_df[combined_df['ClusterType'] == cluster_type].dropna()
    if df_type.empty:
        continue
        
    features = df_type[["Assignment (10)", "Subjective (20)", "Quiz (10)", "DTD", "Test"]]
    subjects = df_type[["Subject"]]
    clusters = df_type[["ClusterName"]]
    target = df_type["Total (40)"]
    
    subject_ohe = OneHotEncoder(handle_unknown='ignore')
    subject_features = subject_ohe.fit_transform(subjects)
    
    cluster_ohe = OneHotEncoder(handle_unknown='ignore')
    cluster_features = cluster_ohe.fit_transform(clusters)
    
    X = np.hstack([features.values, subject_features.toarray(), cluster_features.toarray()])
    y = target.values
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    joblib.dump((model, subject_ohe, cluster_ohe), f"rf_model_{cluster_type}.pkl")
    print(f"Model for {cluster_type} trained and saved.")

external_dfs = []
for ext_file in glob.glob('*_ExternalResults.xlsx'):
    df = pd.read_excel(ext_file)
    roll = ext_file.split('_')[0]
    df['Roll'] = roll
    internal_df = combined_df[combined_df['Roll'] == roll]
    
    external_dfs.append(df)

if external_dfs:
    all_external_df = pd.concat(external_dfs, ignore_index=True)
    print(f"Loaded {len(all_external_df)} external records.")

print("Training script finished.")
