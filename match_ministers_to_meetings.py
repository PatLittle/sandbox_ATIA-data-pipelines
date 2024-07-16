


import pandas as pd
from fuzzywuzzy import fuzz, process

# Load the data
ministers_df = pd.read_csv('output.csv')
meetings_df = pd.read_csv('full_witness_meetings_output.csv')

# Ensure columns for matching exist in both dataframes
if 'minister_name' not in ministers_df.columns or 'meeting_person' not in meetings_df.columns:
    raise ValueError("Required columns are missing in the input files.")

# Function to match a single minister to the meeting records
def match_minister_to_meetings(minister, meeting_names):
    match, score = process.extractOne(minister, meeting_names, scorer=fuzz.token_sort_ratio)
    return match, score

# Apply matching for each minister
results = []
meeting_names = meetings_df['meeting_person'].tolist()

for index, row in ministers_df.iterrows():
    minister_name = row['minister_name']
    match, score = match_minister_to_meetings(minister_name, meeting_names)
    results.append({
        'minister_name': minister_name,
        'matched_meeting_person': match,
        'confidence_score': score
    })

# Create a DataFrame for the results
results_df = pd.DataFrame(results)

# Save the results to a CSV file
results_df.to_csv('minister_meeting_associations.csv', index=False)

print("Matching completed. Results saved to 'minister_meeting_associations.csv'.")
