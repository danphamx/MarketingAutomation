import csv
from datetime import datetime
import os
from urllib.parse import quote, unquote

def get_github_raw_url(image_path):
    """Convert local image path to GitHub raw URL with proper encoding"""
    # Remove 'img/' from the start of the path if present
    image_path = image_path.replace('img/', '')
    
    # Split the path into directory and filename
    directory = "20250422"  # hardcoded since we know the structure
    filename = os.path.basename(image_path)
    
    # Handle already encoded characters by first decoding
    try:
        filename = unquote(filename)
    except:
        pass
    
    # Double encode the filename to match GitHub's encoding
    encoded_filename = quote(quote(filename))
    
    # Construct the full URL with encoded parts and proper GitHub path
    return f"https://raw.githubusercontent.com/danphamx/MarketingAutomation/refs/heads/main/img/{directory}/{encoded_filename}"

def generate_showcase_html():
    csv_files = [f for f in os.listdir('.') if f.startswith('image_links_') and f.endswith('.csv')]
    if not csv_files:
        print("No image_links CSV file found!")
        return
    
    # Use the most recent CSV file
    csv_file = sorted(csv_files)[-1]
    
    # Read the image links
    image_data = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            image_data.append({
                'image_path': row['Image Path'],
                'original_link': row['Original Link']
            })

    # Generate HTML content with CSS for image handling
    html_content = """
<!DOCTYPE html>
<html>
<head>
<style>
.image-container {
    width: 300px;
    height: 400px;
    display: inline-block;
    overflow: hidden;
    position: relative;
    margin: 0 5px;
}

.image-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
}

.row {
    margin-bottom: 20px;
    text-align: center;
}
</style>
</head>
<body>
<div style="text-align: center;">
    <span style="font-size:19px">What to Print This Weekend</span><br />
    Explore the latest 3D Printing Trends!<br />
    &nbsp;
</div>

<div style="text-align: left;">
    <p dir="ltr" style="text-align: center;">Designer Showcase<br />
    <span style="font-size:18px"><a href="https://thangs.com/leaderboard/period?league=All" target="_blank">
    <span style="color:#0000FF">Explore This Week's Exclusive Releases</span></a></span></p>

    <div style="text-align: center;">
"""

    # Add images in pairs
    for i in range(0, len(image_data), 2):
        html_content += '        <div class="row">\n'
        # First image in pair
        img1 = image_data[i]
        github_url1 = get_github_raw_url(img1['image_path'])
        print(f"Generated URL: {github_url1}")  # Debug print
        html_content += f"""            <div class="image-container">
            <a href="{img1['original_link']}" target="_blank">
                <img src="{github_url1}" alt="3D Model Preview" />
            </a>
        </div>"""

        # Second image in pair (if exists)
        if i + 1 < len(image_data):
            img2 = image_data[i + 1]
            github_url2 = get_github_raw_url(img2['image_path'])
            print(f"Generated URL: {github_url2}")  # Debug print
            html_content += f"""<div class="image-container">
            <a href="{img2['original_link']}" target="_blank">
                <img src="{github_url2}" alt="3D Model Preview" />
            </a>
        </div>"""
        
        html_content += '\n        </div>\n'

    # Close the HTML structure
    html_content += """    </div>
    <p dir="ltr" style="text-align: center;">
        <br />
        <a href="https://thangs.com/leaderboard/period?league=All" target="_blank">
            <span style="font-size:18px">View All Top Models</span>
        </a>
    </p>
</div>
</body>
</html>
"""

    # Write to file with date in filename
    current_date = datetime.now().strftime("%Y%m%d")
    output_filename = f'example_from_recent_send_{current_date}.html'
    with open(output_filename, 'w') as f:
        f.write(html_content)
    
    print(f"Generated HTML showcase in {output_filename}")

if __name__ == "__main__":
    generate_showcase_html() 