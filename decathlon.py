# Import necessary libraries
import time
import csv
import streamlit as st
from selenium.webdriver.chrome.options import Options
from chromedriver_autoinstaller import install
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from io import StringIO
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver


# Function to scrape Decathlon product with Selenium
# def install_chromedriver():
#     install()
def scrape_decathlon_product_with_selenium(url):
    
    #install_chromedriver()
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    
    # Use ChromeDriverManager to get the path to the ChromeDriver executable
    chromedriver_path = ChromeDriverManager(version="97.0.4692.71").install()

    # Initialize the WebDriver with the specified options and executable path
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)



    #driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    

    # Check if running on Streamlit Sharing
    is_streamlit_sharing = "IS_STREAMLIT_SHARING" in st.secrets

    if not is_streamlit_sharing:
        # If not on Streamlit Sharing, use webdriver_manager
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    else:
        # If on Streamlit Sharing, use the system installed ChromeDriver
        driver = webdriver.Chrome(options=chrome_options)
   
    # Initialize csv_writer outside the try block
    try:
        # Open the webpage
        driver.get(url)
        csv_writer = None
        csv_data = None

        # Wait for the JavaScript to load content (adjust the timeout as needed)
        wait = WebDriverWait(driver, 10)

        # Extract product name
        product_name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#__next > div:nth-child(6) > div.ProductMainContent_productMainContent__lTUZh > div.rightContentWidth.bg-grey-50.md\:bg-white.md\:\!sticky.md\:\!h-full.z-20.basis-0.max-w-full.md\:max-w-\[40\%\].md\:pt-\[45px\].md\:pr-\[20px\].md\:pl-\[16px\].md\:top-\[50px\].grow > div.bg-white.rounded.p-4.md\:p-0.md\:rounded-0.md\:bg-none.text-14 > h1'))).text.strip()

        # Extract price using XPath
        price = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[1]/div[2]/div[2]/div/div[1]/div[2]/div/span').text.strip()

        # Extract additional information with the given class
        rating_element = wait.until(EC.presence_of_element_located((By.XPATH, '//p[@class="ml-1 text-12 lg:text-16 font-normal cn-586"]')))
        product_rating = rating_element.text.strip()

        try:
            sizes_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#size-select-container > div')))
            sizes = [size.text.strip() for size in sizes_elements]
        except TimeoutException:
            sizes = ["N/A"]  # or any default value to indicate no sizes found

        # Press the "Reviews" button
        reviews_button = driver.find_element(By.XPATH, '//*[@id="product-review-tab-button"]')
        reviews_button.click()

        # Increase the timeout for the "VIEW ALL REVIEWS" button
        view_all_reviews_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "VIEW ALL REVIEWS")]')))

        # Click the "VIEW ALL REVIEWS" button
        view_all_reviews_button.click()

        # Introduce a delay (e.g., 5 seconds)
        time.sleep(2)

        # Scroll to bottom to load more reviews until no new reviews are loaded
        last_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")

        reviews_texts = []  # To store reviews during scraping

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(15)  # Add a short delay to allow new reviews to load

            new_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")

            # Collect reviews text during scrolling
            reviews_boxes = driver.find_elements(By.XPATH, '//*[@id="__next"]/section/div/div/div/div[2]/div[2]/div[1]/div[1]/div/div/div')
            for box in reviews_boxes:
                reviews_text_elements = box.find_elements(By.XPATH, '//*[@id="review-body-text"]')
                for review_text_element in reviews_text_elements:
                    reviews_texts.append(review_text_element.text.strip())

            # Update progress text dynamically
            st.text(f"Scraped {len(reviews_texts)} reviews so far...")

            if new_height == last_height:
                break  # Break the loop if no new reviews are loaded
            else:
                last_height = new_height

        # Wait for the reviews section to load
        reviews_boxes = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/section/div/div/div/div[2]/div[2]/div[1]/div[1]/div/div/div')))

        # Save product details and reviews to BytesIO instead of a file
        buffer = StringIO()
        csv_writer = csv.writer(buffer)
        headers = ['Product Name', 'Price', 'Product Rating', 'Sizes', 'Review']
        #encoded_headers = [h.encode('utf-8') for h in headers]
        csv_writer.writerow(headers)

        for box in reviews_boxes:
            reviews_text_elements = box.find_elements(By.XPATH, '//*[@id="review-body-text"]')
            for review_text_element in reviews_text_elements:
                review_text = review_text_element.text.strip()

                
                product_name_str = product_name
                price_str = price
                product_rating_str = product_rating
                sizes_str = ', '.join(sizes)
                review_str = review_text

                
                # Write product details and each review as a separate row
                csv_writer.writerow([product_name_str, price_str, product_rating_str, sizes_str, review_str])

        # Move the buffer position to the beginning before reading
        buffer.seek(0)

        return buffer.getvalue()
    finally:
        # Close the webdriver
        driver.quit()

# Import libraries
import streamlit as st

st.set_page_config(page_title="Decathlon Reviews Scraper", page_icon="🛒") 

st.header("Decathlon Reviews Scraper")

with st.expander("About this app", expanded=True):
     st.write("""
         This app lets you scrape customer reviews for any product on Decathlon's website. 
         Simply enter the product URL and hit Scrape Reviews to get started!
     """)

# User input 
with st.form("scraper"):
    st.write("Enter the product URL:") 
    product_url = st.text_input("Enter Decathlon Product URL:", placeholder="https://www.decathlon.in/p/")
    submitted = st.form_submit_button("Scrape Reviews")

if submitted:

    with st.spinner("Scraping reviews..."):
        # Call selenium scraper
        csv_data = scrape_decathlon_product_with_selenium(product_url)  

    st.success("Reviews scraped successfully!")

    st.download_button(
        label='Download CSV',
        data=csv_data,
        file_name='reviews.csv'
    )

else:
    st.info("Enter a product URL above to start scraping reviews")