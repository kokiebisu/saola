
from pathlib import Path
import os

import sys

from lib.beautifulsoup import extract_manga_cover_img, extract_manga_metadata
from lib.extractor import extract_chapters
from lib.utils import get_desktop_folder, merge_pdfs


def main():
    url = sys.argv[1]
    desktop_path = get_desktop_folder()
    title = extract_manga_metadata(url)
    manga_path = Path(desktop_path / title)
    chapters_path = Path(manga_path / 'chapters')
    os.mkdir(manga_path)
    extract_manga_cover_img(manga_path, url)
    extract_chapters(chapters_path, url)
    merge_pdfs(manga_path, chapters_path, desktop_path, title)


if __name__ == '__main__':
    main()
