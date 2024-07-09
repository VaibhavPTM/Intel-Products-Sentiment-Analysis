import requests
import pandas as pd
from bs4 import BeautifulSoup
from googletrans import Translator

import random
reviewlist = []

headers = {
    'authority': 'www.amazon.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9,bn;q=0.8',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}

def totalPages(productUrl):
    resp = requests.get(productUrl, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    reviews = soup.find('div', {'data-hook':"cr-filter-info-review-rating-count"})
    return int(reviews.text.strip().split(', ')[1].split(" ")[0])

def extractReviews(reviewUrl):
    # Initialize the Translator
    translator = Translator()
    resp = requests.get(reviewUrl, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    reviews = soup.findAll('div', {'data-hook': "review"})
    for item in reviews:
        try:
            product_title = soup.title.text.replace("Amazon.in:Customer reviews: ", "").strip()
                
            review_title_element = item.find('a', {'data-hook': "review-title"})
            if not review_title_element:
                review_title_element = item.find('span', {'data-hook': "review-title"})
                
            review_title = review_title_element.text.strip() if review_title_element else 'No Title'
            review_title = review_title.split('\n')[1].strip() if '\n' in review_title else review_title
                
            # Translate the review title to English if it's not in English
            try :
                translated_review_title = translator.translate(review_title, dest='en').text
            except:
                pass
            rating_element = item.find('i', {'data-hook': 'review-star-rating'})
            if not rating_element:
                rating_element = item.find('i', {'data-hook': 'cmps-review-star-rating'})
                
            rating = rating_element.text.strip() if rating_element else 'No Rating'
                
            review_body_element = item.find('span', {'data-hook': 'review-body'})
            review_body = review_body_element.text.strip() if review_body_element else 'No Review Body'
                
                # Translate the review body to English if it's not in English
            try:
                translated_review_body = translator.translate(review_body, dest='en').text
            except:
                pass

            review = {
                'productTitle': product_title,
                'Review Title': translated_review_title,
                'Rating': rating,
                'Review Body': translated_review_body,
            }
            reviewlist.append(review)
        except :
            print("Something went wrong...")

def main():
    with open('Amazon_i3_url.txt', 'r') as file:
        productUrls = file.readlines()
    I = 1
    for productUrl in productUrls:
        # productUrl = "https://www.amazon.co.uk/Intel%C2%AE-CoreTM-i9-12900F-Desktop-Processor/dp/B09MDFH5HY/ref=sr_1_1_sspa"
        reviewUrl = productUrl.replace("dp", "product-reviews") + "?pageNumber=" + str(1)
        totalPg = totalPages(reviewUrl)
        # print(productUrl)
        print("New link >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> " + str(I) + " -> " + str(totalPg))
        for i in range((totalPg//10) + (1 if totalPg % 10 != 0 else 0)):
            print(f"Running for page {i+1}")
            reviewUrl = productUrl.replace("dp", "product-reviews") + "?pageNumber=" + str(i+1)
            extractReviews(reviewUrl)
        
        I = I+1

    df = pd.DataFrame(reviewlist)
    df.to_excel('Amazon_i3_Newdataset.xlsx', index=False)

main()