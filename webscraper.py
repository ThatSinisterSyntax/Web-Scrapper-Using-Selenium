import os
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pdfkit

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set path to chromedriver as per your configuration
webdriver_service = Service('C:\\Chromedriver\\chromedriver-win64\\chromedriver.exe')  # Change this to your chromedriver path. You need to download and install the latest one. Google it.

def remove_duplicates(l, links, base_domain):  # Remove duplicates and add URLs to the list
    for item in l:
        match = re.search(r"(?P<url>https?://[^\s]+)", item)  # Use raw string
        if match is not None:
            url = match.group("url")
            defragmented_url, _ = urldefrag(url)  # Remove fragment
            if base_domain in defragmented_url and defragmented_url not in links:
                links.add(defragmented_url)

def scrape_links(driver, links, visited, base_domain, limit=162):
    if len(links) >= limit:
        return
    
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        data = [urljoin(driver.current_url, str(link.get('href'))) for link in soup.find_all('a', href=True)]
        remove_duplicates(data, links, base_domain)

    except Exception as e:
        print(f"Error scraping {driver.current_url}: {e}")

def convert_urls_to_pdfs(urls, output_dir):
    path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Update this path
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    for url in urls:
        try:
            print(f"Converting URL to PDF: {url}")
            parsed_url = urlparse(url)
            filename = parsed_url.path.strip('/').replace('/', '_') or 'index'
            filename = re.sub(r'[^a-zA-Z0-9_]', '', filename)
            output_path = os.path.join(output_dir, f"{filename}.pdf")
            pdfkit.from_url(url, output_path, configuration=config)
            print(f"Saved PDF: {output_path}")
        except Exception as e:
            print(f"Error converting {url} to PDF: {e}")

def scrape_all_pages(starting_url, total_pages, links, visited, base_domain, limit=162):
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    driver.get(starting_url)

    for page_num in range(1, total_pages + 1):
        print(f"Scraping page {page_num}")
        scrape_links(driver, links, visited, base_domain, limit)
        try:
            next_button = driver.find_element(By.LINK_TEXT, 'Next »')
            if next_button:
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)  # TDD: Add delay to allow page to load
            else:
                break
        except Exception as e:
            print(f"Error navigating to page {page_num}: {e}")
            break

    driver.quit()

# scraper
starting_url = 'https://josefkjaergaard.com/'
parsed_url = urlparse(starting_url)
base_domain = parsed_url.netloc

links = set()
visited = set()
total_pages = 43  # TDD: Set this to the number of pages you want to scrape

scrape_all_pages(starting_url, total_pages, links, visited, base_domain)

# TDD: Directory to save PDFs, if the dir doesnt exist the program will create it. The pdf will be saved in it.
output_directory = 'pdf'
os.makedirs(output_directory, exist_ok=True)

convert_urls_to_pdfs(links, output_directory)
