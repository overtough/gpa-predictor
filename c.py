import pandas as pd

# Load the combined class data
df = pd.read_excel('data/class_combined_data.xlsx')

# Filter for P_PROG (Python Programming)
p_prog_df = df[df['Subject'].str.upper() == 'P_PROG']

# Save to CSV
p_prog_df.to_csv('p_prog_details.csv', index=False)

print("Exported P_PROG details to p_prog_details.csv")
print(p_prog_df.head())  # Show the first few rows for confirmation