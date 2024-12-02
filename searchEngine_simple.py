from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pymongo

BASE_URL = "https://www.cpp.edu"

# Retrieve all faculty pages from MongoDB
def retrieve_professors(professors_collection):
    return list(professors_collection.find())

# Pre-process and vectorize documents
def create_tfidf_vectorizer(professors):
    documents = [
        (
            (professor.get('name', '') or '') + " " +
            (professor.get('title', '') or '') + " " +
            (professor.get('email', '') or '') + " " +
            (professor.get('phone', '') or '') + " " +
            (professor.get('office', '') or '') + " " +
            (professor.get('about', '') or '') + " " +
            (professor.get('publications', '') or '') + " " +
            " ".join((professor.get('accolades', {}) or {}).values())
        )
        for professor in professors
    ]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    return vectorizer, tfidf_matrix

# Search the database for relevant faculty members based on the query
# Threshold is used to make search results more strict
# ADJUST THRESHOLD VALUE IF NECESSARY (e.g. o.1, o.4, etc.)
def search(query, vectorizer, tfidf_matrix, professors, threshold=0):
    query_vectorizer = vectorizer.transform([query])
    similarities = cosine_similarity(query_vectorizer, tfidf_matrix).flatten()

    # Sort the results by similarity score
    sorted_indices = similarities.argsort()[::-1]

    # Return sorted documents and their similarity scores
    results = []
    for index in sorted_indices:
        if similarities[index] > threshold:
            professor = professors[index]
            profile_url = professor.get('profile', 'N/A')
            if profile_url != 'N/A' and not profile_url.startswith('http'):
                profile_url = f"{BASE_URL}{profile_url}"  # Prepend the base URL if needed

            result = {
                'name': professor.get('name', 'N/A'),
                'about': professor.get('about', 'N/A'),
                'profile': profile_url,
            }
            results.append(result)
    return results

# Display search results
def display_results(results):
    print("=" * 50)
    print("Search Results")
    print("=" * 50)

    for result in results:
        print(f"Name: {result['name']}")
        print(f"Description: {result['about']}")
        print(f"Profile URL: {result['profile']}")
        print("-" * 50)

    print("\nEND OF SEARCH RESULTS\n")

# Interactive search engine function
def run_search_engine(mongo_connection):
    # Use the MongoDB connection
    db = mongo_connection['cs4250project']
    professors_collection = db['professors']

    # Retrieve professor data from MongoDB
    professors_data = retrieve_professors(professors_collection)

    # Create TF-IDF vectorizer and matrix
    vectorizer, tfidf_matrix = create_tfidf_vectorizer(professors_data)

    # Interactive search process
    done = False
    while not done:
        print("\nType 'exit' or 'quit' to stop the search at any time.")
        query = input("Enter your search query: ").strip()

        # Check if the user wants to exit
        if query.lower() in ['exit', 'quit']:
            print("Exiting the search engine.")
            done = True
            continue

        # Perform search
        search_results = search(query, vectorizer, tfidf_matrix, professors_data)

        # Display results
        if search_results:
            display_results(search_results)
        else:
            print("No results found.")
