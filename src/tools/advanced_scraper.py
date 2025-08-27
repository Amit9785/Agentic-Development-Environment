from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus
import json
import time
import os
from typing import Dict, List, Optional, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

class IntelligentUniversalScraper:
    """Universal web scraper that uses LLM to intelligently analyze queries and scrape accordingly"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        # Initialize LLM lazily (only when needed)
        self.analysis_llm = None
    
    def _get_analysis_llm(self):
        """Lazy initialization of LLM"""
        if self.analysis_llm is None:
            try:
                self.analysis_llm = ChatGoogleGenerativeAI(
                    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                    temperature=0.1,  # Low temperature for consistent analysis
                    google_api_key=os.getenv("GOOGLE_API_KEY")
                )
            except Exception as e:
                # If LLM fails, we'll use fallback analysis
                self.analysis_llm = "error"
                return None
        return self.analysis_llm if self.analysis_llm != "error" else None
    
    def analyze_query_with_llm(self, query: str) -> Dict[str, any]:
        """Use LLM to analyze the query and determine optimal scraping strategy"""
        analysis_prompt = f"""
Analyze this user query and provide a JSON response for optimal web scraping:

Query: "{query}"

Analyze and respond with this exact JSON format:
{{
    "query_type": "weather|news|price|stock|sports|definition|general|specific_site",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "target_sites": ["site1.com", "site2.com"],
    "search_terms": "optimized search query",
    "data_to_extract": ["temperature", "condition", "price", "title", etc.],
    "scraping_method": "google_search|specific_site|api_call|multi_source"
}}

Examples:
- Weather query → "query_type": "weather", "target_sites": ["weather.com", "accuweather.com"]
- Stock price → "query_type": "price", "target_sites": ["yahoo.com", "google.com"]
- News → "query_type": "news", "target_sites": ["google.com", "bing.com"]
- General info → "query_type": "general", "scraping_method": "google_search"
        """
        
        # Get LLM with lazy initialization
        llm = self._get_analysis_llm()
        
        if llm:
            try:
                response = llm.invoke([HumanMessage(content=analysis_prompt)])
                analysis_text = response.content
                
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                    return analysis
                else:
                    # Fallback analysis
                    return self._fallback_analysis(query)
                    
            except Exception as e:
                # Fallback for LLM errors
                return self._fallback_analysis(query, str(e))
        else:
            # No LLM available, use fallback analysis
            return self._fallback_analysis(query)
    
    def _fallback_analysis(self, query: str, error: str = None) -> Dict[str, any]:
        """Fallback query analysis when LLM is not available"""
        query_lower = query.lower()
        
        # Simple rule-based analysis
        if any(word in query_lower for word in ['weather', 'temperature', 'forecast', 'rain', 'sunny']):
            query_type = "weather"
        elif any(word in query_lower for word in ['news', 'headlines', 'breaking', 'latest']):
            query_type = "news"
        elif any(word in query_lower for word in ['price', 'cost', 'stock', 'bitcoin', 'crypto']):
            query_type = "price"
        elif any(word in query_lower for word in ['score', 'game', 'match', 'sports', 'football']):
            query_type = "sports"
        else:
            query_type = "general"
        
        result = {
            "query_type": query_type,
            "keywords": query.split()[:3],
            "search_terms": query,
            "scraping_method": "google_search"
        }
        
        if error:
            result["error"] = error
            
        return result
    
    def universal_scrape(self, query: str) -> str:
        """Universal scraping method that handles any type of query"""
        # Step 1: Analyze query with LLM
        analysis = self.analyze_query_with_llm(query)
        
        # Step 2: Route to appropriate scraping method based on analysis
        query_type = analysis.get("query_type", "general")
        scraping_method = analysis.get("scraping_method", "google_search")
        
        results = []
        results.append(f"🔍 **Query Analysis:** {analysis.get('query_type', 'general').title()}")
        
        try:
            if query_type == "weather":
                weather_results = self._scrape_weather(analysis)
                results.extend(weather_results)
            
            elif query_type == "price" or query_type == "stock":
                price_results = self._scrape_prices(analysis)
                results.extend(price_results)
            
            elif query_type == "news":
                news_results = self._scrape_news(analysis)
                results.extend(news_results)
            
            elif query_type == "sports":
                sports_results = self._scrape_sports(analysis)
                results.extend(sports_results)
                
            else:
                # General scraping for any other type
                general_results = self._scrape_general(analysis)
                results.extend(general_results)
        
        except Exception as e:
            results.append(f"❌ Scraping error: {str(e)}")
        
        # Step 3: Format and return results
        if len(results) > 1:
            header = f"🌐 **Universal Scraper Results for:** '{query}'\n" + "="*70
            return header + "\n\n" + "\n\n".join(results)
        else:
            return f"🌐 No specific results found for '{query}'.\n\n🔗 Manual search: https://www.google.com/search?q={quote_plus(query)}"
    
    def _scrape_weather(self, analysis: Dict) -> List[str]:
        """Specialized weather scraping"""
        search_terms = analysis.get("search_terms", "")
        keywords = analysis.get("keywords", [])
        
        # Extract city from keywords
        city = next((k for k in keywords if k not in ['weather', 'temperature', 'forecast']), "current location")
        
        results = []
        
        # Multiple weather sources
        weather_sources = [
            (f"https://www.google.com/search?q=weather+{quote_plus(city)}", "Google Weather"),
            (f"https://weather.com/search/results?where={quote_plus(city)}", "Weather.com"),
            (f"https://www.accuweather.com/en/search-locations?query={quote_plus(city)}", "AccuWeather")
        ]
        
        for url, source in weather_sources:
            try:
                response = self.session.get(url, timeout=8)
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Look for temperature
                temp_patterns = [r'(\d+)°[CF]', r'(\d+)\s*degrees', r'(\d+)°']
                temps = []
                for pattern in temp_patterns:
                    temps.extend(re.findall(pattern, text))
                
                # Look for conditions
                condition_patterns = [r'(sunny|cloudy|rainy|clear|overcast|stormy|snow)', r'(partly cloudy|mostly cloudy)']
                conditions = []
                for pattern in condition_patterns:
                    conditions.extend(re.findall(pattern, text, re.IGNORECASE))
                
                if temps or conditions:
                    result = f"🌤️ {source}:"
                    if temps:
                        result += f" {temps[0]}°"
                    if conditions:
                        result += f" {conditions[0].title()}"
                    results.append(result)
                    
            except:
                continue
                
        return results if results else [f"🌤️ Weather data not available. Try: https://weather.com/search/results?where={quote_plus(city)}"]
    
    def _scrape_prices(self, analysis: Dict) -> List[str]:
        """Specialized price/stock scraping"""
        search_terms = analysis.get("search_terms", "")
        
        results = []
        
        # Try multiple financial sources
        price_sources = [
            (f"https://www.google.com/search?q={quote_plus(search_terms)}+price", "Google Finance"),
            (f"https://finance.yahoo.com/search?p={quote_plus(search_terms)}", "Yahoo Finance"),
        ]
        
        for url, source in price_sources:
            try:
                response = self.session.get(url, timeout=8)
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Look for price patterns
                price_patterns = [r'\$([\d,]+\.?\d*)', r'₹([\d,]+\.?\d*)', r'€([\d,]+\.?\d*)']
                
                for pattern in price_patterns:
                    prices = re.findall(pattern, text)
                    if prices:
                        currency = '$' if '$' in pattern else '₹' if '₹' in pattern else '€'
                        results.append(f"💰 {source}: {currency}{prices[0]}")
                        break
                        
            except:
                continue
        
        return results if results else [f"💰 Price data not available. Try: https://finance.yahoo.com/search?p={quote_plus(search_terms)}"]
    
    def _scrape_news(self, analysis: Dict) -> List[str]:
        """Specialized news scraping"""
        search_terms = analysis.get("search_terms", "")
        
        results = []
        
        # Try news sources
        news_sources = [
            (f"https://www.google.com/search?q={quote_plus(search_terms)}+news&tbm=nws", "Google News"),
            (f"https://www.bing.com/news/search?q={quote_plus(search_terms)}", "Bing News")
        ]
        
        for url, source in news_sources:
            try:
                response = self.session.get(url, timeout=8)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for news headlines
                headline_selectors = ['h3', 'h2', '.title', '.headline']
                
                for selector in headline_selectors:
                    headlines = soup.select(selector)
                    for headline in headlines[:3]:
                        text = headline.get_text().strip()
                        if len(text) > 20 and len(text) < 150:
                            results.append(f"📰 {text}")
                            break
                    if results:
                        break
                        
            except:
                continue
        
        return results if results else [f"📰 News not available. Try: https://news.google.com/search?q={quote_plus(search_terms)}"]
    
    def _scrape_sports(self, analysis: Dict) -> List[str]:
        """Specialized sports scraping"""
        search_terms = analysis.get("search_terms", "")
        
        results = []
        
        try:
            url = f"https://www.google.com/search?q={quote_plus(search_terms)}+score+live"
            response = self.session.get(url, timeout=8)
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            
            # Look for scores
            score_patterns = [r'(\d+)\s*-\s*(\d+)', r'(\d+):(\d+)']
            for pattern in score_patterns:
                scores = re.findall(pattern, text)
                if scores:
                    results.append(f"⚽ Score: {scores[0][0]}-{scores[0][1]}")
                    break
                    
        except:
            pass
        
        return results if results else [f"⚽ Sports data not available. Try: https://www.google.com/search?q={quote_plus(search_terms)}"]
    
    def _scrape_general(self, analysis: Dict) -> List[str]:
        """General purpose scraping for any topic"""
        search_terms = analysis.get("search_terms", "")
        
        results = []
        
        # Multi-source general search
        search_sources = [
            (f"https://www.google.com/search?q={quote_plus(search_terms)}", "Google"),
            (f"https://www.bing.com/search?q={quote_plus(search_terms)}", "Bing"),
            (f"https://api.duckduckgo.com/?q={quote_plus(search_terms)}&format=json&no_html=1", "DuckDuckGo")
        ]
        
        for url, source in search_sources:
            try:
                if "duckduckgo" in url:
                    # DuckDuckGo API
                    response = self.session.get(url, timeout=8)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("Answer"):
                            results.append(f"🦆 {source}: {data['Answer']}")
                        elif data.get("Abstract"):
                            abstract = data["Abstract"]
                            if len(abstract) > 50:
                                results.append(f"📖 {source}: {abstract[:300]}...")
                else:
                    # Regular web scraping
                    response = self.session.get(url, timeout=8)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for featured snippets and answer boxes
                    snippet_selectors = ['.hgKElc', '.BNeawe', '.VwiC3b', '.b_ans']
                    
                    for selector in snippet_selectors:
                        elements = soup.select(selector)
                        for elem in elements[:2]:
                            text = elem.get_text().strip()
                            if len(text) > 50 and len(text) < 400:
                                results.append(f"💡 {source}: {text}")
                                break
                        if results:
                            break
                            
            except:
                continue
                
            # Don't overload with results
            if len(results) >= 3:
                break
        
        return results if results else [f"🌐 Information not found. Try: https://www.google.com/search?q={quote_plus(search_terms)}"]
    
    def get_weather_from_multiple_sources(self, city: str) -> str:
        """Get weather from multiple reliable sources"""
        results = []
        
        # Method 1: Try Weather.com
        try:
            weather_data = self._get_weather_com_data(city)
            if weather_data:
                results.append(weather_data)
        except:
            pass
        
        # Method 2: Try Google Weather
        try:
            google_weather = self._get_google_weather(city)
            if google_weather:
                results.append(google_weather)
        except:
            pass
        
        # Method 3: Try OpenWeatherMap public data
        try:
            owm_data = self._get_openweather_data(city)
            if owm_data:
                results.append(owm_data)
        except:
            pass
        
        # Method 4: Try AccuWeather
        try:
            accu_data = self._get_accuweather_data(city)
            if accu_data:
                results.append(accu_data)
        except:
            pass
        
        if results:
            # Combine results from multiple sources
            combined_result = f"🌤️ Weather in {city} (Real-time data):\n" + "\n".join(results)
            return combined_result
        else:
            return f"🌤️ Weather in {city}:\n❌ Unable to fetch real-time data from weather services.\n\n🌐 Try checking:\n• https://weather.com/search/results?where={quote_plus(city)}\n• https://www.google.com/search?q=weather+{quote_plus(city)}\n• https://openweathermap.org/find?q={quote_plus(city)}"
    
    def _get_weather_com_data(self, city: str) -> str:
        """Scrape weather.com for accurate weather data"""
        try:
            # Search for the city first
            search_url = f"https://weather.com/search/results?where={quote_plus(city)}"
            response = self.session.get(search_url, timeout=10)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for temperature
            temp_selectors = [
                '.CurrentConditions--tempValue--MHmYY',
                '[data-testid="TemperatureValue"]',
                '.today_nowcard-temp',
                '.current-temperature'
            ]
            
            temperature = None
            for selector in temp_selectors:
                temp_elem = soup.select_one(selector)
                if temp_elem:
                    temperature = temp_elem.get_text().strip()
                    break
            
            # Look for condition
            condition_selectors = [
                '.CurrentConditions--phraseValue--mZC_p',
                '[data-testid="wxPhrase"]',
                '.today_nowcard-phrase',
                '.current-condition'
            ]
            
            condition = None
            for selector in condition_selectors:
                cond_elem = soup.select_one(selector)
                if cond_elem:
                    condition = cond_elem.get_text().strip()
                    break
            
            if temperature or condition:
                result = "📊 Weather.com:"
                if temperature:
                    result += f" Temperature: {temperature}"
                if condition:
                    result += f" Condition: {condition}"
                return result
            
        except Exception as e:
            pass
        
        return None
    
    def _get_google_weather(self, city: str) -> str:
        """Get weather from Google search results"""
        try:
            search_url = f"https://www.google.com/search?q=weather+{quote_plus(city)}"
            response = self.session.get(search_url, timeout=10)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            
            # Look for temperature patterns in the text
            temp_patterns = [
                r'(\d+)°[CF]',
                r'(\d+)\s*degrees',
                r'Temperature[:\s]*(\d+)',
                r'(\d+)°'
            ]
            
            temperatures = []
            for pattern in temp_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                temperatures.extend(matches)
            
            # Look for weather conditions
            weather_conditions = []
            condition_patterns = [
                r'(sunny|cloudy|rainy|stormy|clear|overcast|drizzle|thunderstorm|snow|fog|mist|hazy)',
                r'(partly cloudy|mostly cloudy|light rain|heavy rain|scattered showers)'
            ]
            
            for pattern in condition_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                weather_conditions.extend(matches)
            
            if temperatures or weather_conditions:
                result = "🔍 Google Weather:"
                if temperatures:
                    # Get the most likely temperature (usually the first one found)
                    result += f" Temperature: {temperatures[0]}°"
                if weather_conditions:
                    result += f" Condition: {weather_conditions[0].title()}"
                return result
                
        except Exception:
            pass
        
        return None
    
    def _get_openweather_data(self, city: str) -> str:
        """Try to get data from OpenWeatherMap public pages"""
        try:
            search_url = f"https://openweathermap.org/find?q={quote_plus(city)}"
            response = self.session.get(search_url, timeout=10)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for temperature and condition in the search results
            temp_elem = soup.select_one('.temperature')
            condition_elem = soup.select_one('.weather-condition')
            
            if temp_elem or condition_elem:
                result = "🌍 OpenWeatherMap:"
                if temp_elem:
                    result += f" Temperature: {temp_elem.get_text().strip()}"
                if condition_elem:
                    result += f" Condition: {condition_elem.get_text().strip()}"
                return result
                
        except Exception:
            pass
        
        return None
    
    def _get_accuweather_data(self, city: str) -> str:
        """Try to get data from AccuWeather"""
        try:
            search_url = f"https://www.accuweather.com/en/search-locations?query={quote_plus(city)}"
            response = self.session.get(search_url, timeout=10)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            
            # Look for temperature patterns
            temp_matches = re.findall(r'(\d+)°[CF]', text)
            condition_matches = re.findall(r'(Sunny|Cloudy|Rainy|Clear|Overcast|Stormy)', text, re.IGNORECASE)
            
            if temp_matches or condition_matches:
                result = "🏢 AccuWeather:"
                if temp_matches:
                    result += f" Temperature: {temp_matches[0]}°"
                if condition_matches:
                    result += f" Condition: {condition_matches[0]}"
                return result
                
        except Exception:
            pass
        
        return None
    
    def get_enhanced_search_results(self, query: str) -> str:
        """Enhanced search with multiple sources and better parsing"""
        try:
            results = []
            
            # Method 1: Enhanced Google Search
            google_results = self._enhanced_google_search(query)
            if google_results:
                results.extend(google_results)
            
            # Method 2: Bing Search (as fallback)
            bing_results = self._bing_search(query)
            if bing_results:
                results.extend(bing_results)
            
            # Method 3: DuckDuckGo with better parsing
            ddg_results = self._enhanced_ddg_search(query)
            if ddg_results:
                results.extend(ddg_results)
            
            if results:
                header = f"🔍 Enhanced Search Results for: '{query}'\n" + "="*60
                return header + "\n\n" + "\n\n".join(results[:5])
            else:
                return f"🔍 Enhanced Search Results for: '{query}'\n" + "="*60 + f"\n\nNo specific results found. Try manual search:\n• https://www.google.com/search?q={quote_plus(query)}\n• https://www.bing.com/search?q={quote_plus(query)}"
            
        except Exception as e:
            return f"❌ Error in enhanced search: {str(e)}"
    
    def _enhanced_google_search(self, query: str) -> List[str]:
        """Enhanced Google search with better content extraction"""
        try:
            url = f"https://www.google.com/search?q={quote_plus(query)}"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            
            # Look for featured snippets
            snippet_selectors = [
                '[data-attrid="wa:/description"]',
                '.hgKElc',
                '.BNeawe.s3v9rd.AP7Wnd',
                '.VwiC3b'
            ]
            
            for selector in snippet_selectors:
                elements = soup.select(selector)
                for elem in elements[:3]:
                    text = elem.get_text().strip()
                    if len(text) > 50 and len(text) < 400:
                        results.append(f"📝 Featured Info: {text}")
            
            return results[:2]  # Return top 2 results
            
        except Exception:
            return []
    
    def _bing_search(self, query: str) -> List[str]:
        """Search using Bing as alternative"""
        try:
            url = f"https://www.bing.com/search?q={quote_plus(query)}"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            
            # Look for Bing answer box
            answer_elem = soup.select_one('.b_ans')
            if answer_elem:
                text = answer_elem.get_text().strip()
                if len(text) > 20:
                    results.append(f"🔷 Bing Answer: {text}")
            
            return results
            
        except Exception:
            return []
    
    def _enhanced_ddg_search(self, query: str) -> List[str]:
        """Enhanced DuckDuckGo search"""
        try:
            url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1"
            response = self.session.get(url, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                if data.get("Answer"):
                    results.append(f"🦆 DDG Answer: {data['Answer']}")
                
                if data.get("Abstract"):
                    abstract = data["Abstract"]
                    if len(abstract) > 100:
                        results.append(f"📖 Definition: {abstract}")
                
                return results
            
        except Exception:
            pass
        
        return []

# Global intelligent scraper instance
intelligent_scraper = IntelligentUniversalScraper()

@tool("Universal Web Scraper")
def universal_web_scraper(query: str) -> str:
    """
    UNIVERSAL WEB SCRAPER - Uses AI to analyze any query and scrape accordingly.
    Can handle: weather, news, prices, sports, stocks, definitions, general information.
    
    Examples:
    - "Jaipur weather" → Weather data from multiple sources
    - "Bitcoin price" → Current cryptocurrency price
    - "AI news" → Latest AI news headlines  
    - "India vs Pakistan score" → Live sports scores
    - "What is machine learning" → Definition and explanation
    - "Tesla stock price" → Current stock price
    
    Args:
        query: Any question or search query
    
    Returns:
        Relevant scraped information based on intelligent query analysis
    """
    try:
        return intelligent_scraper.universal_scrape(query)
    except Exception as e:
        return f"❌ Error in universal scraping: {str(e)}\n\n🌐 Manual search: https://www.google.com/search?q={quote_plus(query)}"

@tool("Real Time Weather")  
def real_time_weather(city: str) -> str:
    """
    Get real-time weather information for any city.
    Uses multiple weather sources for accuracy.
    
    Args:
        city: The city name (e.g., "Jaipur", "Delhi", "Mumbai")
    
    Returns:
        Current weather conditions including temperature and description
    """
    try:
        return intelligent_scraper.get_weather_from_multiple_sources(city)
    except Exception as e:
        return f"❌ Error getting weather for {city}: {str(e)}"
