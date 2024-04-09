from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import re
import shutil
import sys

from PIL import Image
import fitz


from lib.beautifulsoup import extract_chapter_links, extract_manga_metadata
from lib.extractor import extract_chapter_content
from lib.image import download_jpg_image
from lib.utils import get_desktop_folder


def main():
    url = sys.argv[1]
    desktop_path = get_desktop_folder()
    title, cover_img_url = extract_manga_metadata(url)
    manga_path = Path(desktop_path / title)
    os.mkdir(manga_path)
    # Prepares the Cover Image in PDF
    download_jpg_image(cover_img_url, Path(manga_path / 'cover.jpg'))
    pdf_pages = [Image.open(Path(manga_path / 'cover.jpg'))]
    pdf_pages[0].save(Path(manga_path / 'cover.pdf'), save_all=True, append_images=pdf_pages[1:])
    os.remove(Path(manga_path / 'cover.jpg'))

    # Downloads each chapter under the 'chapters' folder with the pdf
    chapters = extract_chapter_links(url)
    chapters_path = Path(manga_path / 'chapters')
    os.mkdir(chapters_path)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for chapter in chapters:
            chapter_path = Path(chapters_path / f'{chapter.name}')
            os.mkdir(chapter_path)
            futures.append(executor.submit(process_chapter, chapter.link, chapter_path, chapter.name, chapters_path))
        for future in futures:
            future.result()

    pdf_output = fitz.open()
    with fitz.open(Path(manga_path / 'cover.pdf')) as cover_pdf:
        pdf_output.insert_pdf(cover_pdf)
    pdf_files = [f for f in os.listdir(chapters_path) if f.endswith('.pdf')]
    for pdf_file in sorted(pdf_files, key=lambda x: int(re.search(r'Chapter (\d+)', x).group(1))):
        with fitz.open(Path(chapters_path / pdf_file)) as pdf:
            pdf_output.insert_pdf(pdf)
    pdf_output.save(Path(desktop_path / f'{title}.pdf'))


def process_chapter(chapter_link, chapter_path, chapter_name, chapters_path):
    pdf_pages = []
    extract_chapter_content(chapter_link, chapter_path)
    image_files = [f for f in os.listdir(chapter_path) if f.endswith('.jpg') or f.endswith('.jpeg')]
    # Bundle the images into a single pdf file
    for image_file in sorted(image_files, key=lambda x: int(os.path.splitext(x)[0])):
        image = Image.open(Path(chapter_path) / image_file)
        pdf_pages.append(image.convert('RGB'))

    if pdf_pages:
        pdf_pages[0].save(Path(chapters_path) / f'{chapter_name}.pdf', save_all=True, append_images=pdf_pages[1:])
        shutil.rmtree(chapter_path)
    else:
        # Handle the case where no images were found
        print(f"No images found in {chapter_path}, skipping PDF creation.")


if __name__ == '__main__':
    main()
