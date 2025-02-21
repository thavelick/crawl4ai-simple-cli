# Crawl4AI Simple CLI

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
![Version](https://img.shields.io/badge/version-0.1.0-green.svg)

## Overview

**Crawl4AI Simple CLI** is a lightweight command-line tool that leverages the power of the [Crawl4AI](https://github.com/unclecode/crawl4ai) library to asynchronously crawl websites. It extracts content from web pages, converts them into Markdown files, and packages the results into a ZIP archive for easy access and distribution.

Whether you're looking to archive a website, perform content analysis, or generate documentation, this CLI tool provides a straightforward and efficient solution.

## Get Started
1. Clone the repository
```bash
git clone https://github.com/thavelick/crawl4ai-simple-cli.git && cd crawl4ai-simple-cli
uv run main.py https://example.com
```
## Usage

uv run main.py `<URL>` [--limit `<LIMIT>`] [--output `<OUTPUT>`]

- `<URL>`: The base URL of the website you want to crawl (e.g., `https://example.com`).

### Options

- `--limit`: Set the maximum number of pages to crawl. Default is `10`.
- `--output`: Specify the directory to save crawl results. Default is `output`.
- `--help`: Display the help message and exit.

## Output

After the crawl is completed, the tool performs the following:

1. **Markdown Files:**
   - Each crawled page is saved as a `.md` file in the specified output directory.
   - Filenames are generated based on the page title and URL path for easy identification.

2. **ZIP Archive:**
   - The entire output directory is compressed into a `.zip` file for convenient storage and transfer.
