from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import csv

url = f'https://books.toscrape.com/catalogue/category/books_1/'
HEADERS = {
  "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36"
}

def extractElement(soup):
  try:
    mainContainer = soup.find('div', class_='col-sm-8 col-md-9')
    sectionContainer = mainContainer.find('section')
    olElement = sectionContainer.find('ol', class_='row')
    liElement = olElement.find_all('li', class_='col-xs-6 col-sm-4 col-md-3 col-lg-3')
    return liElement

  except AttributeError as e:
    print(f"HTML parsing error")
    return []
  

def bookData(liElement):
  bookAttr = []
  for book in liElement:
    try:    
      bookName = book.find('h3').find('a').get('title')
      bookPrice = book.find('p', class_='price_color').text.strip()
      bookStock = book.find('p', class_='instock availability').text.strip()
      bookLink = urljoin(url, book.find('h3').find('a').get('href'))
    
      bookAttr.append([bookName, bookPrice, bookStock, bookLink])
    except AttributeError:
      print("Skipping one book due to missing data.")
      continue

  return bookAttr

def page():
  page = 1
  allBooks = []
  
  while True:
    page_url = f'{url}page-{page}.html'
    print(f'Fetching: {page_url}')
    try :
      response = requests.get(page_url, headers=HEADERS)
      response.raise_for_status()
    except requests.exceptions.RequestException as e:
      print(f'Request failed: {e}')
      break
      
    soup = BeautifulSoup(response.text, 'lxml')
    
    extractor = extractElement(soup)
    allBooks.extend(bookData(extractor))
    
    nextButton = soup.find('li', class_='next')
    if not nextButton:
      break
    page += 1
    
  return allBooks

def write_csv(data):
  try:
    with open("books.csv", "w", newline="", encoding='utf-8') as file:
      writer = csv.writer(file)
      writer.writerow(['Book Name', 'Book Price', 'Book Stock', 'Book Link'])
      writer.writerows(data)
    print('Books Saved at books.csv!')
  except PermissionError:
    print("Permision Denied - check if its open somewhere then close it.")
  except Exception as e:
    print(f'Error writing csv: {e}')
    
if __name__ == "__main__":
  books = page()
  write_csv(books)