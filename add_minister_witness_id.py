import pandas as pd
import json

def main():
    # Load the data
    ministers_csv_path = 'output.csv'
    meetings_csv_path = 'full_witness_meetings_output.csv'
    json_path = 'minister.json'
    
    ministers_df = pd.read_csv(ministers_csv_path)
    meetings_df = pd.read_csv(meetings_csv_path)

    # Parse the dates
    ministers_df['start_date'] = pd.to_datetime(ministers_df['start_date'])
    ministers_df['end_date'] = pd.to_datetime(ministers_df['end_date']).fillna(pd.Timestamp('2100-01-01'))
    meetings_df['Date'] = pd.to_datetime(meetings_df['Date'])

    # Function to find the exact witness ID based on the minister's name and tenure
    def find_exact_witness_id_adjusted(minister):
        exact_meetings = meetings_df[
            (meetings_df['Date'] >= minister['start_date']) & 
            (meetings_df['Date'] <= minister['end_date']) &
            (meetings_df['Witness Name'].str.contains(minister['minister_name'], case=False))
        ]
        if not exact_meetings.empty:
            return exact_meetings.iloc[0]['Witness ID']
        return None

    # Apply the function to each minister's record and create a new column for the exact witness ID
    ministers_df['witness_id'] = ministers_df.apply(find_exact_witness_id_adjusted, axis=1)

    # Save the updated ministers DataFrame to the same CSV file
    ministers_df.to_csv(ministers_csv_path, index=False)

    # Load the JSON file
    with open(json_path) as f:
        ministers_json = json.load(f)

    # Create a dictionary from the ministers DataFrame for easier lookup
    witness_id_dict = ministers_df.set_index(['minister_name'])['witness_id'].to_dict()

    # Function to add witness_id to each minister in the JSON structure
    def add_witness_id_to_ministers(ministers_list):
        for minister in ministers_list:
            minister_name = minister['name']
            witness_id = witness_id_dict.get(minister_name)
            if pd.notna(witness_id):
                minister['witness_id'] = int(witness_id)  # Ensure witness_id is an integer if present

    # Add witness_id to each minister in the JSON data
    for department in ministers_json.values():
        add_witness_id_to_ministers(department['ministers'])
 
 # Save the updated JSON to the same file with UTF-8 encoding
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(ministers_json, f, indent=4, ensure_ascii=False)

    print(f'Updated CSV file saved to {ministers_csv_path}')
    print(f'Updated JSON file saved to {json_path}')

if __name__ == "__main__":
    main()
