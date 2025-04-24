#!/bin/bash

# Exit on error
set -e

# Print commands before executing
set -x

echo "🚀 Starting Thangs Newsletter Generation"

# Function to run Python script and check status
run_python_script() {
    local script_path="$1"
    local script_dir=$(dirname "$script_path")
    local script_name=$(basename "$script_path")
    
    # Change to script directory
    cd "$script_dir"
    
    if ! python "$script_name"; then
        echo "❌ Error running $script_path"
        exit 1
    fi
    
    # Return to original directory
    cd - > /dev/null
}

# Store the root directory
ROOT_DIR="$(pwd)"

# Premium Designer Showcase
echo -e "\n📦 Generating Premium Designer Showcase..."
run_python_script "premium-designs/generate_premium_designer_showcase.py"

# Maker League Showcase
echo -e "\n🏆 Generating Maker League Showcase..."
run_python_script "maker-showcase/generate_makerleague_showcase.py"
run_python_script "maker-showcase/fetch_makerleague_links.py"

# Free Models Showcase
echo -e "\n🎁 Generating Free Models Showcase..."
run_python_script "free-models/generate_designer_showcase.py"
run_python_script "free-models/fetch_thangs_links.py"
run_python_script "free-models/download_thumbnails.py"

# Print on Demand Showcase
echo -e "\n🖨️  Generating Print on Demand Showcase..."
run_python_script "print-on-demand/generate_pod_showcase.py"

# Ensure we're in the root directory
cd "$ROOT_DIR"

# Combine all showcases
echo -e "\n🔄 Combining all showcases..."
run_python_script "rollup/generate_html_blob_rollup.py"

# Get today's date in YYYYMMDD format
TODAY=$(date +%Y%m%d)

echo -e "\n✨ Newsletter generation complete!"
echo "📄 Find the combined HTML in rollup/combined_showcase_${TODAY}.html" 