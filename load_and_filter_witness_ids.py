import pandas as pd
import requests
from datetime import datetime, timedelta

# Additional witness IDs to be added
additional_witness_ids = [
    299994, 299995, 299996, 299997, 299998, 299999, 300000, 300001, 300002, 300003, 
    300004, 300005, 300006, 300007, 300008, 300009, 300010, 300011, 300012, 300013, 
    300014, 300015, 300016, 300017, 300018, 300019, 300020, 300021, 300022, 300023, 
    300024, 300025, 300026, 300027, 300028, 300029, 300030, 300031, 300032, 300033, 
    300034, 300035, 300036, 300037
]

def load_and_filter_witness_ids():
    url = 'http://web.archive.org/cdx/search/cdx?url=ourcommons.ca/committees/en/WitnessMeetings?witness&matchType=prefix&limit=100000&collapse=urlkey'
    response = requests.get(url)
    data = response.text.splitlines()
    witness_ids = set(additional_witness_ids)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    for line in data:
        parts = line.split(' ')
        if len(parts) > 3:
            timestamp = parts[1]
            witness_url = parts[2]
            if 'witnessId=' in witness_url:
                witness_id = int(witness_url.split('witnessId=')[1])
                timestamp_date = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
                if timestamp_date > thirty_days_ago:
                    witness_ids.add(witness_id)
    
    witness_ids_sorted = sorted(witness_ids, reverse=True)
    pd.DataFrame(witness_ids_sorted, columns=['Witness ID']).to_csv('sorted_witness_ids.csv', index=False)

if __name__ == "__main__":
    load_and_filter_witness_ids()
    print("CSV file saved to sorted_witness_ids.csv")
