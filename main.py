import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys

def get_all_amazon_reviews(asin):
    """
    Scrapes ALL reviews from a single ASIN on Amazon.com
    by following the 'Next page' links until no more pages are found.
    Returns a list of dictionaries, each containing one review.
    """
    # Start with a query string to ensure we get all reviews and the first page.
    # Example: https://www.amazon.com/product-reviews/B0C2CKT9VR/?reviewerType=all_reviews&pageNumber=1
    current_page_url = f"https://www.amazon.com/product-reviews/{asin}/?reviewerType=all_reviews&pageNumber=1"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    all_reviews = []
    page_number = 1

    while True:
        print(f"Scraping page {page_number}...")
        response = requests.get(current_page_url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to retrieve page {page_number}. Status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        review_blocks = soup.find_all("div", {"data-hook": "review"})

        # Debugging tip: Uncomment the following line to see how many reviews are found each page:
        # print(f"Found {len(review_blocks)} reviews on page {page_number}")

        if not review_blocks:
            # If 0 reviews found on this page, assume no more reviews exist
            print("No more reviews found. Stopping.")
            break

        # Extract the review data from each block
        for block in review_blocks:
            # Review title
            title_tag = block.find("a", {"data-hook": "review-title"})
            review_title = title_tag.get_text(strip=True) if title_tag else None

            # Rating (e.g., "5.0 out of 5 stars")
            rating_tag = block.find("i", {"data-hook": "review-star-rating"})
            if rating_tag and rating_tag.find("span"):
                rating_str = rating_tag.find("span").get_text(strip=True)
                review_rating = rating_str.split()[0]
            else:
                review_rating = None

            # Author
            author_tag = block.find("span", {"class": "a-profile-name"})
            review_author = author_tag.get_text(strip=True) if author_tag else None

            # Date
            date_tag = block.find("span", {"data-hook": "review-date"})
            review_date = date_tag.get_text(strip=True) if date_tag else None

            # Review text
            body_tag = block.find("span", {"data-hook": "review-body"})
            review_text = body_tag.get_text(strip=True) if body_tag else None

            all_reviews.append({
                "title": review_title,
                "rating": review_rating,
                "author": review_author,
                "date": review_date,
                "text": review_text
            })

        # Look for the next-page link with class "a-last"
        next_page_tag = soup.find("li", {"class": "a-last"})
        if next_page_tag and next_page_tag.find("a"):
            next_page_url = "https://www.amazon.com" + next_page_tag.find("a")["href"]
            current_page_url = next_page_url
            page_number += 1
            # Delay to help avoid potential rate-limiting
            time.sleep(2)
        else:
            print("No more pages found.")
            break

    return all_reviews

def main():
    # Prompt user for the ASIN
    asin = input("Please enter the ASIN (e.g., B0C2CKT9VR): ").strip()
    if not asin:
        print("No ASIN provided. Exiting.")
        sys.exit(1)

    # Scrape reviews for the provided ASIN
    all_reviews = get_all_amazon_reviews(asin)
    print(f"Total reviews scraped: {len(all_reviews)}")

    if len(all_reviews) == 0:
        print("No reviews scraped. Exiting.")
        sys.exit(0)

    # Save reviews to an Excel file
    df = pd.DataFrame(all_reviews)
    output_filename = "amazon_reviews.xlsx"
    df.to_excel(output_filename, index=False)
    print(f"Reviews have been saved to {output_filename}")

if __name__ == "__main__":
    main()
