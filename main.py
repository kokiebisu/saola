from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import re
import shutil
import sys

from PIL import Image
import fitz

from lib.extractor import extract_chapter_content, extract_chapter_links, extract_manga_title
from lib.utils import get_desktop_folder


def main():
    url = sys.argv[1]
    desktop_path = get_desktop_folder()
    title = extract_manga_title(url)
    manga_path = Path(desktop_path / title)
    os.mkdir(manga_path)
    chapters = extract_chapter_links(url)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        for chapter in chapters:
            chapter_path = Path(manga_path / f'{chapter.name}')
            os.mkdir(chapter_path)
            futures.append(executor.submit(process_chapter, chapter.link, chapter_path, manga_path, chapter.name))
        for future in futures:
            future.result()

    pdf_output = fitz.open()
    pdf_files = [f for f in os.listdir(manga_path) if f.endswith('.pdf')]
    for pdf_file in sorted(pdf_files, key=lambda x: int(re.search(r'Chapter (\d+)', x).group(1))):
        with fitz.open(Path(manga_path / pdf_file)) as pdf:
            pdf_output.insert_pdf(pdf)
    pdf_output.save(Path(desktop_path / f'{title}.pdf'))


def process_chapter(chapter_link, chapter_path, manga_path, chapter_name):
    pdf_pages = []
    extract_chapter_content(chapter_link, chapter_path)
    image_files = [f for f in os.listdir(chapter_path) if f.endswith('.jpg') or f.endswith('.jpeg')]
    # # Bundle the images into a single pdf file
    for image_file in sorted(image_files, key=lambda x: int(os.path.splitext(x)[0])):
        image = Image.open(Path(chapter_path / image_file))
        pdf_pages.append(image)
    pdf_pages[0].save(Path(manga_path / f'{chapter_name}.pdf'), save_all=True, append_images=pdf_pages[1:])
    shutil.rmtree(chapter_path)


if __name__ == '__main__':
    main()
