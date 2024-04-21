# saola (Pseudoryx nghetinhensis) 🦌

## Project Overview

Pronounced sow-la, this project automates the collection of manga from "mangareader.to" and compiles the chapters into a single PDF file. Designed to streamline the manga reading experience, it simplifies access to offline manga content. By entering a manga URL, users can automatically download all chapters of the manga, which are then merged into a PDF and saved on the user's desktop.

## Features

- Automated Downloading: Fetches manga chapters directly from the provided URL.
  PDF Compilation: Combines all chapters into a single, easily shareable PDF file.
- Metadata Extraction: Retrieves and utilizes manga metadata, such as titles and cover images, for organized storage and file naming.
- User-Friendly: Saves the final PDF on the desktop for easy access, neatly organized within a folder named after the manga title.

### How It Works

- Setup: The script prepares a folder structure on the user's desktop, organizing downloads by manga title and chapters.
- Scraping: Utilizes custom functions to scrape manga metadata and chapter content from the specified URL.
- Compilation: Downloads are merged into a single PDF, preserving the order and integrity of the manga chapters.

## Usage

This project is designed to be straightforward and user-friendly, enabling users to quickly download manga from "mangareader.to" and compile it into a single PDF. Follow these steps to use the script:

### Prerequisites

Ensure you have Python installed on your system. This script is compatible with Python 3.x. Additionally, you will need to install a few Python libraries. You can install these dependencies by running:

```bash
pip install -r requirements.txt
```

Running the Script
Open your terminal or command prompt. Navigate to the directory where the script is located.

Run the script with a manga URL as an argument. Replace <manga_url> with the actual URL of the manga you wish to download and compile:

```bash
usage: main.py [-h] [--url URL] [--thread N] [--start N] [--end N]

options:
  -h, --help  show this help message and exit
  --url URL   the url which you want to extract
  --thread N  the number of threads
  --start N   the chapter you want to start extracting
  --end N     the chapter you want to start extracting until
```

Example:

```bash
python main.py --url https://mangareader.to/some-manga-title
```

Wait for the process to complete. The script will start by creating a directory for the manga on your desktop, then proceed to download each chapter and finally compile them into a PDF. The final PDF will be saved on your desktop, within a folder named after the manga title.

### Notes

Ensure that the URL you provide is a valid "mangareader.to" manga page.
Download times may vary based on the number of chapters and your internet speed.
The script is designed for personal use and respects the copyright of manga creators. Please use it responsibly.
