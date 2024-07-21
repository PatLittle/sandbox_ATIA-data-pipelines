import requests
import xml.etree.ElementTree as ET
import json

# Step 1: Fetch the XML Data from both English and French sources
xml_url_en = 'https://www.ourcommons.ca/Members/en/ministries/xml'
xml_url_fr = 'https://www.ourcommons.ca/Members/fr/ministries/xml'
response_en = requests.get(xml_url_en)
response_en.raise_for_status()
xml_content_en = response_en.content

response_fr = requests.get(xml_url_fr)
response_fr.raise_for_status()
xml_content_fr = response_fr.content

# Step 2: Parse the XML Data
root_en = ET.fromstring(xml_content_en)
root_fr = ET.fromstring(xml_content_fr)

new_ministers = []

for minister_en, minister_fr in zip(root_en.findall('.//Minister'), root_fr.findall('.//Minister')):
    honorific_en = minister_en.find('PersonShortHonorific').text.strip() if minister_en.find('PersonShortHonorific') is not None else ""
    honorific_fr = minister_fr.find('PersonShortHonorific').text.strip() if minister_fr.find('PersonShortHonorific') is not None else ""
    first_name_en = minister_en.find('PersonOfficialFirstName').text.strip()
    last_name_en = minister_en.find('PersonOfficialLastName').text.strip()
    title_en = minister_en.find('Title').text.strip()
    first_name_fr = minister_fr.find('PersonOfficialFirstName').text.strip()
    last_name_fr = minister_fr.find('PersonOfficialLastName').text.strip()
    title_fr = minister_fr.find('Title').text.strip()
    start_date = minister_en.find('FromDateTime').text.strip()
    
    # Handle ToDateTime properly
    to_date_elem = minister_en.find('ToDateTime')
    end_date = to_date_elem.text.strip() if to_date_elem is not None and to_date_elem.text is not None else ""

    name = f"{first_name_en} {last_name_en}"
    name_en = f"{last_name_en}, {first_name_en} ({honorific_en})"
    name_fr = f"{last_name_fr}, {first_name_fr} ({honorific_fr})"

    print(f"Parsing Minister: {honorific_en} {first_name_en} {last_name_en}, Title: {title_en}, Start: {start_date}, End: {end_date}")

    new_ministers.append({
        "name": name,
        "name_en": name_en,
        "name_fr": name_fr,
        "title_en": title_en,
        "title_fr": title_fr,
        "start_date": start_date,
        "end_date": end_date
    })

# Step 3: Load the existing JSON file
existing_json_path = 'minister.json'
with open(existing_json_path, 'r', encoding='utf-8') as f:
    existing_data = json.load(f)

# Step 4: Add new ministers from XML to the existing JSON, preserving witness_ids
for new_minister in new_ministers:
    found = False
    for dept_code, ministry in existing_data.items():
        if ministry['en'] == new_minister['title_en'] and ministry['fr'] == new_minister['title_fr']:
            for minister in ministry['ministers']:
                if new_minister['name'] == minister['name']:
                    found = True
                    break
            if not found:
                # Check if the new minister should have a witness_id preserved
                if 'witness_id' in new_minister:
                    existing_witness_id = new_minister['witness_id']
                else:
                    existing_witness_id = None
                # Append new minister to the ministry
                ministry['ministers'].append(new_minister)
                # Preserve witness_id if exists
                if existing_witness_id is not None:
                    ministry['ministers'][-1]['witness_id'] = existing_witness_id
                print(f"  Added new Minister to {dept_code}: {new_minister['name']}")
            break

# Step 5: Save the updated JSON file
with open(existing_json_path, 'w', encoding='utf-8') as f:
    json.dump(existing_data, f, indent=4, ensure_ascii=False)

print(f"Updated minister.json file has been saved to {existing_json_path}")
