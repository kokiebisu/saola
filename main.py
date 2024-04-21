
from pathlib import Path
import argparse
import os

from lib.beautifulsoup import extract_chapter_links, extract_manga_cover_img, extract_manga_metadata
from lib.extractor import extract_chapters
from lib.utils import get_desktop_folder, merge_pdfs


if __name__ == '__main__':
    '''
    Script that combines combine.py and extract.py to generate a single pdf based on the manga url provided
    '''
    parser = argparse.ArgumentParser(description="Script to extract manga chapters and merge them into a single pdf")
    parser.add_argument('--url', help='the url which you want to extract')
    parser.add_argument('--thread', metavar='N', type=int,
                        help='the number of threads', default=4)
    parser.add_argument('--start', metavar='N', type=int,
                        help='the chapter you want to start extracting')
    parser.add_argument('--end', metavar='N', type=int,
                        help='the chapter you want to start extracting until')
    args = parser.parse_args()

    desktop_path = get_desktop_folder()
    title = extract_manga_metadata(args.url)
    manga_path = Path(desktop_path / title)
    if not os.path.exists(manga_path):
        os.mkdir(manga_path)
    extract_manga_cover_img(manga_path, args.url)
    chapters_path = Path(manga_path / 'chapters')
    if not os.path.exists(chapters_path):
        os.mkdir(chapters_path)
    chapters = extract_chapter_links(args.url, args.start, args.end)
    while True:
        if extract_chapters(chapters_path, args.url, args.thread, args.start, args.end):
            break
    merge_pdfs(manga_path, chapters_path, desktop_path, title)
