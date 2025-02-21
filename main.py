import asyncio
import os
import shutil
import re
import uuid
import aiofiles
from urllib.parse import urlparse, unquote
import argparse
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler


def clean_url(url: str, base_url: str) -> str:
    """Clean URL and return full URL if relative"""
    cleaned_path = clean_path(url, base_url)
    cleaned_url = urljoin(base_url, cleaned_path)
    return cleaned_url


def clean_path(url: str, base_url: str) -> str:
    """Extract and clean the path from URL relative to base URL"""
    # URL decode both URLs to handle any encoded characters
    url = unquote(url)
    base_url = unquote(base_url)

    # Remove base URL to get the relative path
    path = url.replace(base_url, "")

    # If path starts with /, remove it
    path = path.lstrip("/")

    # Handle fragment identifiers (#)
    if "#" in path:
        path = path.split("#")[1]  # Take the fragment part
    else:
        # Remove query parameters if no fragment
        path = path.split("?")[0]

    # If path is empty after cleaning, return empty string
    if not path:
        return ""

    # Normalize .., ., and multiple slashes
    path = os.path.normpath(path)
    # Clean special characters and convert spaces
    clean = re.sub(r"[^\w\s-]", "", path)
    clean = re.sub(r"\s+", "_", clean.strip())
    return clean.lower()


async def process_url(
    url: str, output_dir: str, crawler: AsyncWebCrawler, base_url: str
):
    """Process a single URL and save markdown"""
    internal_links = []
    try:
        result = await crawler.arun(
            url=url, remove_overlay_elements=True, bypass_cache=True
        )

        if result.success:
            # Get title from metadata
            metadata = result.metadata
            title = metadata.get("title", "untitled")
            # Clean title for filename
            clean_title = re.sub(r"[^\w\s-]", "", title)
            clean_title = re.sub(r"\s+", "_", clean_title.strip())

            # Get and clean URL path
            path_suffix = clean_path(url, base_url)

            # Combine title and path for unique filename
            filename = f"{clean_title.lower()}"
            if path_suffix:
                filename += f"_{path_suffix}"
            filename += ".md"

            # Save markdown
            filepath = os.path.join(output_dir, filename)
            async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
                await f.write(result.markdown)

            # Gather internal links
            internal_links = result.links.get("internal", [])
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
    return internal_links


async def crawl_website(url: str, limit: int, output_dir: str):
    """Recursively crawl website and save markdown files"""
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Initialize crawler
        async with AsyncWebCrawler(verbose=False) as crawler:
            processed_urls = set()
            urls_to_process = set([url])
            base_url = url.rstrip("/")

            while urls_to_process and len(processed_urls) < limit:
                current_url = urls_to_process.pop()

                if current_url in processed_urls:
                    continue

                print(
                    f"Crawling ({len(processed_urls)+1}/{len(urls_to_process)}/{limit}): {current_url}"
                )

                # Process URL and get internal links
                internal_links = await process_url(
                    current_url, output_dir, crawler, base_url
                )
                processed_urls.add(current_url)

                # Add new internal links that start with base_url
                for link in internal_links:
                    if isinstance(link, dict):
                        link_url = link.get("href", "")
                    else:
                        link_url = link

                    link_url = clean_url(link_url, base_url)
                    if (
                        link_url
                        and link_url.startswith(base_url)
                        and link_url not in processed_urls
                    ):
                        urls_to_process.add(link_url)

        print("Crawling completed.")

        # Create zip file
        zip_path = f"{output_dir}.zip"
        shutil.make_archive(output_dir, "zip", output_dir)
        print(f"Results have been zipped to {zip_path}")

        # Optionally, remove the output directory after zipping
        shutil.rmtree(output_dir)
        print(f"Temporary output directory '{output_dir}' has been removed.")

    except Exception as e:
        print(f"Crawl failed: {str(e)}")


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Web Crawling CLI Tool")
    parser.add_argument("url", help="Base URL to crawl (e.g., https://example.com)")
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of pages to crawl (default: 10)",
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Directory to save crawl results (default: output)",
    )
    return parser.parse_args()


async def main():
    args = parse_arguments()
    base_url = args.url.rstrip("/")

    # Validate URL
    parsed_url = urlparse(base_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        print("Invalid URL provided. Please include the scheme (e.g., https://).")
        return

    # Create a unique output directory based on UUID
    job_id = uuid.uuid4().hex
    output_dir = os.path.join(args.output, f"crawl_{job_id}")

    await crawl_website(base_url, args.limit, output_dir)


if __name__ == "__main__":
    asyncio.run(main())
