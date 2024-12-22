from pathlib import Path
import logging
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


from lib.image import download_base64_image, download_jpg_image


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)


def extract_chapter_content(url, chapter_path):
    '''
    Extracts all the chapter content (images) associated with the chapter.
    Returns the image urls in a list.
    '''
    logging.info(f'Extracting Chapter Content for url: {url}')
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    options.add_argument("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")
    options.add_experimental_option("mobileEmulation", {"deviceName": "Nexus 5"})

    try:
        logging.info('Setting up driver...')
        driver = webdriver.Remote(
            command_executor='http://selenium-chrome:4444/wd/hub',
            options=options
        )
        driver.set_window_size(390, 844)
        logging.info('Fetching URL...')
        driver.get(url)
        _enable_vertical_scroll(driver)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.container-reader-chapter")))
        _load_all_images(driver)
        _download_images(driver, chapter_path)
    except Exception as e:
        logging.error(f"Error extracting chapter content: {e}")
    finally:
        driver.quit()

def _load_all_images(driver):
    logging.info('Page initially loaded..')
    num_images = len(driver.find_elements(By.CSS_SELECTOR, "div.container-reader-chapter > div"))
    i = 0
    while i < num_images:
        current_element = driver.find_elements(By.CSS_SELECTOR, "div.container-reader-chapter > div")[i]
        if not current_element.find_elements(By.TAG_NAME, "img"):
            time.sleep(2)
            continue
        else:
            _scroll_down_page(driver, i+1)
            i = i + 1

def _scroll_down_page(driver, i):
    logging.info(f'Scrolling to page {i}...')
    driver.execute_script("window.scrollBy(0, 615);")
    time.sleep(0.5)


def _enable_vertical_scroll(driver, max_retries=3):
    logging.basicConfig(level=logging.INFO)
    logging.info('Enabling vertical scroll... ')

    attempt = 0
    while attempt < max_retries:
        try:
            wait = WebDriverWait(driver, 10)  # Adjust wait time as necessary for your needs

            # Remove Overlay
            overlay = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[style*="z-index: 2147483647"]')))
            driver.execute_script("arguments[0].style.display = 'none';", overlay)

            # TODO: Seems like this may not be needed anymore
            # Accept Privacy Policy
            # accept_all_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".st-cmp-permanent-footer-nav-buttons .st-button:nth-child(1) .st-text")))
            # accept_all_button.click()

            # Enable Vertical Scroll
            enable_vertical_scroll_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.rtl-row.mode-item[data-value='vertical']")))
            enable_vertical_scroll_button.click()

            break

        except Exception as e:
            attempt += 1
            logging.error(f'Attempt {attempt} failed: {e}')
            if attempt == max_retries:
                logging.error("Max retries reached. Exiting.")
                break
            else:
                logging.info(f"Retrying... Attempt {attempt+1}/{max_retries}")
                time.sleep(5)


def _download_images(driver, chapter_path):
    logging.info('Downloading the loaded images...')
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
                    base64_image_data = _fetch_blob_as_base64(driver, image_url)
                    download_base64_image(base64_image_data, output_path)
                else:
                    download_jpg_image(image_url, output_path)
    except Exception as e:
        logging.error(f'__download_images: {e}')
        return []


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
