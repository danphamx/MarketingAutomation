import os
import glob
from datetime import datetime
from bs4 import BeautifulSoup

def find_html_blobs():
    """Find all html_blob_*.html files in the parent and sibling directories"""
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # List to store all found HTML blob files
    html_files = []
    
    # Search patterns to look for
    search_dirs = [
        os.path.join(parent_dir, "**", "html_blob_*.html"),  # Search in all subdirectories
        os.path.join(parent_dir, "html_blob_*.html")         # Search in parent directory
    ]
    
    # Find all matching files
    for pattern in search_dirs:
        html_files.extend(glob.glob(pattern, recursive=True))
    
    # Extract dates from filenames and group files by date
    date_grouped_files = {}
    for file_path in html_files:
        filename = os.path.basename(file_path)
        # Extract date from filename (assuming format html_blob_*_YYYYMMDD.html)
        try:
            date_str = filename.split('_')[-1].replace('.html', '')
            if len(date_str) == 8 and date_str.isdigit():  # Ensure it's a valid YYYYMMDD format
                date_grouped_files.setdefault(date_str, []).append(file_path)
        except IndexError:
            continue
    
    # Find the date with the most files
    if not date_grouped_files:
        return []
    
    most_common_date = max(date_grouped_files.items(), key=lambda x: len(x[1]))[0]
    print(f"📅 Using files from date: {most_common_date}")
    
    return sorted(date_grouped_files[most_common_date])

def extract_body_content(html_file):
    """Extract the body content from an HTML file"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    soup = BeautifulSoup(content, 'html.parser')
    
    # Get the body content
    body = soup.body
    if body:
        return body.decode_contents()
    return ""

def generate_rollup():
    """Generate a combined HTML file from all html blobs"""
    html_files = find_html_blobs()
    
    if not html_files:
        print("❌ No HTML blob files found!")
        return
    
    print(f"📝 Found {len(html_files)} HTML blob files")
    
    # Get the date from the first file (they should all be the same date now)
    file_date = os.path.basename(html_files[0]).split('_')[-1].replace('.html', '')
    
    # Start building the combined HTML
    combined_html = """<!DOCTYPE html>
<html>
<head>
    <title>Combined Thangs Newsletter Showcase</title>
    <style>
        .showcase-section {
            margin: 20px 0;
            padding: 20px;
            border-bottom: 2px solid #eee;
        }
        .section-title {
            background: #f5f5f5;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1 style="text-align: center;">Combined Thangs Showcase</h1>
    <p style="text-align: center;">Date: """ + file_date + """</p>
"""
    
    # Add each file's content
    for html_file in html_files:
        file_name = os.path.basename(html_file)
        print(f"Processing: {file_name}")
        
        combined_html += f"""
    <div class="showcase-section">
        <div class="section-title">Source: {file_name}</div>
        {extract_body_content(html_file)}
    </div>
"""
    
    # Close the HTML
    combined_html += """
</body>
</html>
"""
    
    # Save the combined file using the same date as input files
    output_filename = f'combined_showcase_{file_date}.html'
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(combined_html)
    
    print(f"\n✅ Generated combined showcase: {output_filename}")

if __name__ == "__main__":
    print("🔄 Starting HTML Blob Rollup\n")
    generate_rollup()
    print("\n✨ Process completed successfully!")
