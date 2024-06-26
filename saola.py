
from pathlib import Path
import argparse
import os

from lib.beautifulsoup import extract_chapter_links, extract_manga_cover_img, extract_manga_metadata
from lib.extractor import extract_chapters
from lib.utils import read_base_path, merge_pdfs


if __name__ == '__main__':
    '''
    Script that combines compile.py and scrape.py to generate a single pdf based on the manga url provided
    '''
    parser = argparse.ArgumentParser(description="Script to extract manga chapters and merge them into a single pdf")
    parser.add_argument('-u', '--url', help='manga url which you want to extract/generate the pdf', required=True)
    parser.add_argument('-t', '--thread', type=int,
                        help='number of threads you want to use to process', default=1)
    parser.add_argument('-s', '--start', type=int,
                        help='starting chapter within the range you want to extract', required=False)
    parser.add_argument('-e', '--end', type=int,
                        help='last chapter within the range you want to extract', required=False)
    parser.add_argument('-l', '--language', type=str, choices=['ja', 'en', 'sp'],
                        help='language option: ja (Japanese), en (English), sp (Spanish)',
                        default='ja')
    args = parser.parse_args()

    base_path = read_base_path()
    title = extract_manga_metadata(args.url)
    manga_path = Path(base_path / title)
    if not os.path.exists(manga_path):
        os.makedirs(manga_path)
    extract_manga_cover_img(manga_path, args.url)
    chapters_path = Path(manga_path / 'chapters')
    if not os.path.exists(chapters_path):
        os.mkdir(chapters_path)
    chapters = extract_chapter_links(args.url, args.start, args.end, args.language)
    while True:
        if extract_chapters(chapters, chapters_path, args.thread):
            break
    merge_pdfs(manga_path, chapters_path, base_path, title)
