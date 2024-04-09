from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import logging
import os
import shutil


from PIL import Image

from lib.beautifulsoup import extract_chapter_links
from lib.selenium import extract_chapter_content


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)


def extract_chapters(chapters_path, url):
    '''
    Downloads each chapter under the 'chapters' folder with the pdf
    '''
    chapters = extract_chapter_links(url)
    os.mkdir(chapters_path)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for chapter in chapters:
            chapter_path = Path(chapters_path / f'{chapter.name}')
            os.mkdir(chapter_path)
            futures.append(executor.submit(_extract_chapter, chapter.link, chapter_path, chapter.name, chapters_path))
        for future in futures:
            future.result()


def _extract_chapter(chapter_link, chapter_path, chapter_name, chapters_path):
    pdf_pages = []
    extract_chapter_content(chapter_link, chapter_path)
    image_files = [f for f in os.listdir(chapter_path) if f.endswith('.jpg') or f.endswith('.jpeg')]
    # Bundle the downloaded jpg images into a single pdf file
    for image_file in sorted(image_files, key=lambda x: int(os.path.splitext(x)[0])):
        image = Image.open(Path(chapter_path) / image_file)
        pdf_pages.append(image.convert('RGB'))
    if pdf_pages:
        pdf_pages[0].save(Path(chapters_path) / f'{chapter_name}.pdf', save_all=True, append_images=pdf_pages[1:])
        shutil.rmtree(chapter_path)
    else:
        print(f"No images found in {chapter_path}, skipping PDF creation.")
