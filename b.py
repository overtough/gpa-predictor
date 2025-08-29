import pandas as pd
import glob
from subject_name_map import SUBJECT_NAME_MAP
import manual_clusters

s = set()
reverse_name_map = {v.upper(): k for k, v in SUBJECT_NAME_MAP.items()}
for f in glob.glob('*_ExternalResults.xlsx'):
    df = pd.read_excel(f)
    s.update(df['Subject'].astype(str).str.strip().str.upper().map(lambda x: reverse_name_map.get(x, x)).unique())

known = set(manual_clusters.SUBJECT_TO_CLUSTER_NAME.keys())
unknown = s - known

print("Subjects missing from SUBJECT_TO_CLUSTER_NAME:")
for subj in sorted(unknown):
    print(f'"{subj}",')