from langchain.tools import tool
import requests
import os
import json
from typing import List, Dict
from urllib.parse import quote_plus

@tool("Web Search")
def web_search(query: str, num_results: int = 5) -> str:
    """
    Search the web for information using DuckDuckGo Instant Answer API.
    Args:
        query: The search query string
        num_results: Number of results to return (default 5, max 10)
    Returns:
        Formatted search results with titles, snippets, and URLs
    """
    try:
        # Use DuckDuckGo Instant Answer API (no API key required)
        encoded_query = quote_plus(query)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        
        headers = {
            'User-Agent': 'ADE-Agent/1.0 (Educational Purpose)'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        results = []
        result_count = 0
        
        # Check for instant answer
        if data.get("Answer"):
            results.append(f"\nInstant Answer: {data['Answer']}")
            if data.get("AnswerType"):
                results.append(f"Type: {data['AnswerType']}")
            result_count += 1
        
        # Check for abstract/definition
        if data.get("Abstract"):
            results.append(f"\nDefinition: {data['Abstract']}")
            if data.get("AbstractSource"):
                results.append(f"Source: {data['AbstractSource']}")
            if data.get("AbstractURL"):
                results.append(f"URL: {data['AbstractURL']}")
            result_count += 1
        
        # Check for related topics
        if data.get("RelatedTopics") and result_count < num_results:
            results.append("\nRelated Topics:")
            for i, topic in enumerate(data["RelatedTopics"][:num_results-result_count], 1):
                if isinstance(topic, dict):
                    text = topic.get("Text", "")
                    url = topic.get("FirstURL", "")
                    if text:
                        results.append(f"{result_count + i}. {text}")
                        if url:
                            results.append(f"   Link: {url}")
        
        # If no results, try a fallback search suggestion
        if not results:
            results.append(f"No direct results found for '{query}'.")
            results.append("Try searching for more specific terms or check:")
            results.append(f"- Manual search: https://duckduckgo.com/?q={encoded_query}")
            results.append(f"- LangChain docs: https://python.langchain.com/docs/")
        
        header = f"Search Results for: '{query}'\n" + "="*60
        return header + "\n" + "\n".join(results)
        
    except requests.exceptions.RequestException as e:
        return f"Error making search request: {str(e)}. Try manual search at https://duckduckgo.com/?q={quote_plus(query)}"
    except Exception as e:
        return f"Error during web search: {str(e)}"

@tool("Get Web Page Content")
def get_webpage_content(url: str) -> str:
    """
    Fetch the content of a web page.
    Args:
        url: The URL of the webpage to fetch
    Returns:
        The text content of the webpage (truncated for safety)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Basic text extraction (you could enhance this with BeautifulSoup)
        content = response.text
        
        # Truncate for safety and readability
        max_length = 5000
        if len(content) > max_length:
            content = content[:max_length] + "\\n\\n[Content truncated...]"
        
        return f"Content from {url}:\\n\\n{content}"
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching webpage: {str(e)}"
    except Exception as e:
        return f"Error processing webpage: {str(e)}"
