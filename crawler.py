from urllib.request import urlopen
from bs4 import BeautifulSoup
import pymongo
import re

def find_target_page(frontier, target_title, col):
    for site in frontier:
        print(f"Processing URL: {site}")
        base = re.match(r'https://\w*\.\w+\.\w+', site).group()
        
        html = urlopen(site).read()
        bs = BeautifulSoup(html, 'html.parser')
        title = bs.find('title').getText().strip()
        store_page(title, site, html, col)

        # Find the links on the page
        links = bs.find_all('a', {'href': re.compile('/')})
        urls = [link.get('href') for link in links]

        # Convert relative links to absolute URLs
        for i, url in enumerate(urls):
            if url.startswith('/'):
                urls[i] = base + url

        # Check for the specific "Faculty & Staff Directory" link
        for link in links:
            if "Faculty & Staff Directory" in link.text:  # Target menu text
                directory_url = link['href']
                if directory_url.startswith('/'):
                    directory_url = base + directory_url
                print(f"Found 'Faculty & Staff Directory' link: {directory_url}")
                frontier.append(directory_url)  # Add to frontier

        # Add new links to the frontier
        for url in urls:
            if url not in frontier:
                frontier.append(url)

        if title == target_title:
            break

def store_page(title, url, html, col):
    doc = {'title': title,
           'url': url,
           'html': str(html)}
    col.insert_one(doc)

def run_crawler(seed_url, target_title, mongo_connection):
    # Use provided seed URL and target title
    frontier = [seed_url]

    # Use the MongoDB connection
    db = mongo_connection.cs4250project
    pages = db.pages

    find_target_page(frontier, target_title, pages)

    print('Crawling completed.')
