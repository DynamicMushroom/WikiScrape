import requests
from bs4 import BeautifulSoup
import mysql.connector
from dotenv import load_dotenv
import os

#Load .env file
load_dotenv()

#Database config
db_config = {
   'user': os.getenv('DB_USER'),
   'password': os.getenv('DB_PASSWORD'),
   'host': os.getenv('DB_HOST'),
   'database': os.getenv('DB_NAME')
  }


def create_database(cursor, db_name):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        

def create_table(cursor, db_name):
    try:
        cursor.execute(f"USE {db_name}")
        cursor.execute("""
             CREATE TABLE IF NOT EXISTS wikipedia_articles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                url VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
        """)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        

def save_scraped_data(conn, title, url, content):
    try:
        cursor = conn.cursor()
        query = "INSERT INTO wikipedia_articles (title, url, content) VALUES (%s, %s, %s)"
        cursor.execute(query, (title, url, content))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        

def get_wikipedia_page(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def extract_entire_page(soup):
    content = ''
    for paragraph in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
        content += paragraph.get_text() + '\n'
    return content

def main():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # Create database and tables
        create_database(cursor, "wikiscrape")
        create_table(cursor, "wikiscrape")
        page_title = input("Enter the Wikipedia page title to scrape: ")
        url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
        soup = get_wikipedia_page(url)
        content = extract_entire_page(soup)
        print("Extracted Information: ")
        print(content)

        # Save the scraped data to the database
        save_scraped_data(conn, page_title, url, content)

        # Saving the information to a file
        with open('extracted_info.txt', 'w', encoding='utf-8') as file:
            file.write(content)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
