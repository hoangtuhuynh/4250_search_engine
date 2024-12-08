from urllib.request import urlopen
from pymongo import MongoClient
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.cpp.edu"  # Replace with the base URL of the site

# # Function to fetch the About section
def fetch_about_section(soup):
    try:
        # about_header = soup.find('h2', string=re.compile(r'(About|Bio|Short|Biography|Overview)\s+.*', re.IGNORECASE))
        about_header = soup.find(re.compile(r'(h2|h3|p)'), string=re.compile(r'(About|Bio|Short|Biography|Overview)', re.IGNORECASE))

        if about_header:
            parent_div = about_header.find_parent('div', class_='section-intro')
            if parent_div:
                about_content = parent_div.find('div', class_='section-menu')
                if about_content:
                    return about_content.get_text(separator="\n", strip=True)
        return None
    except Exception as e:
        print(f"Error fetching About section: {e}")
        return None



# Function to fetch the Selected Publications section
def fetch_publications_section(soup):
    try:
        publications_section = soup.find('h2', string=re.compile(r'Selected Publications'))
        if publications_section:
            parent = publications_section.find_parent("div", class_="section-intro")
            if parent:
                return parent.get_text(strip=True)
        return None
    except Exception as e:
        print(f"Error fetching Publications section: {e}")
        return None

# Function to dynamically fetch all content after the Accolades section
def fetch_accolades_section(soup):
    accolades = {}
    try:
        accolades_sections = soup.find_all('div', class_="accolades")
        for section in accolades_sections:
            heading = section.find('h2')
            if heading:
                content = section.get_text(strip=True)
                accolades[heading.get_text(strip=True)] = content.replace(heading.get_text(strip=True), "").strip()
    except Exception as e:
        print(f"Error fetching Accolades section: {e}")
    return accolades

# Function to fetch and structure dynamic content
def fetch_and_store_data(url):
    try:
        if not url.startswith("http"):
            url = BASE_URL + url

        html = urlopen(url)
        page = html.read()
        soup = BeautifulSoup(page, 'html.parser')

        # Extract dynamic sections
        about_section = fetch_about_section(soup)
        publications_section = fetch_publications_section(soup)
        accolades_content = fetch_accolades_section(soup)

        return {
            "about": about_section,
            "publications": publications_section,
            "accolades": accolades_content,
        }
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return None

# Updated function to replace main()
def run_search(mongo_connection):
    # Use the MongoDB connection
    db = mongo_connection['cs4250project']
    collection = db['professors']

    for professor in collection.find():
        profile_url = professor.get('profile')  # Ensure profile field is used
        if profile_url:
            print(f"Fetching data for {professor['name']} from {profile_url}")
            data = fetch_and_store_data(profile_url)
            if data:
                collection.update_one(
                    {"_id": professor["_id"]},
                    {"$set": {
                        "about": data["about"],
                        "publications": data["publications"],
                        "accolades": data["accolades"]
                    }}
                )
                print(f"Updated data for {professor['name']}")
        else:
            print(f"No profile URL for {professor['name']}")

    print("Search and update completed.")
