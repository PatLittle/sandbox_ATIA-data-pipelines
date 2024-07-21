import requests
import xml.etree.ElementTree as ET
import json

# Step 1: Fetch the XML Data
xml_url = 'https://www.ourcommons.ca/Members/en/ministries/xml'
response = requests.get(xml_url)
response.raise_for_status()
xml_content = response.content

# Step 2: Parse the XML Data
root = ET.fromstring(xml_content)
new_ministers = []

for minister in root.findall('.//Minister'):
    honorific = minister.find('PersonShortHonorific').text.strip() if minister.find('PersonShortHonorific') is not None else ""
    first_name = minister.find('PersonOfficialFirstName').text.strip()
    last_name = minister.find('PersonOfficialLastName').text.strip()
    title = minister.find('Title').text.strip()
    start_date = minister.find('FromDateTime').text.strip()
    
    # Handle ToDateTime properly
    to_date_elem = minister.find('ToDateTime')
    end_date = to_date_elem.text.strip() if to_date_elem is not None and to_date_elem.text is not None else ""

    print(f"Parsing Minister: {honorific} {first_name} {last_name}, Title: {title}, Start: {start_date}, End: {end_date}")

    new_ministers.append({
        "honorific": honorific,
        "name": f"{first_name} {last_name}",
        "first_name": first_name,
        "last_name": last_name,
        "title": title,
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
        if ministry['en'] == new_minister['title']:
            for minister in ministry['ministers']:
                if new_minister['name'] == minister['name']:
                    found = True
                    break
            if not found:
                ministry['ministers'].append(new_minister)
                print(f"  Added new Minister to {dept_code}: {new_minister['name']}")
            break

# Step 5: Save the updated JSON file
with open(existing_json_path, 'w', encoding='utf-8') as f:
    json.dump(existing_data, f, indent=4, ensure_ascii=False)

print(f"Updated minister.json file has been saved to {existing_json_path}")
