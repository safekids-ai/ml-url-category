import sys
import requests
from bs4 import BeautifulSoup

def fetch_meta_description_title_and_rating(url):
    # User-Agent string for Chrome browser
    headers = {
        'User-Agent': 'curl/7.68.0', # Mimicking a common curl version's User-Agent
        'Accept': '*/*', # Accepting all content types
    }
#    headers = {
#        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
#    }
    try:
        response = requests.get(url, headers=headers)
        # Ensure the request was successful
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the title
        title_tag = soup.find('title')
        title = title_tag.string if title_tag else 'No title found'

        #print(response.text)
        
        # Find the meta description
        meta_description_tag = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_description_tag['content'] if meta_description_tag else 'No meta description found'
        
        # Find the meta rating
        meta_rating_tag = soup.find('meta', attrs={'name': 'rating'})
        meta_rating = meta_rating_tag['content'] if meta_rating_tag else 'No rating found'
        
        return title, meta_description, meta_rating
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None, None, None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        title, meta_description, meta_rating = fetch_meta_description_title_and_rating(url)
        print(f"Title: {title}")
        print(f"Meta Description: {meta_description}")
        print(f"Rating: {meta_rating}")
    else:
        print("Please provide a URL as an argument.")
