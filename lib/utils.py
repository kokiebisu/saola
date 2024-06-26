from pathlib import Path
import os
import re

import fitz


def merge_pdfs(manga_path, chapters_path, desktop_path, title):
    '''
    Merges all the pdf files that were generated including cover.pdf and the chapter.pdfs.
    '''
    pdf_output = fitz.open()
    with fitz.open(Path(manga_path / 'cover.pdf')) as cover_pdf:
        pdf_output.insert_pdf(cover_pdf)
    pdf_files = [f for f in os.listdir(chapters_path) if f.endswith('.pdf')]
    for pdf_file in sorted(pdf_files, key=lambda x: int(re.search(r'Chapter (\d+)', x).group(1))):
        with fitz.open(Path(chapters_path / pdf_file)) as pdf:
            pdf_output.insert_pdf(pdf)
    pdf_output.save(Path(desktop_path / f'{title}.pdf'))


def read_base_path():
    return Path(os.environ.get('OUTPUT_PATH'))
