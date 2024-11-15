import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time
import math

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['cpp_search_engine']
collection = db['pages']

# Retrieve URL with headers and retries
def retrieve_url(url, retries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(retries):
        try:
            response = urllib.request.urlopen(req)
            return response.read().decode('utf-8')
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            time.sleep(1)  # Wait before retrying
    return None  # Return None after retries

# Parse HTML to extract links
def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def extract_links(soup, base_url):
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Handle relative and absolute links
        if href.startswith('/'):
            href = base_url + href
        if href.startswith('http'):
            links.append(href)
    return links

# Check if the page is a target
def is_target_page(soup):
    # Target page detection logic (replace with actual criteria for faculty pages)
    return bool(soup.find("div", {"class": "areas-of-search"}))

# Crawl the website
def crawler(seed_urls, num_targets):
    frontier = seed_urls
    visited = set()
    targets_found = 0

    while frontier and targets_found < num_targets:
        url = frontier.pop(0)
        if url in visited:
            continue
        visited.add(url)

        html = retrieve_url(url)
        if not html:
            continue  # Skip if URL retrieval failed
        soup = parse_html(html)

        # Store page content in MongoDB
        collection.insert_one({"url": url, "html": html})
        
        if is_target_page(soup):
            targets_found += 1
            print(f"Target page found: {url}")
        
        if targets_found < num_targets:
            new_links = extract_links(soup, "/".join(url.split("/")[:3]))
            for link in new_links:
                if link not in visited:
                    frontier.append(link)

# Start crawling
seed_urls = [
    "https://www.cpp.edu/cba/international-business-marketing/index.shtml"
]

crawler(seed_urls, 30)

# Data Parsing and Indexing
def extract_area_of_search(html):
    soup = parse_html(html)
    area_of_search = soup.find("div", {"class": "areas-of-search"})
    return area_of_search.text.strip() if area_of_search else None

def index_data():
    documents = []
    urls = []
    for page in collection.find():
        area_of_search = extract_area_of_search(page['html'])
        if area_of_search:
            documents.append(area_of_search)
            urls.append(page['url'])
    return documents, urls

documents, urls = index_data()

# TF-IDF Vectorization
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(documents)

# Query Functionality
def search_query(query, tfidf_matrix, urls, top_k=5):
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    ranked_indices = scores.argsort()[::-1][:top_k]
    results = [(urls[i], documents[i]) for i in ranked_indices if scores[i] > 0]
    return results

# Pagination
def paginate(results, page, per_page=5):
    total_pages = math.ceil(len(results) / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    return results[start:end], total_pages

# Example usage
query = "marine biology"
results = search_query(query, tfidf_matrix, urls)
page = 1
paginated_results, total_pages = paginate(results, page)

print(f"Page {page}/{total_pages}")
for url, snippet in paginated_results:
    print(f"URL: {url}\nSnippet: {snippet[:100]}...\n")
