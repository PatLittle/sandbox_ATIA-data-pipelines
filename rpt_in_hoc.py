import pandas as pd
import re
from bs4 import BeautifulSoup
import feedparser

# Load RSS feed and parse entries
rss_url = "https://www.ourcommons.ca/PublicationSearch/en/?View=D&oob=ReturnsandReportsDepositedwiththeClerkoftheHouse,ReturnsandReportsDepositedwiththeActingClerkoftheHouse&Topic=&Proc=&Text=&RPP=15&order=&targetLang=&SBS=0&MRR=2000000&PubType=203&rss=1"
feed = feedparser.parse(rss_url)

# Prepare data for DataFrame
data = []
for entry in feed.entries:
    publication_id = entry.get('guid', None)
    pub_date = entry.get('published', None)
    description = entry.get('description', None)
    if description:
        soup = BeautifulSoup(description, 'html.parser')
        text_content = soup.get_text(separator=" ")
        summary_parts = re.split(r'\s*[–—-]\s*', text_content)
        while len(summary_parts) < 5:
            summary_parts.append(None)
        data.append([publication_id, pub_date] + summary_parts[:5])

# Create DataFrame
df = pd.DataFrame(data, columns=[
    'guid', 'pubDate', 'description_part_1', 'description_part_2', 'description_part_3', 'description_part_4', 'description_part_5'
])

# Filter rows where 'description_part_2' starts with 'by Mr.' or 'by Ms.'
filtered_df = df[df['description_part_2'].str.startswith(('by Mr.', 'by Ms.'), na=False)]

# Remove 'by ' from the start of 'description_part_2'
filtered_df['description_part_2'] = filtered_df['description_part_2'].str.replace(r'^by\s+', '', regex=True)

# Split 'description_part_2' into two parts: name and title within round brackets
split_min_title = filtered_df['description_part_2'].str.extract(r'^(.*?)\s*\((.*?)\)$')
filtered_df['description_part_2'] = split_min_title[0]
filtered_df['min_title'] = split_min_title[1]

# Add a column called 'deadline' with the date 30 days past 'pubDate'
filtered_df['pubDate'] = pd.to_datetime(filtered_df['pubDate'])
filtered_df['deadline'] = filtered_df['pubDate'] + pd.Timedelta(days=30)

# Merge all 'description_part_' columns into one
merged_df = filtered_df.copy()
merged_df['merged_description'] = merged_df.filter(regex='^description_part_').apply(lambda x: ' — '.join(x.dropna()), axis=1)

# Drop all 'description_part_' columns
merged_df.drop(columns=merged_df.filter(regex='^description_part_').columns, inplace=True)

# Write the merged DataFrame to a CSV file
merged_df.to_csv('merged_output.csv', index=False)

# The script is designed to run in a GitHub Actions environment without user interaction
