import requests
from bs4 import BeautifulSoup
import re
import csv
from datetime import datetime
import os

def fetch_thangs_leaderboard_links():
    """
    Fetch and extract links from Thangs leaderboard page
    """
    url = "https://thangs.com/leaderboard/makes?inTheRunning=popular&range=period"
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Make the HTTP request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links
        links = []
        for a_tag in soup.find_all('a', href=True):
            link = {
                'url': a_tag['href'],
                'text': a_tag.get_text(strip=True)
            }
            
            # Clean up the URL
            if not link['url'].startswith('http'):
                if link['url'].startswith('//'):
                    link['url'] = 'https:' + link['url']
                elif link['url'].startswith('/'):
                    link['url'] = 'https://thangs.com' + link['url']
            
            # Only include links that contain '/3d-model/'
            if '/3d-model/' in link['url']:
                links.append(link)
        
        print(f"Found {len(links)} model links on the page")
        
        # Create dated CSV file
        date_str = datetime.now().strftime('%Y%m%d')
        csv_filename = f'thangs_links_{date_str}.csv'
        
        # Save to CSV
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["URL", "Link Text"])
            for link in links:
                writer.writerow([link['url'], link['text']])
        
        # Save URLs to links.txt
        with open('links.txt', 'w', encoding='utf-8') as f:
            for link in links:
                f.write(f"{link['url']}\n")
        
        return links
        
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def test_link_extraction():
    """
    Test the link extraction and print results
    """
    links = fetch_thangs_leaderboard_links()
    if links:
        print(f"\nSuccessfully extracted {len(links)} links")
        print("\nFirst 5 links for verification:")
        for i, link in enumerate(links[:5], 1):
            print(f"\nLink {i}:")
            print(f"Text: {link['text']}")
            print(f"URL:  {link['url']}")
    else:
        print("Failed to extract links")

if __name__ == "__main__":
    test_link_extraction() 