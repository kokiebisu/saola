
from pathlib import Path
import os

from lib.beautifulsoup import extract_chapter_links, extract_manga_cover_img, extract_manga_metadata
from lib.extractor import extract_chapters
from lib.utils import get_desktop_folder, merge_pdfs


def main():
    url = sys.argv[1]
    desktop_path = get_desktop_folder()
    title = extract_manga_metadata(url)
    manga_path = Path(desktop_path / title)
    if not os.path.exists(manga_path):
        os.mkdir(manga_path)
    extract_manga_cover_img(manga_path, url)
    chapters_path = Path(manga_path / 'chapters')
    if not os.path.exists(chapters_path):
        os.mkdir(chapters_path)
    chapters = extract_chapter_links(args.url, args.start, args.end)
    while True:
        if extract_chapters(chapters_path, args.url, args.thread, args.start, args.end):
            break
    merge_pdfs(manga_path, chapters_path, desktop_path, title)


if __name__ == '__main__':
    main()
