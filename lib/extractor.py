from pathlib import Path
import json
import logging
import base64
import time
import requests

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

class Chapter:
    def __init__(self, base_url, name, link):
        self.name = name
        self.link = 'https://mangareader.to' + link

    def __str__(self) -> str:
        return json.dumps({
            'name': self.name,
            'link': self.link
        })


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


def extract_chapter_content(url, chapter_path):
    '''
    Extracts all the chapter content (images) associated with the chapter.
    Returns the image urls in a list.
    '''
    logging.info(f'Extracting Chapter Content for url: {url}')
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")
    chrome_options.add_experimental_option("mobileEmulation", {"deviceName": "Nexus 5"})

    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.set_window_size(390, 844)

        driver.get(url)
        _allow_reading_content(driver)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.container-reader-chapter")))
        _scroll_down_page(driver)
        _download_images(driver, chapter_path)
    except Exception as e:
        logging.error(f"Error extracting chapter content: {e}")
    finally:
        driver.quit()


def _scroll_down_page(driver):
    SECONDS_TO_SCROLL = 30
    start_time = time.time()
    while time.time() - start_time < SECONDS_TO_SCROLL:
        driver.execute_script("window.scrollBy(0, 200);")
        time.sleep(0.5)


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
            By.CSS_SELECTOR, "a.rtl-row.mode-item[data-value='vertical']")
        enable_horizontal_scroll_button.click()
    except Exception as e:
        logging.error(f'_allow_reading_content: {e}')


def _download_images(driver, chapter_path):
    try:
        iv_card_elements = driver.find_elements(By.CSS_SELECTOR, '.iv-card')

        for i, card in enumerate(iv_card_elements):
            img_elements = card.find_elements(By.CSS_SELECTOR, 'img.image-vertical')
            if img_elements:
                is_shuffled = 'shuffled' in card.get_attribute('class')
                img_element = img_elements[0]  # Assuming there's always only one img element of interest per card
                image_url = img_element.get_attribute("src")
                output_path = Path(chapter_path / f"{i + 1}.jpg")

                if is_shuffled:
                    # Process for shuffled
                    base64_image_data = _fetch_blob_as_base64(driver, image_url)
                    _save_base64_image(base64_image_data, output_path)
                else:
                    # Process for non-shuffled
                    _download_jpg_image(image_url, output_path)
    except Exception as e:
        logging.error(f'_download_images: {e}')
        return []


def _download_jpg_image(image_url, output_path):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(output_path, "wb") as file:
                response.raw.decode_content = True
                file.write(response.raw.data)
            logging.info(f"Downloaded image to path: {output_path}")
        else:
            logging.error(f"Failed to download: {url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading to path: {output_path} due to {e}")

def _fetch_blob_as_base64(driver, blob_url):
    js_script = f'''
    var callback = arguments[arguments.length - 1];
    fetch("{blob_url}")
        .then(response => response.blob())
        .then(blob => {{
            var reader = new FileReader();
            reader.readAsDataURL(blob); 
            reader.onloadend = function() {{
                var base64data = reader.result;                
                callback(base64data);
            }}
        }});
    '''
    return driver.execute_async_script(js_script)


def _save_base64_image(base64_data, file_name):
    _, encoded = base64_data.split(",", 1)
    data = base64.b64decode(encoded)
    with open(file_name, "wb") as file:
        file.write(data)
