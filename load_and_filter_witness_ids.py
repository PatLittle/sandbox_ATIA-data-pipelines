import pandas as pd
import requests
from datetime import datetime, timedelta

def load_and_filter_witness_ids():
    url = 'http://web.archive.org/cdx/search/cdx?url=ourcommons.ca/committees/en/WitnessMeetings?witness&matchType=prefix&limit=100000&collapse=urlkey'
    response = requests.get(url)
    data = response.text.splitlines()
    witness_ids = []
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    for line in data:
        parts = line.split(' ')
        if len(parts) > 3:
            timestamp = parts[1]
            witness_url = parts[2]
            if 'witnessId=' in witness_url:
                witness_id = witness_url.split('witnessId=')[1]
                timestamp_date = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
                if timestamp_date > thirty_days_ago:
                    witness_ids.append(witness_id)
    
    witness_ids = list(set(witness_ids))
    witness_ids_df = pd.DataFrame(witness_ids, columns=['Witness ID'])
    witness_ids_df = witness_ids_df.sort_values(by='Witness ID', ascending=False)
    witness_ids_df.to_csv('sorted_witness_ids.csv', index=False)

if __name__ == "__main__":
    load_and_filter_witness_ids()
