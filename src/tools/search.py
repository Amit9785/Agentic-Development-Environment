from langchain.tools import tool
import requests
import json
from urllib.parse import quote_plus
import re
from bs4 import BeautifulSoup

@tool("Web Search")
def simple_web_search(query: str, num_results: int = 5) -> str:
    """
    Search the web for current information using multiple APIs.
    Best for: weather, news, current events, factual information, definitions.
    Args:
        query: The search query string
        num_results: Number of results to return (default 5)
    Returns:
        Formatted search results with current information
    """
    try:
        results = []
        encoded_query = quote_plus(query)
        
        # Method 1: Try DuckDuckGo Instant Answer API (best for quick facts)
        try:
            ddg_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(ddg_url, timeout=8, headers={'User-Agent': 'ADE-Agent/1.0'})
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract instant answer (great for weather, calculations, etc.)
                if data.get("Answer"):
                    results.append(f"📋 Instant Answer: {data['Answer']}")
                    if data.get("AnswerType"):
                        results.append(f"   Type: {data['AnswerType']}")
                
                # Extract definition/abstract
                if data.get("Abstract") and len(data["Abstract"]) > 50:
                    results.append(f"\n📖 Information: {data['Abstract']}")
                    if data.get("AbstractSource"):
                        results.append(f"   Source: {data['AbstractSource']}")
                    if data.get("AbstractURL"):
                        results.append(f"   More info: {data['AbstractURL']}")
                
                # Extract related topics (additional information)
                if data.get("RelatedTopics") and len(results) < 3:
                    results.append("\n🔗 Related Information:")
                    count = 0
                    for topic in data["RelatedTopics"][:3]:
                        if isinstance(topic, dict) and topic.get("Text"):
                            count += 1
                            text = topic["Text"]
                            # Clean and limit text length
                            if len(text) > 150:
                                text = text[:150] + "..."
                            results.append(f"   {count}. {text}")
                            if topic.get("FirstURL"):
                                results.append(f"      🌐 {topic['FirstURL']}")
        except Exception as e:
            results.append(f"DuckDuckGo search had an issue: {str(e)}")
        
        # Method 2: Wikipedia for detailed factual information
        try:
            # Try direct Wikipedia page first
            wiki_summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"
            response = requests.get(wiki_summary_url, timeout=8)
            
            if response.status_code == 200:
                wiki_data = response.json()
                if wiki_data.get("extract") and len(wiki_data["extract"]) > 50:
                    extract = wiki_data["extract"]
                    if len(extract) > 300:
                        extract = extract[:300] + "..."
                    results.append(f"\n📚 Wikipedia: {extract}")
                    if wiki_data.get("content_urls", {}).get("desktop", {}).get("page"):
                        results.append(f"   Full article: {wiki_data['content_urls']['desktop']['page']}")
            
            # If no direct page, try Wikipedia search
            elif len(results) == 0:
                wiki_search_url = f"https://en.wikipedia.org/api/rest_v1/page/search/{encoded_query}"
                search_response = requests.get(wiki_search_url, timeout=8)
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    if search_data.get("pages") and len(search_data["pages"]) > 0:
                        first_result = search_data["pages"][0]
                        if first_result.get("description"):
                            results.append(f"\n📚 Wikipedia: {first_result['title']} - {first_result['description']}")
                            results.append(f"   Read more: https://en.wikipedia.org/wiki/{first_result['key']}")
        except:
            pass
        
        # Method 3: For weather queries, provide helpful guidance
        if any(word in query.lower() for word in ['weather', 'temperature', 'rain', 'forecast', 'climate']):
            if not any('weather' in result.lower() for result in results):
                city = query.lower().replace('weather', '').replace('temperature', '').replace('forecast', '').strip()
                results.append(f"\n🌤️ Weather Information:")
                results.append(f"   For current weather in {city}:")
                results.append(f"   • Check: https://weather.com/search/results?where={encoded_query}")
                results.append(f"   • Or: https://openweathermap.org/find?q={encoded_query}")
                results.append(f"   Note: Real-time weather requires specialized weather APIs")
        
        # Method 4: GitHub search for programming queries
        if any(keyword in query.lower() for keyword in ['python', 'javascript', 'code', 'programming', 'library', 'framework']):
            try:
                github_url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&order=desc&per_page=2"
                response = requests.get(github_url, timeout=6)
                if response.status_code == 200:
                    github_data = response.json()
                    if github_data.get("items"):
                        results.append("\n💻 GitHub Projects:")
                        for i, repo in enumerate(github_data["items"][:2], 1):
                            results.append(f"   {i}. {repo['full_name']} ⭐ {repo['stargazers_count']}")
                            if repo.get("description"):
                                desc = repo["description"]
                                if len(desc) > 100:
                                    desc = desc[:100] + "..."
                                results.append(f"      {desc}")
                            results.append(f"      🌐 {repo['html_url']}")
            except:
                pass
        
        # Format and return results
        if results:
            header = f"🔍 Search Results for: '{query}'\n" + "="*60
            return header + "\n" + "\n".join(results)
        else:
            # Enhanced fallback with specific suggestions
            return f"""🔍 Search Results for: '{query}'\n{'='*60}\n\nNo specific results found, but you can try:\n\n🌐 Manual Search Options:\n   • DuckDuckGo: https://duckduckgo.com/?q={encoded_query}\n   • Google: https://google.com/search?q={encoded_query}\n   • Wikipedia: https://en.wikipedia.org/wiki/Special:Search?search={encoded_query}\n\n💡 Tips: Try more specific keywords or check if you need real-time data"""
            
    except Exception as e:
        return f"🔍 Search Results for: '{query}'\n{'='*60}\n\n❌ Error during search: {str(e)}\n\n🌐 Try manual search: https://duckduckgo.com/?q={encoded_query}"

@tool("LangChain Documentation Search")  
def langchain_docs_search(topic: str) -> str:
    """
    Search LangChain documentation and resources for specific topics.
    Args:
        topic: The topic to search for in LangChain docs
    Returns:
        Relevant LangChain information and documentation links
    """
    try:
        # Common LangChain topics and their direct documentation URLs
        langchain_topics = {
            "tools": "https://python.langchain.com/docs/modules/tools/",
            "agents": "https://python.langchain.com/docs/modules/agents/",
            "chains": "https://python.langchain.com/docs/modules/chains/",
            "memory": "https://python.langchain.com/docs/modules/memory/",
            "embeddings": "https://python.langchain.com/docs/modules/data_connection/text_embedding/",
            "vectorstores": "https://python.langchain.com/docs/modules/data_connection/vectorstores/",
            "chat models": "https://python.langchain.com/docs/modules/model_io/chat/",
            "llms": "https://python.langchain.com/docs/modules/model_io/llms/",
            "prompts": "https://python.langchain.com/docs/modules/model_io/prompts/",
            "callbacks": "https://python.langchain.com/docs/modules/callbacks/",
            "langgraph": "https://langchain-ai.github.io/langgraph/"
        }
        
        results = []
        topic_lower = topic.lower()
        
        # Find matching topics
        matches = []
        for key, url in langchain_topics.items():
            if topic_lower in key or any(word in key for word in topic_lower.split()):
                matches.append((key, url))
        
        if matches:
            results.append(f"LangChain Documentation for '{topic}':nnN")
            for i, (key, url) in enumerate(matches, 1):
                results.append(f"{i}. {key.title()}")
                results.append(f"   Documentation: {url}")
        
        # Add general resources
        results.append("\\nGeneral LangChain Resources:")
        results.append("• Main Documentation: https://python.langchain.com/docs/")
        results.append("• API Reference: https://api.python.langchain.com/")
        results.append("• GitHub Repository: https://github.com/langchain-ai/langchain")
        results.append("• Community: https://github.com/langchain-ai/langchain/discussions")
        results.append("• LangGraph (New Agent Framework): https://langchain-ai.github.io/langgraph/")
        
        # Specific guidance for tools
        if "tool" in topic_lower:
            results.append("\\n🔧 New LangChain Tools Information:")
            results.append("• Custom Tools: https://python.langchain.com/docs/modules/tools/custom_tools")
            results.append("• Tool Calling: https://python.langchain.com/docs/modules/tools/tool_calling")
            results.append("• Toolkits: https://python.langchain.com/docs/integrations/toolkits/")
            results.append("• LangGraph Tools: https://langchain-ai.github.io/langgraph/how-tos/tool-calling/")
        
        return "\\n".join(results)
        
    except Exception as e:
        return f"Error searching LangChain docs: {str(e)}"

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
        
        # Try to extract readable content
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            content = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = '\\n'.join(chunk for chunk in chunks if chunk)
            
        except ImportError:
            # Fallback if BeautifulSoup is not available
            content = response.text
            # Basic cleanup
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\\s+', ' ', content)
        
        # Truncate for safety and readability
        max_length = 3000
        if len(content) > max_length:
            content = content[:max_length] + "\\n\\n[Content truncated for readability...]"
        
        return f"Content from {url}:\\n\\n{content}"
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching webpage: {str(e)}"
    except Exception as e:
        return f"Error processing webpage: {str(e)}"
