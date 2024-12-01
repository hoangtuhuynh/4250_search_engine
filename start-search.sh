#!/bin/bash

# stop the script in case anything happens
set -e

# spin up the local MongoDB server
mongod --config /opt/homebrew/etc/mongod.conf

# setting up the virtual environment
echo "Setting up the virtual environment..."
python -m venv cs4250 

# set the source
source cs4250/bin/activate

# download and install dependencies
echo "Downloading and installing dependencies..."
pip install -r requirements.txt

# start the crawler
echo "Starting crawler.py..."
python3 crawler.py

# start the parser
echo "Starting parser.py..."
python3 crawler.py

# start search.py
echo "Starting search.py..."
python3 search.py

# start the search engine
echo "Starting the search engine..."
python3 searchEngine.py