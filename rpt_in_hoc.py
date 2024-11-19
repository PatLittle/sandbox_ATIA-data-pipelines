

import xml.etree.ElementTree as ET
import pandas as pd
import requests
import feedparser
from bs4 import BeautifulSoup

def parse_rss_to_df(rss_url):
    # Parse RSS feed
    feed = feedparser.parse(rss_url)

    # Prepare data for DataFrame
    data = []

    # Extract information from feed entries
    for entry in feed.entries:
        publication_id = entry.get('guid', None)
        pub_date = entry.get('published', None)
        description = entry.get('description', None)

        # Append row data to list
        data.append([
            publication_id, pub_date, description
        ])

    # Create DataFrame
    df = pd.DataFrame(data, columns=[
        'guid', 'pubDate', 'description'
    ])

    return df

# RSS feed URL
rss_url = "https://www.ourcommons.ca/PublicationSearch/en/?View=D&oob=ReturnsandReportsDepositedwiththeClerkoftheHouse,ReturnsandReportsDepositedwiththeActingClerkoftheHouse&Topic=&Proc=&Text=&RPP=15&order=&targetLang=&SBS=0&MRR=2000000&PubType=203&rss=1"

# Parse RSS and create DataFrame
persisted_df = parse_rss_to_df(rss_url)

# Create a copy of the DataFrame to avoid modifying the original
transformed_df = persisted_df.copy()

# Extract only the second <div> from the 'description' column
transformed_df['description'] = transformed_df['description'].apply(lambda x: str(BeautifulSoup(x, 'html.parser').find_all('div')[1]) if x and len(BeautifulSoup(x, 'html.parser').find_all('div')) > 1 else None)

# Create a copy of the DataFrame to avoid modifying the original
updated_df = transformed_df.copy()

# Strip HTML tags from the 'description' column
updated_df['description'] = updated_df['description'].apply(lambda x: BeautifulSoup(x, 'html.parser').get_text() if x else None)

# Split the 'description' column by em dash as a delimiter without limiting the number of columns
split_columns = updated_df['description'].str.split('— ', expand=True)

# Add the split columns back to the DataFrame
for i in range(split_columns.shape[1]):
    updated_df[f'description_part_{i+1}'] = split_columns[i]

# Drop the original 'description' column
updated_df.drop(columns=['description'], inplace=True)

# Rename 'description_part_1' to 'mp_profile_url'
updated_df.rename(columns={'description_part_1': 'mp_profile_url'}, inplace=True)

# Filter rows where 'description_part_2' starts with 'by Mr.' or 'by Ms.'
filtered_df = updated_df[updated_df['description_part_2'].str.startswith(('by Mr.', 'by Ms.'), na=False)]

# Remove 'by ' prefix from 'description_part_2'
filtered_df['description_part_2'] = filtered_df['description_part_2'].str.replace(r'^by\s+', '', regex=True)

# Split 'description_part_2' into two parts: name and title within round brackets
split_min_title = filtered_df['description_part_2'].str.split(' \(', expand=True)

# Update filtered_df with split values
filtered_df['description_part_2'] = split_min_title[0]
filtered_df['min_title'] = split_min_title[1]

# Rename 'description_part_2' to 'mp_short_nm'
filtered_df.rename(columns={'description_part_2': 'mp_short_nm'}, inplace=True)

# Split 'description_part_3' to extract action information
split_act = filtered_df['description_part_3'].str.split(', pursuant to', expand=True)

# Sort filtered_df by 'pubDate' in descending order
filtered_df = filtered_df.sort_values(by='pubDate', ascending=False)

# Add deadline column (30 days after 'pubDate')
filtered_df['pubDate'] = pd.to_datetime(filtered_df['pubDate'])
filtered_df['deadline'] = filtered_df['pubDate'] + pd.Timedelta(days=30)

# Merge all 'description_part_' columns into one
merged_df = filtered_df.copy()
merged_df['merged_description'] = merged_df.filter(regex='^description_part_').apply(lambda x: ' — '.join(x.dropna()), axis=1)

# Drop all 'description_part_' columns
merged_df.drop(columns=merged_df.filter(regex='^description_part_').columns, inplace=True)

merged_df = merged_df[merged_df['merged_description'].str.contains('Act', na=False)]
# Write the merged DataFrame to a CSV file
merged_df.to_csv('merged_output.csv', index=False)

# Display the DataFrame with the merged column
print(merged_df)
