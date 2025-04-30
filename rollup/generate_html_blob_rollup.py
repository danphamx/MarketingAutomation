import os
import glob
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote

def find_html_blobs(date_str=None):
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
            file_date = filename.split('_')[-1].replace('.html', '')
            if len(file_date) == 8 and file_date.isdigit():  # Ensure it's a valid YYYYMMDD format
                # If date_str is provided, only include files matching that date
                if date_str and file_date != date_str:
                    continue
                date_grouped_files.setdefault(file_date, []).append(file_path)
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

def get_github_source_url(file_path):
    """Convert local file path to GitHub source URL"""
    # Using the repository URL from the README demo links
    base_url = "https://github.com/danphamx/MarketingAutomation/blob/main"
    
    # Get the actual directory name from the file path
    dir_name = os.path.dirname(file_path)
    if dir_name:
        # Get just the last directory name from the path
        dir_name = os.path.basename(dir_name)
        # First decode the filename in case it's already URL-encoded
        filename = os.path.basename(file_path)
        try:
            filename = unquote(filename)
            # Double encode the filename - this is what GitHub expects
            encoded_filename = quote(quote(filename, safe=''), safe='')
        except:
            # Fallback to simple encoding if there's an error
            encoded_filename = quote(filename, safe='')
        return f"{base_url}/{dir_name}/{encoded_filename}"
    else:
        # If no directory (file is in root), just append filename
        filename = os.path.basename(file_path)
        try:
            filename = unquote(filename)
            encoded_filename = quote(quote(filename, safe=''), safe='')
        except:
            encoded_filename = quote(filename, safe='')
        return f"{base_url}/{encoded_filename}"

def generate_rollup():
    """Generate a combined HTML file from all html blobs"""
    # Use today's date to find HTML blobs
    today_date = datetime.now().strftime('%Y%m%d')
    html_files = find_html_blobs(today_date)
    
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
        .source-link {
            color: #0366d6;
            text-decoration: none;
        }
        .source-link:hover {
            text-decoration: underline;
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
        github_url = get_github_source_url(html_file)  # Now passing the full file path
        print(f"Processing: {file_name}")
        
        combined_html += f"""
    <div class="showcase-section">
        <div class="section-title">Source: <a href="{github_url}" class="source-link" target="_blank">{file_name}</a></div>
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

def update_readme_with_latest_link(date_str):
    """Update README.md with the latest newsletter link"""
    readme_path = os.path.join('..', 'README.md')
    combined_showcase_url = f"https://danphamx.github.io/MarketingAutomation/rollup/combined_showcase_{date_str}.html"
    
    try:
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Find the "Links to Newsletters" section
        section_start = content.find("## Links to Newsletters")
        if section_start == -1:
            print("❌ Could not find 'Links to Newsletters' section in README.md")
            return
        
        # Find the end of the section
        section_end = content.find("##", section_start + 1)
        if section_end == -1:
            section_end = len(content)
        
        # Create new content with updated link
        new_section = f"""## Links to Newsletters

- Latest Newsletter Preview: {combined_showcase_url}
- Previous Newsletters:
  - [2024-04-22](https://danphamx.github.io/MarketingAutomation/rollup/combined_showcase_20250422.html)
"""
        
        # Replace the section
        new_content = content[:section_start] + new_section + content[section_end:]
        
        with open(readme_path, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Updated README.md with latest newsletter link: {combined_showcase_url}")
    except Exception as e:
        print(f"❌ Error updating README.md: {e}")

def main():
    print("🔄 Starting HTML Blob Rollup\n")
    
    # Generate the combined showcase
    generate_rollup()
    
    # Update README with latest link
    update_readme_with_latest_link(datetime.now().strftime('%Y%m%d'))
    
    print("\n✨ Process completed successfully!")
    
    # Add Git reminder
    print("\n⚠️  IMPORTANT: Remember to push your changes to GitHub!")
    print("This ensures all images will be accessible in the newsletter.")
    print("\nRun these commands:")
    print("  git add .")
    print("  git commit -m 'Update newsletter content and images'")
    print("  git push origin main")

if __name__ == "__main__":
    main()
