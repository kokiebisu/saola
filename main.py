import os
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor
from lib.extractor import download_image_urls, extract_chapter_content, extract_chapter_links, extract_manga_title
from lib.utils import get_desktop_folder


def main():
    # url = sys.argv[1]
    # url = 'https://mangareader.to/kingdom-10'
    url = 'https://mangareader.to/i-was-told-to-relinquish-my-fiance-to-my-little-sister-and-the-greatest-dragon-took-a-liking-to-me-and-unbelievably-took-over-the-kingdom-10695'
    desktop_path = get_desktop_folder()
    title = extract_manga_title(url)
    manga_path = Path(desktop_path / title)
    os.mkdir(manga_path)
    chapters = extract_chapter_links(url)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for chapter in chapters:
            chapter_path = Path(manga_path / f'{chapter.name}')
            os.mkdir(chapter_path)
            futures.append(executor.submit(process_chapter, chapter.link, chapter_path))

        for future in futures:
            future.result()


def process_chapter(chapter_link, chapter_path):
    image_urls = extract_chapter_content(chapter_link)
    download_image_urls(output_dir=chapter_path, image_urls=image_urls)
    time.sleep(5)


if __name__ == '__main__':
    main()