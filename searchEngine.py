from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pymongo


# Connect to MongoDB
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.cs4250project
professors = db.professors


# Retrieve all faculty pages from MongoDB
def retrieveProfessors():
    return list(professors.find())


# Pre-process and vectorize documents
def createTFIDFVectorizer(professors):
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
    tfidfMatrix = vectorizer.fit_transform(documents)
    return vectorizer, tfidfMatrix


# Search the database for relevant faculty members based on the query
def search(query, vectorizer, tfidfMatrix, professors):
    queryVectorizer = vectorizer.transform([query])
    similarities = cosine_similarity(queryVectorizer, tfidfMatrix).flatten()

    # Sort the results by similarity score
    sortedIndeces = similarities.argsort()[::-1]

    # Return sorted documents and their similarity scores
    results = []
    for index in sortedIndeces:
        if similarities[index] > 0:
            professor = professors[index]
            result = {
                'name': professor['name'],
                'title': professor.get('title', 'N/A'),
                'email': professor.get('email', 'N/A'),
                'phone': professor.get('phone', 'N/A'),
                'office': professor.get('office', 'N/A'),
                'profile': professor.get('profile', 'N/A'),
                'about': professor.get('about', 'N/A'),
                'publications': professor.get('publications', 'N/A'),
                'accolades': professor.get('accolades', {}),
                'similarity': similarities[index]
            }
            results.append(result)
    return results


# Display search results
def displayResults(results):
    print("=" * 50)
    print("Search Results")
    print("=" * 50)

    for result in results:
        print(f"Name: {result['name']}")
        print(f"Title: {result['title']}")
        print(f"Email: {result['email']}")
        print(f"Phone: {result['phone']}")
        print(f"Office: {result['office']}")
        print(f"Profile: {result['profile']}")
        print()
        print(f"About: {result['about']}")
        print()
        print(f"Publications: {result['publications']}")
        print()
        print("-" * 50)

    print("\nEND OF SEARCH RESULTS\n")


# Main search function
def main():
    done = False
    while not done:
        query = input("Enter your search query: ").strip()

        facultyData = retrieveProfessors()
        vectorizer, tfidfMatrix = createTFIDFVectorizer(facultyData)

        search_results = search(query, vectorizer, tfidfMatrix, facultyData)

        if search_results:
            displayResults(search_results)
        else:
            print("No results found.")

if __name__ == '__main__':
    main()
