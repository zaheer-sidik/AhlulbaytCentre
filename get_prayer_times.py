#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
from html.parser import HTMLParser

class PrayerTimesParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.current_row = []
        self.all_rows = []
        self.cell_count = 0
        
    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
        elif tag == 'tr' and self.in_table:
            self.in_row = True
            self.current_row = []
            self.cell_count = 0
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
            self.cell_count += 1
            
    def handle_data(self, data):
        if self.in_cell:
            self.current_row.append(data.strip())

def fetch_prayer_times():
    try:
        # Get today's date
        today = datetime.now()
        day = today.day
        month = today.month
        
        # Fetch the Oxford prayer times page
        url = 'https://najaf.org/english/prayer/oxford'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
        
        # Parse the HTML
        parser = PrayerTimesParser()
        parser.feed(html)
        
        # Find today's prayer times
        prayer_data = None
        for row in parser.all_rows:
            if len(row) >= 8:
                try:
                    row_day = int(row[7])
                    if row_day == day:
                        prayer_data = {
                            'imsaak': row[6],
                            'fajr': row[5],
                            'sunrise': row[4],
                            'dhuhr': row[3],
                            'sunset': row[2],
                            'maghrib': row[1],
                            'midnight': row[0],
                            'date': today.strftime('%d %B %Y')
                        }
                        break
                except (ValueError, IndexError):
                    continue
        
        if prayer_data:
            return prayer_data
        else:
            return {'error': 'Prayer times not found for today'}
            
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    result = fetch_prayer_times()
    print('Content-Type: application/json')
    print()
    print(json.dumps(result, indent=2))
