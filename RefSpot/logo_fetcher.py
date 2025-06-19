import requests
import os
import uuid
from urllib.parse import urlparse
from PIL import Image
import io

COMPANY_LOGO_FOLDER = 'static/uploads/company_logos'

def get_company_domain(company_name):
    """Get the most likely domain for a company"""
    # Clean company name
    clean_name = company_name.lower().strip()
    
    # Handle special cases first
    special_cases = {
        'google': 'google.com',
        'microsoft': 'microsoft.com',
        'apple': 'apple.com',
        'amazon': 'amazon.com',
        'facebook': 'facebook.com',
        'meta': 'meta.com',
        'netflix': 'netflix.com',
        'spotify': 'spotify.com',
        'uber': 'uber.com',
        'airbnb': 'airbnb.com',
        'tesla': 'tesla.com',
        'twitter': 'twitter.com',
        'linkedin': 'linkedin.com',
        'adobe': 'adobe.com',
        'salesforce': 'salesforce.com',
        'oracle': 'oracle.com',
        'ibm': 'ibm.com',
        'intel': 'intel.com',
        'cisco': 'cisco.com',
        'hp': 'hp.com',
        'dell': 'dell.com',
        'tata': 'tata.com',
        'reliance': 'ril.com',
        'infosys': 'infosys.com',
        'wipro': 'wipro.com',
        'tcs': 'tcs.com',
        'accenture': 'accenture.com'
    }
    
    # Check for special cases
    for key, domain in special_cases.items():
        if key in clean_name:
            return [domain]
    
    # Remove common corporate suffixes
    suffixes = [' inc', ' llc', ' ltd', ' corp', ' corporation', ' company', ' co', ' group', ' holdings', ' pvt', ' private', ' limited']
    for suffix in suffixes:
        if clean_name.endswith(suffix):
            clean_name = clean_name[:-len(suffix)].strip()
    
    # Replace spaces and special characters
    clean_name = clean_name.replace(' ', '').replace('&', 'and').replace('.', '').replace('-', '')
    
    # Try common domain extensions
    possible_domains = [
        f"{clean_name}.com",
        f"www.{clean_name}.com",
        f"{clean_name}.in",
        f"{clean_name}.org",
        f"{clean_name}.net",
        f"{clean_name}group.com",
        f"{clean_name}corp.com"
    ]
    
    return possible_domains

def fetch_logo_from_clearbit(company_name):
    """Fetch company logo from Clearbit Logo API"""
    domains = get_company_domain(company_name)
    
    for domain in domains:
        try:
            # Clearbit Logo API (free tier)
            url = f"https://logo.clearbit.com/{domain}"
            
            response = requests.get(url, timeout=10, allow_redirects=True)
            if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                return response.content
        except:
            continue
    
    return None

def fetch_logo_from_favicon(company_name):
    """Fetch company logo from favicon"""
    domains = get_company_domain(company_name)
    
    for domain in domains:
        try:
            # Try to get favicon from multiple sources
            favicon_urls = [
                f"https://www.google.com/s2/favicons?domain={domain}&sz=128",
                f"https://logo.clearbit.com/{domain}",
                f"https://{domain}/favicon.ico",
                f"https://{domain}/favicon.png",
                f"https://{domain}/apple-touch-icon.png",
                f"https://{domain}/android-chrome-192x192.png"
            ]
            
            for favicon_url in favicon_urls:
                response = requests.get(favicon_url, timeout=8, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                if response.status_code == 200 and len(response.content) > 200:  # Better size check
                    # Verify it's actually an image
                    if response.headers.get('content-type', '').startswith('image/'):
                        return response.content
        except:
            continue
    
    return None

def save_company_logo_from_data(logo_data, company_name):
    """Save logo data to file and return filename"""
    if not logo_data:
        return None
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(COMPANY_LOGO_FOLDER, exist_ok=True)
        
        # Open image and resize if needed
        image = Image.open(io.BytesIO(logo_data))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Resize to reasonable size
        max_size = (100, 100)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Generate unique filename
        filename = f"auto_{uuid.uuid4().hex[:8]}_{company_name.lower().replace(' ', '_')}.jpg"
        filepath = os.path.join(COMPANY_LOGO_FOLDER, filename)
        
        # Save as JPEG
        image.save(filepath, 'JPEG', quality=85, optimize=True)
        
        return filename
        
    except Exception as e:
        print(f"Error saving logo: {e}")
        return None

def fetch_company_logo(company_name):
    """Main function to fetch company logo automatically"""
    if not company_name or len(company_name.strip()) < 2:
        return None
    
    # Try Clearbit first (better quality)
    logo_data = fetch_logo_from_clearbit(company_name)
    
    # Fallback to favicon
    if not logo_data:
        logo_data = fetch_logo_from_favicon(company_name)
    
    # Save the logo if found
    if logo_data:
        return save_company_logo_from_data(logo_data, company_name)
    
    return None

def delete_company_logo(filename):
    """Delete company logo from filesystem"""
    if filename:
        file_path = os.path.join(COMPANY_LOGO_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)