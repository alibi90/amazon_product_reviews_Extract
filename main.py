import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def get_amazon_reviews_selenium(asin):
    """
    Opens Chrome, navigates to the Amazon review page for the given ASIN,
    waits for manual login if necessary, then scrapes the loaded reviews
    by targeting the HTML structure you provided.
    Follows 'Next page' links until no more are found.
    """

    options = webdriver.ChromeOptions()
    # If you want to reuse your logged-in Chrome profile, uncomment & set your path:
    options.add_argument(r"user-data-dir=C:\Users\Home-MSI\AppData\Local\Google\Chrome\User Data")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    # Start at page 1, forcing all reviews
    start_url = (
        f"https://www.amazon.com/product-reviews/{asin}/"
        f"?reviewerType=all_reviews&pageNumber=1"
    )
    driver.get(start_url)

    # Give yourself time to manually log in if needed
    print("Waiting 15 seconds to log in or pass any captchas if needed...")
    time.sleep(15)

    all_reviews = []
    page_number = 1

    while True:
        print(f"Scraping page {page_number}...")

        # Identify each "review block" container. 
        # Amazon usually uses data-hook="review" or .a-section.review
        # If you're certain each is data-hook="review", use that:
        review_blocks = driver.find_elements(By.CSS_SELECTOR, "div[data-hook='review']")
        # If that doesn't find anything, try the known container classes:
        # review_blocks = driver.find_elements(By.CSS_SELECTOR, ".a-section.review.aok-relative")

        if not review_blocks:
            print("No review blocks found. Stopping.")
            break

        for block in review_blocks:
            try:
                # 1) Reviewer Name
                reviewer_name = block.find_element(By.CSS_SELECTOR, "span.a-profile-name").text
            except:
                reviewer_name = None

            try:
                # 2) Review Title (child <span> inside <a.review-title ...>)
                # The parent has classes: a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold
                # The actual text is in a child <span> with no class
                title_element = block.find_element(By.CSS_SELECTOR, "a.review-title span")
                review_title = title_element.text
            except:
                review_title = None

            try:
                # 3) Rating (the <span> with class "a-icon-alt": e.g. "5.0 out of 5 stars")
                # Parent i tag has classes: "a-icon a-icon-star a-star-5 review-rating"
                rating_full = block.find_element(By.CSS_SELECTOR, "span.a-icon-alt").text
                # Typically "5.0 out of 5 stars"
                review_rating = rating_full.split()[0] if rating_full else None
            except:
                review_rating = None

            try:
                # 4) Review Date (the <span> with classes "a-size-base a-color-secondary review-date")
                date_element = block.find_element(By.CSS_SELECTOR, "span.review-date")
                review_date = date_element.text
            except:
                review_date = None

            try:
                # 5) Review Text
                # The parent <span> has classes: a-size-base review-text review-text-content
                # Inside it is a child <span> (no class) that holds the actual text
                # But often .text on the parent is enough:
                text_parent = block.find_element(By.CSS_SELECTOR, "span.a-size-base.review-text.review-text-content")
                review_text = text_parent.text
            except:
                review_text = None

            # Store in a list of dicts
            all_reviews.append({
                "reviewer_name": reviewer_name,
                "title": review_title,
                "rating": review_rating,
                "date": review_date,
                "text": review_text,
            })

        # Find & click "Next" to go to subsequent pages of reviews
        try:
            next_page_link = driver.find_element(By.CSS_SELECTOR, "li.a-last a")
            next_page_link.click()
            page_number += 1
            time.sleep(3)  # Pause to let the page load
        except:
            print("No more pages found.")
            break

    driver.quit()
    return all_reviews

def main():
    asin = input("Enter Amazon ASIN (e.g. B0C2CKT9VR): ").strip()
    if not asin:
        print("No ASIN provided. Exiting.")
        return

    reviews = get_amazon_reviews_selenium(asin)
    print(f"Total reviews scraped: {len(reviews)}")

    if reviews:
        df = pd.DataFrame(reviews)
        df.to_excel("amazon_reviews.xlsx", index=False)
        print("Saved to amazon_reviews.xlsx")
    else:
        print("No reviews found.")

if __name__ == "__main__":
    main()
