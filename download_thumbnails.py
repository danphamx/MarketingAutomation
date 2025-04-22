import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import csv
from datetime import datetime

def create_img_folder():
    """Create dated img folder if it doesn't exist"""
    # Create folder with date format YYYYMMDD
    date_str = datetime.now().strftime('%Y%m%d')
    folder_path = os.path.join('img', date_str)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def get_model_name_from_url(url):
    """Extract model name from URL for filename"""
    path = urlparse(url).path
    model_name = path.split('/')[-1].split('-')[0]  # Get the last part of the path before the ID
    return model_name

def download_image(image_url, filename):
    """Download image from URL and save it locally"""
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {image_url}: {e}")
        return False

def process_model_page(url):
    """Visit model page and extract thumbnail image"""
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the main model image
        # This selector might need adjustment based on Thangs' HTML structure
        img_element = soup.select_one('meta[property="og:image"]')
        if img_element and img_element.get('content'):
            return img_element.get('content')
            
        # Fallback: try other image selectors if the above doesn't work
        img_element = soup.select_one('img[alt*="model"]')
        if img_element and img_element.get('src'):
            return img_element.get('src')
            
        return None
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

def main():
    # Create dated img folder
    img_folder = create_img_folder()
    date_str = datetime.now().strftime('%Y%m%d')
    
    # Create CSV file with date
    csv_filename = f'image_links_{date_str}.csv'
    
    # Initialize CSV with headers
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Image Path', 'Original Link'])
    
    # Read links from file
    with open('links.txt', 'r') as f:
        links = [line.strip() for line in f if line.strip()]
    
    for i, url in enumerate(links, 1):
        print(f"Processing {i}/{len(links)}: {url}")
        
        # Get model name for filename
        model_name = get_model_name_from_url(url)
        
        # Get thumbnail URL
        thumbnail_url = process_model_page(url)
        
        if thumbnail_url:
            # Create filename
            file_extension = os.path.splitext(urlparse(thumbnail_url).path)[1] or '.jpg'
            filename = os.path.join(img_folder, f"{model_name}{file_extension}")
            
            # Download image
            if download_image(thumbnail_url, filename):
                print(f"Successfully downloaded: {filename}")
                # Add to CSV
                with open(csv_filename, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([filename, url])
            else:
                print(f"Failed to download: {filename}")
        else:
            print(f"No thumbnail found for: {url}")
        
        # Add a small delay between requests to be nice to the server
        time.sleep(1)
    
    print(f"\nProcess completed!")
    print(f"Images saved in: {img_folder}")
    print(f"CSV file created: {csv_filename}")

if __name__ == "__main__":
    main() 