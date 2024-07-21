import requests
import xml.etree.ElementTree as ET
import json
import pandas as pd

def fetch_ministers_xml(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def parse_ministers_xml(xml_content):
    root = ET.fromstring(xml_content)
    ministries = {}

    for ministry in root.findall('.//Ministry'):
        dept_code = ministry.find('ShortTitle').text.strip()
        dept_name_en = ministry.find('Title').text.strip()
        dept_name_fr = ministry.find('TitleFR').text.strip()

        ministers = []
        for minister in ministry.findall('Minister'):
            name = minister.find('PersonOfficialFirstName').text.strip() + ' ' + minister.find('PersonOfficialLastName').text.strip()
            name_en = minister.find('DisplayName').text.strip()
            name_fr = minister.find('DisplayNameFR').text.strip()
            start_date = minister.find('DateOfAppointment').text.strip()
            end_date = minister.find('DateOfResignation').text.strip() if minister.find('DateOfResignation') is not None else ""

            ministers.append({
                "name": name,
                "name_en": name_en,
                "name_fr": name_fr,
                "start_date": start_date,
                "end_date": end_date
            })

        ministries[dept_code] = {
            "en": dept_name_en,
            "fr": dept_name_fr,
            "ministers": ministers
        }

    return ministries

def update_ministers_json(existing_json_path, new_ministries):
    # Load existing JSON
    with open(existing_json_path, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)

    # Update existing data with new data, preserving witness_ids
    for dept_code, ministry in new_ministries.items():
        if dept_code in existing_data:
            existing_ministers = {minister['name']: minister for minister in existing_data[dept_code]['ministers']}
            for new_minister in ministry['ministers']:
                if new_minister['name'] in existing_ministers:
                    new_minister['witness_id'] = existing_ministers[new_minister['name']].get('witness_id')
        existing_data[dept_code] = ministry

    # Save the updated JSON
    with open(existing_json_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

def main():
    xml_url = 'https://www.ourcommons.ca/Members/en/ministries/xml'
    json_path = 'minister.json'

    # Fetch and parse the XML data
    xml_content = fetch_ministers_xml(xml_url)
    new_ministries = parse_ministers_xml(xml_content)

    # Update the existing JSON with the new data
    update_ministers_json(json_path, new_ministries)

    print(f'Minister JSON file at {json_path} has been updated.')

if __name__ == "__main__":
    main()
