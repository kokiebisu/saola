# saola 🦌

## Project Overview

Pronounced sow-la, this project automates the collection of manga from [mangareader.to](https://mangareader.to/) and compiles the chapters into a single PDF file. Designed to streamline the manga reading experience, it simplifies access to offline manga content. By entering a manga URL, users can automatically download all chapters of the manga, which are then merged into a PDF and saved on the user's desktop.

## Features

- Automated Downloading: Fetches manga chapters directly from the provided URL.
  PDF Compilation: Combines all chapters into a single, easily shareable PDF file.
- Metadata Extraction: Retrieves and utilizes manga metadata, such as titles and cover images, for organized storage and file naming.
- User-Friendly: Saves the final PDF on the desktop for easy access, neatly organized within a folder named after the manga title.

### How It Works

- Setup: The script prepares a folder structure on the user's desktop, organizing downloads by manga title and chapters.
- Scraping: Utilizes custom functions to scrape manga metadata and chapter content from the specified URL.
- Compilation: Downloads are merged into a single PDF, preserving the order of the manga chapters.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Docker**: You need Docker installed on your system to build and run the containers. Download and install Docker from [Docker's official site](https://www.docker.com/get-started).

## Setup

To get a local copy up and running follow these simple steps:

1. **Clone the repository**
   ```bash
   git clone https://github.com/kokiebisu/saola.git
   cd saola
   ```
2. **Build the Docker environment**

   ```bash
   make run-clean-container
   ```

   This command builds the Docker images and starts the containers in the background. Once the containers are up, one will be in a 'waiting' mode, ready for commands to be executed.

### Use Cases

1. You want to extract the manga into a folder and then merge it into a pdf.

```bash
usage: docker-compose exec script python saola.py [-h] [-u URL] [-t N] [-s N] [-e N] [-l S]
```

Example:

```bash
# Indicates you want to download the manga at https://mangareader.to/one-piece-3 with 8 threads and start from chapter 12 till 256. The langauge should be japanese.
usage: make saola OPTIONS="-u https://mangareader.to/one-piece-3 -t 8 -s 12 -e 256 -l ja"
```

Wait for the process to complete. The script will start by creating a directory for the manga on your desktop, then proceed to download each chapter and finally compile them into a PDF. The final PDF will be saved on your desktop, within a folder named after the manga title.

You can also run other scripts in case you want to just

2. Scrapes the manga into a folder (skip the merging into a single pdf)

```bash
usage: make scrape OPTIONS="[-h] [-u URL] [-t N] [-s N] [-e N] [-l S]"
```

3. You have the extracted manga already inside a folder and just want to merge it into a single pdf

```bash
usage: make compile OPTIONS="[-h] [-u URL]"
```

The following are all the options you can pass to the script:

```bash
options:
  -h, --help  show this help message and exit
  -u --url URL   the url which you want to extract (Required)
  -t --thread N  the number of threads (Optional: Default 1)
  -s --start N   the chapter you want to extract from (Optional)
  -e --end N     the chapter you want to extract until (Optional)
  -l --language S the language of the manga you want to scrape (Option: Default to 'ja')
```

### Customization

If you want to customize configurations (like specifying where the folder should be created), you can do so by creating `settings.json` and by filling in the properties you want to update.
You can see an example at `settings.example.jsonc`.

### Notes

Ensure that the URL you provide is a valid "mangareader.to" manga page.
Download times may vary based on the number of threads being used, chapters and your internet speed.
The script is designed for personal use and respects the copyright of manga creators. Please use it responsibly.
