import pymongo
import requests
from bs4 import BeautifulSoup

# MongoDB connection
# MongoDB connection test
try:
    client = pymongo.MongoClient('mongodb+srv://piyanshu:piyanshug@cluster0.sghco.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0', serverSelectionTimeoutMS=5000)
    # Ping the database to check connection
    client.admin.command('ping')
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

db = client['search_engine']

def scrape_data():
    results = []
    base_url = "https://stackoverflow.com/questions/tagged/python?tab=newest&page={page}&pagesize=15"

    try:
        for page in range(1, 10):  # Limit pages for initial testing; change to 39490 for full scraping
            response = requests.get(base_url.format(page=page))
            if response.status_code != 200:
                print(f"Failed to fetch page {page}. Status Code: {response.status_code}")
                continue

            content = BeautifulSoup(response.text, 'html.parser')
            questions = content.find_all('div', {'class': 's-post-summary js-post-summary'})

            print(f"Scraping page {page}, found {len(questions)} questions.")  # Print the number of questions found

            for item in questions:
                title_element = item.find('a', {'class': 's-link'})
                description_element = item.find("div", {"class": "s-post-summary--content-excerpt"})

                # Extract title, link, and description
                title = title_element.text.strip() if title_element else "No title"
                link = 'https://stackoverflow.com/' + title_element['href'] if title_element else "No link"
                description = description_element.text.strip().replace('\n', '') if description_element else "No description"

                # Append to results
                results.append({'title': title, 'link': link, 'description': description})

            print(f"Page {page} scraped. Total results so far: {len(results)}")

        # Insert all results into MongoDB
        if results:
            db.data.insert_many(results)
            print(f"Inserted {len(results)} records into MongoDB.")

        # Create a text index on the 'title' field for full-text search
        db.data.create_index([('title', pymongo.TEXT)])
        print("Text index created on 'title'.")

    except Exception as e:
        print(f"An error occurred: {e}")


scrape_data()