from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import csv

main_url = 'https://www.scrapethissite.com/pages/forms'

def launchBrowser():
  p = sync_playwright().start()
  browser = p.chromium.launch(headless = False, slow_mo = 70)
  page = browser.new_page()
  
  return p, browser, page

def extractElements(html):
  soup = BeautifulSoup(html, 'lxml')
  mainContainer = soup.find('table', class_='table')
  tBody = mainContainer.find('tbody')
  rows = tBody.find_all('tr', class_='team')
  
  pageData = []
  
  for row in rows:
    data = {
      "teamName": row.find('td', class_='name').text.strip(),
      "teamYear": row.find('td', class_='year').text.strip(),
      "teamWins": row.find('td', class_='wins').text.strip(),
      "teamLosses": row.find('td', class_='losses').text.strip(),
      "winPercent": row.find('td', class_=['pct', 'text-success']).text.strip(),
      "goalsFor": row.find('td', class_='gf').text.strip(),
      "goalsAgainst": row.find('td', class_='ga').text.strip()
    }
    
    pageData.append(data)
    
  return pageData

def getPage(page):
  page.wait_for_selector("ul.pagination")
  html = page.content()
  soup = BeautifulSoup(html, "lxml")
  
  pagination = soup.select("ul.pagination li a")
  page_numbers = []
  for link in pagination:
    if link.text.strip().isdigit():
      page_numbers.append(int(link.text.strip()))
      
  return max(page_numbers) if page_numbers else 1


def pagination():
  all_data = []
  p, browser, page = launchBrowser()
  
  page.goto(main_url)
  totalPage = getPage(page)
  
  print(f"Total page scrapped: {totalPage}")
  
  for pageNum in range(1, totalPage + 1):
    url = f"{main_url}/?page_num={pageNum}"
    print(f"Scrapping page: {pageNum}, {url}")
    
    page.goto(url)
    page.wait_for_selector('table.table')
    time.sleep(1)
    
    html = page.content()
    parsedPage = extractElements(html)
    all_data.extend(parsedPage)
    print(f"Found {len(parsedPage)} teams on page {pageNum}")
    
  browser.close()
  p.stop()
  return all_data

def csvFile(data):
  with open('hockeyTeams.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
  print("Data saved to hockey_teams.csv")
  
if __name__ == "__main__":
  all_data = pagination()
  csvFile(all_data)
    
    