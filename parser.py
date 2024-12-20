from bs4 import BeautifulSoup
import pymongo
import re

def get_dict(source, target):
    result = source.find_one({'title': target})
    if result is None:
        raise ValueError(f"No document found with title: {target}")
    return result

def get_faculty_tags(html):
    bs = BeautifulSoup(html, 'html.parser')
    return bs.find_all('div', {'class': 'col-md directory-listing'})

def store_info(html, dest):
    name_tag = html.find('h3')
    # Extract the text and clean up text
    name = name_tag.get_text(strip=True) if name_tag else None
    if name:
        name = re.sub(r'\\n', ' ', name)  # Remove escaped newline characters
        name = re.sub(r'[\n\r]+', ' ', name)  # Remove actual newlines (\r and \n)
        name = re.sub(r'\s+', ' ', name).strip()  # Replace multiple spaces with a single space

    title_tag = html.find('div', {'class': 'mb-1 text-muted'})
    title = title_tag.get_text(strip=True) if title_tag else None

    info = get_info(html)

    if name and title:
        info['name'] = name
        info['title'] = title
        print(info)  # Debugging: Print the extracted information
        dest.insert_one(info)

def get_info(html):
    result = {}
    ul_tag = html.find('ul')
    if not ul_tag:
        return result

    email_tag = ul_tag.find('a', href=lambda href: href and 'mailto:' in href)
    result['email'] = email_tag['href'].replace('mailto:', '') if email_tag else None

    phone_tag = ul_tag.find('i', {'class': 'fas fa-phone'})
    if phone_tag and phone_tag.find_next_sibling(text=True):
        result['phone'] = phone_tag.find_next_sibling(text=True).strip()

    office_tag = ul_tag.find('i', {'class': 'fas fa-building'})
    if office_tag and office_tag.find_next_sibling(text=True):
        result['office'] = office_tag.find_next_sibling(text=True).strip()

    profile_tag = ul_tag.find('a', href=True, title=True)
    result['profile'] = profile_tag['href'] if profile_tag else None

    return result

def run_parser(target_title, mongo_connection):
    # Use the MongoDB connection
    db = mongo_connection.cs4250project
    pages = db.pages
    professors = db.professors

    try:
        # Retrieve the target page's data
        page = get_dict(pages, target_title)
        if not page:
            print(f"No page found with title: {target_title}")
            return

        html = page['html']
        profs = get_faculty_tags(html)

        for prof in profs:
            store_info(prof, professors)
            print('\n')

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print("Parsing completed.")
