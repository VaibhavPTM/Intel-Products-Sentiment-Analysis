import requests
import pandas as pd
from bs4 import BeautifulSoup
from googletrans import Translator

reviewlist = []

headers = {
    'authority': 'www.flipkart.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9,bn;q=0.8',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}

def totalPages(productUrl):
    resp = requests.get(productUrl, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Find the element containing the number of reviews
    review_element = soup.find_all('div', class_='row j-aW8Z')
    
    if not review_element:
        return 0  # In case the element is not found, return 0 pages
    
    reviews_text = review_element[1].find('span').text
    pages = int(reviews_text.replace("Reviews","").replace(" ",""))
    t = (pages // 10) + (1 if (pages % 10 > 0) else 0)
    return t

def extractReviews(reviewUrl):
    # Initialize the Translator
    translator = Translator()
    resp = requests.get(reviewUrl, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')

    # productTitle
    productname_tag = soup.find('a', class_='wjcEIp AbG6iz')
    productname = productname_tag.text if productname_tag else "Unknown Product"

    # Review Title
    review_titles = []
    # Rating
    ratings = []
    # Review Body
    comments = []

    title = soup.find_all('p', class_='z9E0IG')
    for t in title:
        review_titles.append(t.get_text())
    
    rat = soup.find_all('div', class_='XQDdHH Ga3i8K')
    for r in rat:
        rating = r.get_text()
        if rating:
            ratings.append(rating)
        else:
            ratings.append('0')

    cmt = soup.find_all('div', class_='ZmyHeo')
    for c in cmt:
        comment_text = c.div.div.get_text(strip=True)
        comments.append(comment_text)

    for title, rating, comment in zip(review_titles, ratings, comments):
        translated_review_title = title
        try:
            translated_review_title = translator.translate(title, dest='en').text
        except:
            pass
        
        translated_review_comment = comment
        try:
            translated_review_comment = translator.translate(comment, dest='en').text
        except:
            pass

        review = {
            'productTitle': productname,
            'Review Title': translated_review_title,
            'Rating': rating,
            'Review Body': translated_review_comment
        }
        reviewlist.append(review)

def main():
    with open('Flipkart_i3_url.txt', 'r') as file:
        productUrls = file.readlines()
    for productUrl in productUrls:
        try:
            totalPg = totalPages(productUrl)
            print(totalPg)
            for i in range(totalPg):
                try :
                    tmp = productUrl + str(i + 1)
                    extractReviews(tmp)
                except:
                    pass
        except:
            pass
        
    df = pd.DataFrame(reviewlist)
    df.to_excel('Flipkart_i3_reviews.xlsx', index=False)

if __name__ == "__main__":
    main()
