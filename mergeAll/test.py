from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['test_database']
collection = db['test_collection']
collection.insert_one({"test": "connection successful"})
print("Inserted a test document")