import argparse
import os
from pathlib import Path

from lib.beautifulsoup import extract_chapter_links, extract_manga_metadata
from lib.extractor import extract_chapters
from lib.utils import get_desktop_folder


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='Script that extracts the manga chapters and generate pdfs for each.')
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
    chapters_path = Path(manga_path / 'chapters')
    if not os.path.exists(chapters_path):
        os.mkdir(chapters_path)
    chapters = extract_chapter_links(args.url, args.start, args.end)
    while True:
        if extract_chapters(chapters, chapters_path, args.thread):
            break
