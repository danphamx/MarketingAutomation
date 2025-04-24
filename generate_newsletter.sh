#!/bin/bash

# Exit on error
set -e

# Print commands before executing
set -x

# Print header
echo "🚀 Starting Newsletter Generation Process"
echo "========================================"

# Run all generator scripts
echo -e "\n📝 Running Premium Designer Generator..."
cd premium-designs
python3 generate_premium_designer_showcase.py

echo -e "\n📝 Running Maker League Generator..."
cd ../maker-showcase
python3 generate_makerleague_showcase.py

echo -e "\n📝 Running Designer Showcase Generator..."
cd ../free-models
python3 generate_designer_showcase.py

echo -e "\n📝 Running POD Designer Generator..."
cd ../print-on-demand
python3 generate_pod_showcase.py

echo -e "\n📝 Running HTML Blob Rollup..."
cd ../rollup
python3 generate_html_blob_rollup.py

echo -e "\n✨ Newsletter generation complete!"
echo "Check the rollup directory for the combined showcase file." 