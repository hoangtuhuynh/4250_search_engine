## TODO
## Write the script to run 4 files as the main program

import crawler
import parser
import search
import searchEngine # More details to be showed
import searchEngine_simple # Limit the information to be showed
import pymongo

def main():
    # Define global variables
    seed_url = 'https://www.cpp.edu/cba/international-business-marketing/index.shtml'
    target_title = 'Faculty & Staff Directory'
    mongo_client = pymongo.MongoClient(host='localhost', port=27017)
    
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




