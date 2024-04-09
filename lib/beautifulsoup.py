import json
import logging
import requests

from bs4 import BeautifulSoup


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
        return soup.find(class_='manga-name-or').text, soup.find(class_='manga-poster-img')['src']
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
