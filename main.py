import pymongo
import crawler
import parser
import search
import searchEngine  # More details to be shown
import searchEngine_simple  # Limited information to be shown

def clear_database(mongo_client, db_name, collections_to_clear=None):
    """
    Clear specified collections in the database. If no collections are specified, clear the entire database.
    """
    db = mongo_client[db_name]
    if collections_to_clear:
        for collection in collections_to_clear:
            if collection in db.list_collection_names():
                db[collection].drop()
                print(f"Cleared collection: {collection}")
    else:
        for collection in db.list_collection_names():
            db[collection].drop()
            print(f"Cleared collection: {collection}")
    print(f"Database '{db_name}' cleared.")

def main():
    # Define global variables
    seed_url = 'https://www.cpp.edu/cba/international-business-marketing/index.shtml'
    target_title = 'Faculty & Staff Directory'
    db_name = 'cs4250project'  # Specify your database name
    collections_to_clear = ['pages', 'professors']  # Specify collections to clear
    mongo_client = pymongo.MongoClient(host='localhost', port=27017)

    # Step 0: Clear the database (specific collections)
    clear_database(mongo_client, db_name, collections_to_clear)

    # Step 1: Run the crawler
    crawler.run_crawler(seed_url, target_title, mongo_client)

    # Step 2: Run the parser
    parser.run_parser(target_title, mongo_client)

    # Step 3: Run the search
    search.run_search(mongo_client)

    # Step 4: Run the search engine (interactive)
    searchEngine_simple.run_search_engine(mongo_client)
    # searchEngine.run_search_engine(mongo_client)

if __name__ == '__main__':
    main()
