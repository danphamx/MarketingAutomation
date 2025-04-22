import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote, unquote
import time
import csv
from datetime import datetime
import subprocess

def check_github_status():
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

def get_github_raw_url(image_path):
    """Convert local image path to GitHub raw URL"""
    image_path = image_path.replace('img/', '')
    directory = datetime.now().strftime('%Y%m%d')
    filename = os.path.basename(image_path)
    
    try:
        filename = unquote(filename)
    except:
        pass
    
    encoded_filename = quote(quote(filename))
    return f"https://raw.githubusercontent.com/danphamx/MarketingAutomation/refs/heads/main/free-models/img/{directory}/{encoded_filename}" 