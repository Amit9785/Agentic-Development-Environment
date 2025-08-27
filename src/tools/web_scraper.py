from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse, quote_plus
import time
from typing import Dict, List, Optional

class IntelligentWebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def get_weather_data(self, city: str) -> str:
        """Scrape weather information for a specific city"""
        try:
            # Try multiple weather sources
            urls = [
                f"https://www.google.com/search?q=weather+{quote_plus(city)}",
                f"https://www.weather.com/weather/today/l/{quote_plus(city)}",
                f"https://openweathermap.org/find?q={quote_plus(city)}"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract temperature and weather info
                    weather_info = []
                    
                    # Look for temperature patterns
                    temp_patterns = [
                        r'(\d+)°[CF]',
                        r'Temperature:?\s*(\d+)',
                        r'(\d+)\s*degrees'
                    ]
                    
                    text = soup.get_text()
                    for pattern in temp_patterns:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        if matches:
                            weather_info.extend([f"Temperature: {match}°" for match in matches[:3]])
                    
                    # Look for weather conditions
                    weather_keywords = ['sunny', 'cloudy', 'rainy', 'clear', 'overcast', 'storm', 'snow']
                    for keyword in weather_keywords:
                        if keyword.lower() in text.lower():
                            weather_info.append(f"Condition: {keyword.title()}")
                            break
                    
                    if weather_info:
                        return f"🌤️ Weather in {city}:\n" + "\n".join(weather_info[:5])
                        
                except Exception:
                    continue
            
            return f"🌤️ Weather for {city}:\nCouldn't fetch specific data. Please check:\n• https://weather.com/search/results?where={quote_plus(city)}\n• https://www.google.com/search?q=weather+{quote_plus(city)}"
            
        except Exception as e:
            return f"Error fetching weather: {str(e)}"
    
    def get_news_data(self, topic: str) -> str:
        """Scrape news information about a topic"""
        try:
            urls = [
                f"https://www.google.com/search?q={quote_plus(topic)}+news",
                f"https://news.google.com/search?q={quote_plus(topic)}"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract news headlines
                    headlines = []
                    
                    # Common news headline selectors
                    selectors = [
                        'h3', 'h2', '.headline', '.title', '[data-testid="headline"]'
                    ]
                    
                    for selector in selectors:
                        elements = soup.select(selector)
                        for element in elements[:5]:
                            text = element.get_text().strip()
                            if len(text) > 20 and topic.lower() in text.lower():
                                headlines.append(text)
                    
                    if headlines:
                        return f"📰 Latest news about {topic}:\n" + "\n".join([f"• {h}" for h in headlines[:5]])
                        
                except Exception:
                    continue
                    
            return f"📰 News about {topic}:\nCouldn't fetch specific headlines. Check:\n• https://news.google.com/search?q={quote_plus(topic)}\n• https://www.google.com/search?q={quote_plus(topic)}+news"
            
        except Exception as e:
            return f"Error fetching news: {str(e)}"
    
    def get_general_info(self, query: str) -> str:
        """Scrape general information about a query"""
        try:
            # Try to get Wikipedia info first
            wiki_url = f"https://en.wikipedia.org/wiki/{quote_plus(query)}"
            
            try:
                response = self.session.get(wiki_url, timeout=8)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Get the first paragraph
                    first_para = soup.find('p')
                    if first_para:
                        text = first_para.get_text().strip()
                        if len(text) > 100:
                            return f"📚 Information about {query}:\n{text[:500]}...\n\nSource: Wikipedia"
            except:
                pass
            
            # Fallback to Google search
            google_url = f"https://www.google.com/search?q={quote_plus(query)}"
            
            try:
                response = self.session.get(google_url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for knowledge panel or featured snippets
                snippets = []
                
                # Common Google snippet selectors
                selectors = [
                    '.BNeawe', '.hgKElc', '.st', '.VwiC3b'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    for element in elements[:3]:
                        text = element.get_text().strip()
                        if len(text) > 50 and len(text) < 300:
                            snippets.append(text)
                
                if snippets:
                    return f"🔍 Information about {query}:\n" + "\n\n".join(snippets[:2])
                    
            except:
                pass
                
            return f"🔍 Search for {query}:\nCouldn't extract specific information. Try:\n• https://www.google.com/search?q={quote_plus(query)}\n• https://en.wikipedia.org/wiki/{quote_plus(query)}"
            
        except Exception as e:
            return f"Error fetching information: {str(e)}"

# Global scraper instance
scraper = IntelligentWebScraper()

@tool("Smart Web Scraper")
def smart_web_scraper(query: str) -> str:
    """
    Intelligently browse and scrape web content based on the query.
    Automatically detects query type (weather, news, general info) and scrapes accordingly.
    
    Args:
        query: The search query (e.g., "Jaipur weather", "Bitcoin news", "Einstein biography")
    
    Returns:
        Scraped and formatted information relevant to the query
    """
    try:
        query_lower = query.lower()
        
        # Detect query type and route to appropriate scraping method
        
        # Weather queries
        if any(word in query_lower for word in ['weather', 'temperature', 'forecast', 'climate']):
            # Extract city name
            city = query_lower
            for word in ['weather', 'temperature', 'forecast', 'climate', 'of', 'in', 'today', 'current']:
                city = city.replace(word, '')
            city = city.strip()
            
            if not city:
                city = "current location"
            
            return scraper.get_weather_data(city)
        
        # News queries
        elif any(word in query_lower for word in ['news', 'latest', 'recent', 'breaking', 'current events']):
            topic = query_lower
            for word in ['news', 'latest', 'recent', 'breaking', 'current events']:
                topic = topic.replace(word, '')
            topic = topic.strip()
            
            if not topic:
                topic = "general news"
                
            return scraper.get_news_data(topic)
        
        # Price/financial queries
        elif any(word in query_lower for word in ['price', 'cost', 'value', 'stock', 'crypto', 'bitcoin']):
            return scraper.get_general_info(query) + "\n\n💡 For real-time prices, check financial websites like Yahoo Finance or CoinGecko"
        
        # General information queries
        else:
            return scraper.get_general_info(query)
            
    except Exception as e:
        return f"❌ Error in smart web scraping: {str(e)}\n\n🌐 Manual search: https://www.google.com/search?q={quote_plus(query)}"

@tool("Targeted Web Scraper")
def targeted_web_scraper(url: str, target_info: str = "main content") -> str:
    """
    Scrape specific information from a given URL.
    
    Args:
        url: The URL to scrape
        target_info: What type of information to extract (e.g., "main content", "headlines", "prices")
    
    Returns:
        Extracted information from the webpage
    """
    try:
        response = scraper.session.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        results = []
        
        if "headline" in target_info.lower():
            # Extract headlines
            headlines = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for h in headlines[:10]:
                text = h.get_text().strip()
                if len(text) > 10:
                    results.append(f"📰 {text}")
        
        elif "price" in target_info.lower():
            # Look for price patterns
            text = soup.get_text()
            price_patterns = [
                r'\$[\d,]+\.?\d*',
                r'₹[\d,]+\.?\d*',
                r'€[\d,]+\.?\d*',
                r'£[\d,]+\.?\d*'
            ]
            
            for pattern in price_patterns:
                prices = re.findall(pattern, text)
                for price in prices[:5]:
                    results.append(f"💰 {price}")
        
        else:
            # Extract main content
            # Try to find main content areas
            content_selectors = [
                'main', 'article', '.content', '#content', '.post', '.entry-content'
            ]
            
            content_found = False
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements[:2]:
                        text = element.get_text().strip()
                        if len(text) > 100:
                            # Clean and truncate text
                            text = re.sub(r'\s+', ' ', text)
                            results.append(text[:1000] + "..." if len(text) > 1000 else text)
                            content_found = True
                            break
                if content_found:
                    break
            
            # Fallback: get paragraphs
            if not content_found:
                paragraphs = soup.find_all('p')
                for p in paragraphs[:5]:
                    text = p.get_text().strip()
                    if len(text) > 50:
                        results.append(text)
        
        if results:
            return f"🌐 Content from {url}:\n\n" + "\n\n".join(results)
        else:
            return f"🌐 Content from {url}:\n\nCouldn't extract specific information. The page might use dynamic content or have access restrictions."
            
    except requests.exceptions.RequestException as e:
        return f"❌ Error accessing {url}: {str(e)}"
    except Exception as e:
        return f"❌ Error scraping {url}: {str(e)}"
