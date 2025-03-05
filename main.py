import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def get_amazon_reviews_selenium(asin):
    """
    Opens Chrome, navigates to the Amazon review page for the given ASIN,
    waits for manual login if necessary, then scrapes the loaded reviews.
    Follows 'Next page' links until no more are found.
    """

    # 1) (Optional) Configure Chrome to reuse your local user profile 
    # so you stay logged in automatically. 
    # Set 'user-data-dir' to your actual path (the example below is Windows).
    # WARNING: DO NOT share user-data-dir with multiple Chrome processes simultaneously!
    # Make sure Chrome is closed before you run this so you don't corrupt your profile.
    options = webdriver.ChromeOptions()
    # options.add_argument(r"user-data-dir=C:\Users\<YourUserName>\AppData\Local\Google\Chrome\User Data")

    # 2) Create a Chrome driver instance
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    # 3) Go to the Amazon reviews page for the given ASIN
    # Add query parameters to ensure we get all_reviews & pageNumber=1
    start_url = f"https://www.amazon.com/product-reviews/{asin}/?reviewerType=all_reviews&pageNumber=1"
    driver.get(start_url)

    # Give you time to log in if Amazon forces it, or to pass any captcha checks
    # This is purely optional. If you're already logged in via user-data-dir, it may not be necessary.
    print("Waiting 15 seconds so you can log in or handle any captchas (if needed)...")
    time.sleep(60)

    all_reviews = []
    page_number = 1

    while True:
        print(f"Scraping page {page_number}...")

        # 4) Locate the review blocks in the rendered HTML
        review_blocks = driver.find_elements(By.CSS_SELECTOR, 'div[data-hook="review"]')
        
        if not review_blocks:
            print("No more reviews found or the page is not loaded. Stopping.")
            break

        # 5) Extract data from each review block
        for block in review_blocks:
            try:
                title = block.find_element(By.CSS_SELECTOR, '[data-hook="review-title"]').text
            except:
                title = None

            try:
                rating_full = block.find_element(By.CSS_SELECTOR, '[data-hook="review-star-rating"] span').text
                # Usually "5.0 out of 5 stars"
                rating = rating_full.split()[0]
            except:
                rating = None

            try:
                author = block.find_element(By.CSS_SELECTOR, '.a-profile-name').text
            except:
                author = None

            try:
                date = block.find_element(By.CSS_SELECTOR, '[data-hook="review-date"]').text
            except:
                date = None

            try:
                text = block.find_element(By.CSS_SELECTOR, '[data-hook="review-body"]').text
            except:
                text = None

            all_reviews.append({
                "title": title,
                "rating": rating,
                "author": author,
                "date": date,
                "text": text
            })

        # 6) Check if there's a Next page
        try:
            next_page = driver.find_element(By.CSS_SELECTOR, 'li.a-last a')
            next_page.click()
            page_number += 1
            time.sleep(3)  # short pause to let next page load
        except:
            print("No more pages found.")
            break

    # 7) Close the browser
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
