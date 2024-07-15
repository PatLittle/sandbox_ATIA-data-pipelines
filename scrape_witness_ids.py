import pandas as pd
import requests
import csv
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import multiprocessing

def fetch_data(witness_id, index):
    url = f"https://www.ourcommons.ca/committees/en/WitnessMeetings?witnessId={witness_id}"
    response = requests.get(url)
    if index % 50 == 0:
        print(f"Request {index}: HTTP status {response.status_code} for witness ID {witness_id}")
    if response.status_code != 200:
        print(f"Failed to fetch data for witness ID {witness_id}")
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    if index % 50 == 0:
        print(f"Content fetched for witness ID {witness_id}:")
        print(soup.prettify()[:1000])
    witness_details = soup.select_one('div.witness-details')
    if not witness_details:
        print(f"No witness details found for witness ID {witness_id}")
        return []
    name_elem = witness_details.select_one('div.witness-details-name')
    title_elem = witness_details.select_one('div.witness-details-title')
    org_elem = witness_details.select_one('div.witness-details-organization')
    name = name_elem.text.strip() if name_elem else "N/A"
    title = title_elem.text.strip() if title_elem else "N/A"
    organization = org_elem.text.strip() if org_elem else "N/A"
    meetings = []
    for grouping in soup.select('div.grouping-header'):
        date = grouping.text.strip()
        for meeting_item in grouping.find_next_siblings('div', class_='accordion-item'):
            meeting_name_elem = meeting_item.select_one('div.meeting-title-main')
            if not meeting_name_elem:
                continue
            meeting_name = meeting_name_elem.text.strip()
            acronym_elem = meeting_name_elem.select_one('span.meeting-acronym')
            acronym = acronym_elem.text.strip() if acronym_elem else ''
            time_elem = meeting_item.select_one('div.the-time')
            time = time_elem.text.strip() if time_elem else "N/A"
            button_list = meeting_item.select_one('div.button-list.meeting-card-buttons')
            if not button_list:
                continue
            notice_link_elem = button_list.select_one('a.btn-meeting-notice')
            evidence_link_elem = button_list.select_one('a.btn-meeting-evidence')
            minutes_link_elem = button_list.select_one('a.btn-meeting-minutes')
            notice_link = notice_link_elem['href'] if notice_link_elem else "N/A"
            evidence_link = evidence_link_elem['href'] if evidence_link_elem else "N/A"
            minutes_link = minutes_link_elem['href'] if minutes_link_elem else "N/A"
            meeting_data = {
                'Witness ID': witness_id,
                'Witness Name': name,
                'Title': title,
                'Organization': organization,
                'Meeting Name': meeting_name,
                'Date': date,
                'Time': time,
                'Acronym': acronym,
                'Notice Link': f"https://www.ourcommons.ca{notice_link}" if notice_link != "N/A" else "N/A",
                'Evidence Link': f"https://www.ourcommons.ca{evidence_link}" if evidence_link != "N/A" else "N/A",
                'Minutes Link': f"https://www.ourcommons.ca{minutes_link}" if minutes_link != "N/A" else "N/A"
            }
            if index % 50 == 0:
                print(f"Scraped data: {meeting_data}")
            meetings.append(meeting_data)
    return meetings

def main():
    sorted_witness_ids_df = pd.read_csv('sorted_witness_ids.csv')
    sorted_witness_ids = sorted_witness_ids_df['Witness ID'].tolist()
    fieldnames = ['Witness ID', 'Witness Name', 'Title', 'Organization', 'Meeting Name', 'Date', 'Time', 'Acronym', 'Notice Link', 'Evidence Link', 'Minutes Link']
    try:
        with open('full_witness_meetings_output.csv', mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            num_workers = min(32, (multiprocessing.cpu_count() or 1) * 4)
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = {executor.submit(fetch_data, wid, idx): wid for idx, wid in enumerate(sorted_witness_ids)}
                for future in tqdm(as_completed(futures), total=len(futures)):
                    result = future.result()
                    wid = futures[future]
                    if result:
                        writer.writerows(result)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
