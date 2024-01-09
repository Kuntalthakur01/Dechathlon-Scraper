

# Dechathlon Scraper

This is a scraper built to extract data from the Decathlon page. The app is built by streamlit and currently, this is not deployed online

## Usage

1. Run the file development.py 
```
streamlit run development.py
```      

2. Enter the Url of product page [eg: https://www.decathlon.in/p/8584912/accessories/adult-padel-racket-pr-530-blue-green?id=8584912&type=p ]

3. Wait patiently as the scraper takes time to crawl the data and print out a CSV containing the extracted data.

The CSV includes:

- Product name
- Product price
- Product rating
- sizes (if any)
- List of Reviews

## Requirements

The scraper requires the following packages:

- BeautifulSoup4
- Requests

Install required packages using pip:

```
pip install -r requirements.txt 
```


Let me know if you would like me to explain or expand on any part of this README! I'm happy to update it to include any other relevant information for your repository.
