import json
import logging
import os
from urllib.parse import urlparse
import requests
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")


class Chapter:
    def __init__(self, base_url, name, link):
        self.name = name
        self.link = 'https://mangareader.to' + link

    def __str__(self) -> str:
        return json.dumps({
            'name': self.name,
            'link': self.link
        })


def download_image_urls(image_urls, output_dir):
    with ThreadPoolExecutor() as executor:
        for i, url in enumerate(image_urls, start=1):
            logging.info(f'Downloading image for url: {url}')
            executor.submit(partial(_download_image, url, output_dir, i))


def _download_image(url, output_dir, index):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            file_name = f"page_{index}.{os.path.splitext(urlparse(url).path)[1][1:]}"
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, "wb") as file:
                response.raw.decode_content = True
                file.write(response.raw.data)
            logging.info(f"Downloaded: {file_name}")
        else:
            logging.error(f"Failed to download: {url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading {url}: {e}")


def extract_manga_title(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find(class_='manga-name-or').text
    except requests.exceptions.HTTPError as e:
        logging.error(f"Error extracting manga title: {e}")
        return None


def extract_chapter_links(url):
    '''
    Extracts all the links to the chapters of the manga.
    '''
    try:
        logging.info(f'Extracting Chapter Links for url: {url}')
        chapters = []
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        ul_element = soup.find(id='ja-chapters')
        for li_element in ul_element.find_all('li'):
            a_element = li_element.find('a')
            if a_element:
                href_value = a_element['href']
            chapter_name = li_element.find(class_='name').text.split(':')[0]
            chapters.append(Chapter(base_url=url, name=chapter_name, link=href_value))
        return chapters
    except Exception as e:
        logging.error(f"Error extracting chapter links: {e}")
        return []


def extract_chapter_content(url, headless=True):
    '''
    Extracts all the chapter content (images) associated with the chapter.
    Returns the image urls in a list.
    '''
    try:
        logging.info(f'Extracting Chapter Content for url: {url}')
        if headless:
            driver = webdriver.Chrome(options=chrome_options)
        else:
            driver = webdriver.Chrome()

        driver.get(url)
        _allow_reading_content(driver)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".divslide-wrapper")))
        image_urls = _extract_chapter_image_urls(driver)
        driver.quit()
        return image_urls
    except Exception as e:
        logging.error(f"Error extracting chapter content: {e}")
        return []


def _allow_reading_content(driver):
    try:
        # Remove Overlay to interact with the page
        wait = WebDriverWait(driver, 10)
        overlay = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[style*="z-index: 2147483647"]')))
        driver.execute_script("arguments[0].style.display = 'none';", overlay)

        # Click the "Accept All" button from Privacy Modal
        accept_all_button = driver.find_element(
            By.CSS_SELECTOR, ".st-cmp-permanent-footer-nav-buttons .st-button:nth-child(1) .st-text")
        accept_all_button.click()

        # Click the Horizontal Scroll option to start navigating through the content
        enable_horizontal_scroll_button = driver.find_element(
            By.CSS_SELECTOR, "a.rtl-row.mode-item[data-value='horizontal']")
        enable_horizontal_scroll_button.click()
    except Exception as e:
        logging.error(f'_allow_reading_content: {e}')


def _extract_chapter_image_urls(driver):
    try:
        image_urls = []
        element = driver.find_element(By.CSS_SELECTOR, '.divslide-wrapper')
        image_elements = element.find_elements(By.CSS_SELECTOR, '.ds-item')
        for el in image_elements:
            element = el.find_element(By.CSS_SELECTOR, ".ds-image")
            url = element.get_attribute("data-url")
            if url:
                image_urls.append(url)
        return image_urls
    except Exception as e:
        logging.error(f'_extract_chapter_image_urls: {e}')
        return []