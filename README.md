# Marketing Automation for Thangs Newsletter

## Overview
This project automates the process of creating visually appealing newsletters featuring trending 3D models from Thangs.com. What used to be a manual 1-4 hour weekly process has been transformed into an automated workflow that pulls live data directly from Thangs.com.

## Key Features
- **Automated Content Generation**: Scripts automatically fetch trending models and designer content from Thangs.com
- **Multiple Showcase Types**:
  - Premium Designer Showcase
  - Maker League Showcase
  - Designer Showcase
  - POD (Print on Demand) Designer Showcase
- **HTML Generation**: Creates Mailchimp-compatible HTML for each showcase type
- **Combined View**: Generates a unified view of all showcases for easy review

## Project Structure
```
.
├── premium-designs/          # Premium designer content generation
├── maker-showcase/          # Maker league content generation
├── rollup/                  # Combined showcase generator
└── README.md               # This file
```

## How It Works
1. Individual scripts fetch current trending models and designer content from Thangs.com
2. Each script generates a formatted HTML blob optimized for email marketing
3. The rollup script (`generate_html_blob_rollup.py`) combines all HTML blobs into a single preview file
4. The generated HTML can be directly used in Mailchimp for the weekly newsletter

## Benefits
- **Time Savings**: Reduces newsletter creation time from hours to minutes
- **Real-time Content**: Always features the most current trending content from Thangs.com
- **Consistency**: Maintains a professional, uniform layout across newsletters
- **Flexibility**: Modular design allows for easy updates and modifications

## Alternative Solutions Considered
Several alternatives were evaluated before developing this automation solution:

1. **Hiring Freelancers**
   - Requires ongoing coordination and management
   - Inconsistent availability and quality
   - Recurring costs for routine work
   - Limited technical understanding of the platform

2. **Marketing Agency**
   - High monthly retainer costs
   - Less direct control over content
   - Slower turnaround times
   - Additional overhead in communication

3. **Engineering Resources**
   - Expensive use of developer time
   - Competing priorities with product development
   - Overqualified for the task
   - Less marketing-focused approach

The automated solution provides the best balance of cost, efficiency, and control while freeing up valuable team resources for higher-impact tasks.

## Usage
1. Run individual showcase generators:
   ```bash
   python premium-designs/generate_premium_designer_showcase.py
   python maker-showcase/fetch_thangs_links.py
   # ... other showcase generators
   ```
2. Combine all showcases:
   ```bash
   python rollup/generate_html_blob_rollup.py
   ```
3. Find the combined HTML in `rollup/combined_showcase_YYYYMMDD.html`

## Requirements
- Python 3.x
- BeautifulSoup4
- Requests

## Contributing
Feel free to submit issues and enhancement requests!