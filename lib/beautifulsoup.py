from pathlib import Path
import json
import logging
import os
import requests
import re

from PIL import Image
from bs4 import BeautifulSoup

from lib.image import download_jpg_image


class Chapter:
    def __init__(self, base_url, name, link):
        self.name = name
        self.link = 'https://mangareader.to' + link

    def __str__(self) -> str:
        return json.dumps({
            'name': self.name,
            'link': self.link
        })


def extract_manga_metadata(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find(class_='manga-name-or').text
    except requests.exceptions.HTTPError as e:
        logging.error(f"Error extracting manga title: {e}")
        return None


def extract_manga_cover_img(manga_path, url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    cover_img_url = soup.find(class_='manga-poster-img')['src']
    download_jpg_image(cover_img_url, Path(manga_path / 'cover.jpg'))
    pdf_pages = [Image.open(Path(manga_path / 'cover.jpg'))]
    pdf_pages[0].save(Path(manga_path / 'cover.pdf'), save_all=True, append_images=pdf_pages[1:])
    os.remove(Path(manga_path / 'cover.jpg'))


def extract_chapter_links(url, start, end, language):
    '''
    Extracts all the links to the chapters of the manga from 'start' to 'end', inclusive.
    If only 'start' is provided, it covers from 'start' to the last chapter.
    If only 'end' is provided, it covers from the first to 'end'.
    If both 'start' and 'end' are specified, it covers from 'start' to 'end'.
    If neither is specified, it covers all chapters.
    '''
    try:
        logging.info(f'Extracting Chapter Links for url: {url}')
        chapters = []
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        ul_element = soup.find(id=f'{language}-chapters')
        try:
            all_list_elements = ul_element.find_all('li')
            for li_element in all_list_elements:
                a_element = li_element.find('a')
                if a_element:
                    href_value = a_element['href']
                chapter_name = li_element.find(class_='name').text.split(':')[0]
                numbers = re.findall(r'\d+', chapter_name)
                if numbers:
                    chapter_number = int(numbers[0])
                    if (start is None or chapter_number >= start) and (end is None or chapter_number <= end):
                        chapters.append(Chapter(base_url=url, name=chapter_name, link=href_value))
            return chapters
        except Exception:
            logging.error("The manga is doesn't include the language you specified. Try another one.")
    except Exception as e:
        logging.error(f"Error extracting chapter links: {e}")
        return []
