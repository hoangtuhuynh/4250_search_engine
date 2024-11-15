from urllib.request import urlopen
from pymongo import MongoClient
from bs4 import BeautifulSoup
import re
BASE_URL = "https://www.cpp.edu"  # Replace with the base URL of the site
# Function to fetch the About section
def fetch_about_section(soup):
    about_section = soup.find('h2', string=re.compile(r'About Me'))
    if about_section:
        parent = about_section.find_parent("div", class_="section-intro")
        if parent:
            return parent.get_text(strip=True)
    return None

# Function to fetch the Selected Publications section
def fetch_publications_section(soup):
    publications_section = soup.find('h2', string=re.compile(r'Selected Publications'))
    if publications_section:
        parent = publications_section.find_parent("div", class_="section-intro")
        if parent:
            return parent.get_text(strip=True)
    return None

# Function to dynamically fetch all content after the Accolades section
def fetch_accolades_section(soup):
    accolades = {}
    accolades_sections = soup.find_all('div', class_="accolades")
    for section in accolades_sections:
        heading = section.find('h2')
        if heading:
            content = section.get_text(strip=True)
            accolades[heading.get_text(strip=True)] = content.replace(heading.get_text(strip=True), "").strip()
    return accolades

# Main function to crawl and store data


def fetch_and_store_data(url):
    try:
        # Construct absolute URL if the provided URL is relative
        if not url.startswith("http"):
            url = BASE_URL + url
        
        html = urlopen(url)
        page = html.read()
        soup = BeautifulSoup(page, 'html.parser')

        # Extract About section
        about_section = fetch_about_section(soup)

        # Extract Selected Publications section
        publications_section = fetch_publications_section(soup)

        # Extract dynamic content from Accolades section
        accolades_content = fetch_accolades_section(soup)

        return {
            "about": about_section,
            "publications": publications_section,
            "accolades": accolades_content,
        }
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return None

def main():
    # MongoDB connection
    client = MongoClient(host='localhost', port=27017)
    db = client['cs4250project']
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

    client.close()

if __name__ == "__main__":
    main()
