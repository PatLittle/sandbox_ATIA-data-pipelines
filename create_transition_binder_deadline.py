import pandas as pd
from datetime import datetime, timedelta
import json

# Load the existing JSON file
existing_json_path = 'minister.json'
with open(existing_json_path, 'r', encoding='utf-8') as f:
    existing_data = json.load(f)

# Prepare the data for the new CSV
csv_data = []

for dept_code, ministry in existing_data.items():
    for minister in ministry['ministers']:
        # Calculate the deadline which is 120 days after the start_date
        start_date = datetime.strptime(minister['start_date'], "%Y-%m-%dT%H:%M:%S")
        deadline = start_date + timedelta(days=120)
        minister_data = {
            "dept_code": dept_code,
            "title_en": ministry['en'],
            "title_fr": ministry['fr'],
            "name": minister.get('name', ''),
            "name_en": minister.get('name_en', ''),
            "name_fr": minister.get('name_fr', ''),
            "start_date": minister.get('start_date', ''),
            "end_date": minister.get('end_date', ''),
            "witness_id": minister.get('witness_id', ''),
            "deadline": deadline.strftime("%Y-%m-%dT%H:%M:%S")
        }
        csv_data.append(minister_data)

# Convert the data to a DataFrame
df = pd.DataFrame(csv_data)

# Save the DataFrame to a CSV file
csv_output_path = 'minister_transition_binder_deadline.csv'
df.to_csv(csv_output_path, index=False)
