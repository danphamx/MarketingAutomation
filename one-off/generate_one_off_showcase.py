import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote, unquote
import time
from typing import List, Dict, Optional
import csv
from datetime import datetime
import subprocess
from pathlib import Path

# Constants
REQUESTS_TIMEOUT = 10  # seconds
RATE_LIMIT_DELAY = 1  # seconds
MAX_RETRIES = 3
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted and points to thangs.com or than.gs
    
    Args:
        url: The URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc]) and (
            'thangs.com' in parsed.netloc or 
            'than.gs' in parsed.netloc
        )
    except Exception:
        return False

def check_github_status() -> None:
    """Check if there are uncommitted changes that need to be pushed"""
    try:
        # Check if we're in a git repository
        subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], 
                     check=True, capture_output=True)
        
        # Check for uncommitted changes
        result = subprocess.run(['git', 'status', '--porcelain'],
                              check=True, capture_output=True, text=True)
        
        if result.stdout.strip():
            print("\n⚠️  WARNING: You have uncommitted changes in your repository!")
            print("Please commit and push your changes before proceeding.")
            print("This ensures your images will be available when generating the showcase.\n")
            
            response = input("Do you want to proceed anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)
            print()
    except subprocess.CalledProcessError:
        print("\n⚠️  Note: This directory is not a git repository.")
        print("If you plan to host images on GitHub, please initialize a repository first.\n")
        
        response = input("Do you want to proceed anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
        print()

def make_request(url: str, headers: Dict[str, str], retry_count: int = 0) -> Optional[requests.Response]:
    """
    Make an HTTP request with retry logic and proper error handling
    
    Args:
        url: The URL to request
        headers: Request headers
        retry_count: Current retry attempt number
        
    Returns:
        Optional[requests.Response]: Response object if successful, None otherwise
    """
    try:
        response = requests.get(url, headers=headers, timeout=REQUESTS_TIMEOUT)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        if retry_count < MAX_RETRIES:
            print(f"⚠️  Retrying {url} (attempt {retry_count + 1}/{MAX_RETRIES})")
            time.sleep(RATE_LIMIT_DELAY * (retry_count + 1))
            return make_request(url, headers, retry_count + 1)
        print(f"❌ Error requesting {url}: {e}")
        return None

def fetch_one_off_links() -> List[Dict[str, str]]:
    """
    Fetch and extract links from designer pages listed in links.txt
    
    Returns:
        List[Dict[str, str]]: List of dictionaries containing URL and text for each model
    """
    print("🔍 Fetching links from designer pages...")
    
    # Read and validate source URLs
    try:
        links_file = Path('links.txt')
        if not links_file.exists():
            raise FileNotFoundError("links.txt not found!")
            
        source_urls = [line.strip() for line in links_file.read_text().splitlines() if line.strip()]
        source_urls = [url for url in source_urls if validate_url(url)]
        
        if not source_urls:
            raise ValueError("No valid URLs found in links.txt")
    except Exception as e:
        print(f"❌ Error reading links.txt: {e}")
        sys.exit(1)

    headers = {'User-Agent': USER_AGENT}
    all_model_links = []
    
    for source_url in source_urls:
        print(f"Processing: {source_url}")
        response = make_request(source_url, headers)
        if not response:
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        page_links = []
        
        for a_tag in soup.find_all('a', href=True):
            link = {
                'url': a_tag['href'],
                'text': a_tag.get_text(strip=True)
            }
            
            # Clean up and validate the URL
            if not link['url'].startswith('http'):
                if link['url'].startswith('//'):
                    link['url'] = 'https:' + link['url']
                elif link['url'].startswith('/'):
                    link['url'] = 'https://thangs.com' + link['url']
            
            if not validate_url(link['url']):
                continue
                
            # Only include links that contain '/3d-model/'
            if '/3d-model/' in link['url']:
                page_links.append(link)
                
            # Take only first 3 model links from this page
            if len(page_links) >= 3:
                break
        
        all_model_links.extend(page_links)
        print(f"✅ Found {len(page_links)} model links from {source_url}")
        
        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)
    
    print(f"\n✅ Found total of {len(all_model_links)} model links")
    
    # Save results to files
    date_str = datetime.now().strftime('%Y%m%d')
    save_links_to_files(all_model_links, date_str)
    
    return all_model_links

def save_links_to_files(links: List[Dict[str, str]], date_str: str) -> None:
    """
    Save links to CSV and text files
    
    Args:
        links: List of dictionaries containing URL and text for each model
        date_str: Date string for file naming
    """
    csv_filename = f'thangs_one_off_links_{date_str}.csv'
    
    # Save to CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["URL", "Link Text"])
        for link in links:
            writer.writerow([link['url'], link['text']])
    
    # Save to text file
    with open('model_links.txt', 'w', encoding='utf-8') as f:
        for link in links:
            f.write(f"{link['url']}\n")

def create_img_folder():
    """Create dated img folder if it doesn't exist"""
    date_str = datetime.now().strftime('%Y%m%d')
    folder_path = os.path.join('img', date_str)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def get_model_name_from_url(url):
    """Extract model name from URL for filename"""
    path = urlparse(url).path
    model_name = path.split('/')[-1].split('-')[0]
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
        print(f"❌ Error downloading {image_url}: {e}")
        return False

def process_model_page(url):
    """Visit model page and extract thumbnail image"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        img_element = soup.select_one('meta[property="og:image"]')
        if img_element and img_element.get('content'):
            return img_element.get('content')
            
        img_element = soup.select_one('img[alt*="model"]')
        if img_element and img_element.get('src'):
            return img_element.get('src')
            
        return None
    except Exception as e:
        print(f"❌ Error processing {url}: {e}")
        return None

def download_thumbnails():
    """Download thumbnails for all models"""
    print("\n📥 Downloading model thumbnails...")
    
    img_folder = create_img_folder()
    date_str = datetime.now().strftime('%Y%m%d')
    csv_filename = f'image_links_one_off_{date_str}.csv'
    
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Image Path', 'Original Link'])
    
    with open('model_links.txt', 'r') as f:
        links = [line.strip() for line in f if line.strip()]
    
    for i, url in enumerate(links, 1):
        print(f"Processing {i}/{len(links)}: {url}")
        
        model_name = get_model_name_from_url(url)
        thumbnail_url = process_model_page(url)
        
        if thumbnail_url:
            file_extension = os.path.splitext(urlparse(thumbnail_url).path)[1] or '.jpg'
            filename = os.path.join(img_folder, f"{model_name}{file_extension}")
            
            if download_image(thumbnail_url, filename):
                print(f"✅ Downloaded: {filename}")
                with open(csv_filename, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([filename, url])
            else:
                print(f"❌ Failed to download: {filename}")
        else:
            print(f"⚠️  No thumbnail found for: {url}")
        
        time.sleep(1)
    
    print(f"\n✅ Downloads completed!")
    print(f"📁 Images saved in: {img_folder}")
    print(f"📄 CSV file created: {csv_filename}")
    return img_folder

def get_github_raw_url(image_path):
    """Convert local image path to GitHub raw URL"""
    image_path = image_path.replace('img/', '')
    directory = datetime.now().strftime('%Y%m%d')
    filename = os.path.basename(image_path)
    
    try:
        # First decode the filename in case it's already URL-encoded
        filename = unquote(filename)
        # Double encode the filename - this is what GitHub expects
        encoded_filename = quote(quote(filename, safe=''), safe='')
    except:
        # Fallback to simple encoding if there's an error
        encoded_filename = quote(filename, safe='')
    
    return f"https://raw.githubusercontent.com/danphamx/MarketingAutomation/refs/heads/main/one-off/img/{directory}/{encoded_filename}"

def generate_showcase_html():
    """Generate HTML showcase of downloaded models"""
    print("\n🎨 Generating HTML showcase...")
    
    csv_files = [f for f in os.listdir('.') if f.startswith('image_links_') and f.endswith('.csv')]
    if not csv_files:
        print("❌ No image_links CSV file found!")
        return
    
    csv_file = sorted(csv_files)[-1]
    image_data = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            image_data.append({
                'image_path': row['Image Path'],
                'original_link': row['Original Link']
            })

    html_content = """
<!DOCTYPE html>
<html>
<head>
</head>
<body>
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="min-width: 100%;">
    <tr>
        <td align="center" style="padding: 20px 0;">
            <span style="font-size:19px">What to Print This Weekend</span><br />
            Explore the latest 3D Printing Trends!<br />
            &nbsp;
        </td>
    </tr>
    <tr>
        <td align="center" style="padding-bottom: 20px;">
            Designs on Thangs<br />
            <span style="font-size:18px">
                <a href="https://thangs.com" target="_blank" style="color:#0000FF">
                    Search from over 30M 3D Models
                </a>
            </span>
        </td>
    </tr>
</table>
"""

    # Add model images in groups of three
    for i in range(0, len(image_data), 3):
        html_content += """
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="min-width: 100%;">
    <tr>
        <td align="center">
            <table cellpadding="10" cellspacing="0" border="0">
                <tr>"""
        
        # Process up to three images per row
        for j in range(3):
            if i + j < len(image_data):
                img = image_data[i + j]
                # Use get_github_raw_url to properly encode the image URL
                github_img_url = get_github_raw_url(img['image_path'])
                
                html_content += f"""
                    <td style="vertical-align: top;">
                        <a href="{img['original_link']}" target="_blank" style="text-decoration: none;">
                            <img src="{github_img_url}" alt="3D Model Preview" width="300" height="400" style="display: block; width: 300px; height: 400px; object-fit: cover; object-position: center;" />
                        </a>
                    </td>"""
            else:
                # Add empty cell to maintain structure
                html_content += """
                    <td width="300" style="vertical-align: top;">&nbsp;</td>"""
        
        html_content += """
                </tr>
            </table>
        </td>
    </tr>
</table>"""

    # Add footer with link to marketplace
    html_content += """
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="min-width: 100%;">
    <tr>
        <td align="center" style="padding: 20px 0;">
            <a href="https://thangs.com/marketplace/memberships/trending" target="_blank" style="font-size:18px; text-decoration: none;">
                Check out the Marketplace!
            </a>
        </td>
    </tr>
</table>
</body>
</html>
"""

    date_str = datetime.now().strftime('%Y%m%d')
    output_filename = f'html_blob_one_off_{date_str}.html'
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Generated HTML showcase: {output_filename}")

def main():
    print("🚀 Starting One Off Designs Generator\n")
    
    # Run each step in sequence
    fetch_one_off_links()
    download_thumbnails()
    generate_showcase_html()
    
    print("\n✨ Process completed successfully!")

if __name__ == "__main__":
    main() 