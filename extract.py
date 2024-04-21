import argparse
import os
from pathlib import Path

from lib.beautifulsoup import extract_chapter_links, extract_manga_metadata
from lib.extractor import extract_chapters
from lib.utils import get_desktop_folder


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script that extracts the manga chapters and generate pdfs for each.')
    parser.add_argument('-u', '--url', help='manga url which you want to extract')
    parser.add_argument('-t', '--thread', type=int,
                        help='number of threads you want to use to process', default=4)
    parser.add_argument('-s', '--start', type=int,
                        help='starting chapter within the range you want to extract')
    parser.add_argument('-e', '--end', type=int,
                        help='last chapter within the range you want to extract')
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
