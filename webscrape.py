# webscrape.py
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ScrapedData:
    website_name: str
    scraped_at: datetime
    paragraphs: list
    total_words: int

def extract_content(url: str) -> ScrapedData:
    """
    Scrape the content from the given URL and return a ScrapedData object.
    
    Args:
        url (str): The URL to scrape.
        
    Returns:
        ScrapedData: An object containing scraped data.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        scraped_at = datetime.now()
        paragraphs = [para.get_text() for para in soup.find_all('p')]
        total_words = sum(len(para.split()) for para in paragraphs)
        
        scraped_data = ScrapedData(
            website_name=url,
            scraped_at=scraped_at,
            paragraphs=paragraphs,
            total_words=total_words
        )
        
        return scraped_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None
