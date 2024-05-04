import argparse
import os
from pathlib import Path

from lib.beautifulsoup import extract_manga_cover_img, extract_manga_metadata
from lib.utils import get_desktop_folder, merge_pdfs

if __name__ == '__main__':
    '''
    A script that compiles the manga folder into a single pdf
    '''
    parser = argparse.ArgumentParser(description='Script that combines all the chapter pdfs into a single pdf.')
    parser.add_argument('-u', '--url', help='manga url which you want to generate the pdf')
    args = parser.parse_args()
    desktop_path = get_desktop_folder()
    title = extract_manga_metadata(args.url)
    manga_path = Path(desktop_path / title)
    if not os.path.exists(manga_path):
        os.mkdir(manga_path)
    extract_manga_cover_img(manga_path, args.url)
    chapters_path = Path(manga_path / 'chapters')
    if not os.path.exists(chapters_path):
        raise f"The chapters path doesn't exist for {title}"
    merge_pdfs(manga_path, chapters_path, desktop_path, title)
