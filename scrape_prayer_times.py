#!/usr/bin/env python3
"""
Script to scrape prayer times for Oxford from najaf.org and save to JSON.
Run this script monthly to update prayer times.
"""
import requests
from html.parser import HTMLParser
import json
from datetime import datetime

class PrayerTimesParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.current_row = []
        self.all_rows = []
        
    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
        elif tag == 'tr' and self.in_table:
            self.in_row = True
            self.current_row = []
        elif tag == 'td' and self.in_row:
            self.in_cell = True
            
    def handle_endtag(self, tag):
        if tag == 'table':
            self.in_table = False
        elif tag == 'tr':
            if self.in_row and len(self.current_row) >= 8:
                self.all_rows.append(self.current_row)
            self.in_row = False
        elif tag == 'td':
            self.in_cell = False
            
    def handle_data(self, data):
        if self.in_cell:
            self.current_row.append(data.strip())

def scrape_prayer_times():
    """Scrape all prayer times for Oxford and save to JSON file"""
    
    url = 'https://najaf.org/english/prayer/oxford'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    print(f"Fetching prayer times from: {url}")
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    html = response.text
    print(f"Successfully fetched HTML (length: {len(html)})")
    
    # Parse the HTML
    parser = PrayerTimesParser()
    parser.feed(html)
    print(f"Found {len(parser.all_rows)} rows in prayer times table")
    
    # Convert to dictionary with day as key
    prayer_times_dict = {}
    
    for row in parser.all_rows:
        if len(row) >= 8:
            try:
                day = int(row[7])
                prayer_times_dict[day] = {
                    'day': day,
                    'midnight': row[0],
                    'maghrib': row[1],
                    'sunset': row[2],
                    'dhuhr': row[3],
                    'sunrise': row[4],
                    'fajr': row[5],
                    'imsaak': row[6]
                }
            except (ValueError, IndexError) as e:
                print(f"Error parsing row: {e}")
                continue
    
    # Get current month and year for metadata
    now = datetime.now()
    
    # Create final data structure
    data = {
        'month': now.strftime('%B'),
        'year': now.year,
        'last_updated': now.isoformat(),
        'prayer_times': prayer_times_dict
    }
    
    # Save to JSON file
    output_file = 'prayer_times_oxford.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Successfully saved {len(prayer_times_dict)} days of prayer times to {output_file}")
    print(f"📅 Data for: {data['month']} {data['year']}")
    print(f"🕐 Last updated: {data['last_updated']}")
    
    return data

if __name__ == '__main__':
    try:
        scrape_prayer_times()
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
