from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import mysql.connector
from dotenv import load_dotenv
import os

#initialize Flask app
app = Flask(__name__)
CORS(app)

#Load .env file
load_dotenv()

#Database config
db_config = {
   'user': os.getenv('DB_USER'),
   'password': os.getenv('DB_PASSWORD'),
   'host': os.getenv('DB_HOST'),
   'database': os.getenv('DB_NAME')
  }


def create_database(cursor, DB_NAME):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        

def create_table(cursor, DB_NAME):
    try:
        cursor.execute(f"USE {DB_NAME}")
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


def search_articles(conn, search_query):
    try:
        cursor = conn.cursor()
        query =  "SELECT * FROM wikipedia_articles WHERE title LIKE %s OR content LIKE %s"
        cursor.execute(query, ('%' + search_query + '%', '%' + search_query + '%'))
        results = cursor.fetchall()
        for row in results:
            print(row)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        

def update_article(conn, article_id, new_title, new_content):
    try:
        cursor = conn.cursor()
        query = "UPDATE wikipedia_articles SET title = %s, content = %s WHERE id = %s"
        cursor.execute(query, (new_title, new_content, article_id))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        

def delete_article(conn, article_id):
    try:
        cursor = conn.cursor()
        query = "DELETE FROM wikipedia_articles WHERE id = %s"
        cursor.execute(query, (article_id,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        
@app.route('/scrape', methods=['POST'])
def scrape_wikipedia():
    page_title = request.json['title']
    url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
    soup = get_wikipedia_page(url)
    content = extract_entire_page(soup)
    save_scraped_data(mysql.connector.connect(**db_config), page_title, url, content)
    return jsonify({"message": "Scraped and saved successfully", "title": page_title, "url": url})


app.route('/search', methods=['GET'])
def search():
        search_query = request.args.get('query')
        conn = mysql.connector.connect(**db_config)
        results = search_articles(conn, search_query)
        conn.close()
        return jsonify(results)
    

app.route('/update', metods=['PUT'])
def update():
    article_id = request.json['id']
    new_title = request.json['title']
    new_content = request.json['content']
    conn = mysql.connector.connect(**db_config)
    update_article(conn, article_id, new_title, new_content)
    conn.close()
    return jsonify({"message": "Article updated", "id": article_id})

@app.route('/delete', methods=['DELETE'])
def delete():
    article_id = request.json['id']
    conn = mysql.connector.connect(**db_config)
    delete_article(conn, article_id)
    conn.close()
    return jsonify({"message": "Article deleted", "id": article_id})

if __name__ == "__main__":
    app.run(debug=True)
