import requests
from bs4 import BeautifulSoup

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
    page_title = input("Enter the Wikipedia page title to scrape: ")
    url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
    soup = get_wikipedia_page(url)
    information = extract_entire_page(soup)
    print("Extracted Information: ")
    print(information) 
       # Saving the information to a file
    with open('extracted_info.txt', 'w', encoding='utf-8') as file:
        file.write(information)
    

if __name__ == "__main__":
    main()
