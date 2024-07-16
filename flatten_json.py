import pandas as pd
import json
import sys

if len(sys.argv) < 3:
    print("Usage: python flatten_json.py <input_json_file> <output_csv_file>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

# Load JSON data
with open(input_file, 'r') as f:
    data = json.load(f)

# Flatten the JSON data
flattened_data = []
for key, value in data.items():
    for minister in value['ministers']:
        flattened_data.append({
            'department_code': key,
            'department_name_en': value['en'],
            'department_name_fr': value['fr'],
            'minister_name': minister['name'],
            'minister_name_en': minister['name_en'],
            'minister_name_fr': minister['name_fr'],
            'start_date': minister['start_date'],
            'end_date': minister['end_date']
        })

# Create a DataFrame and convert to CSV
df = pd.DataFrame(flattened_data)
df.to_csv(output_file, index=False)
