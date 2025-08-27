from langchain.agents import Tool
from .tools.calc import calculator
from .tools.py_repl import python_repl
from .tools.fs import fs_write, fs_read, create_directory
from .tools.search import simple_web_search, langchain_docs_search, get_webpage_content
from .tools.web_scraper import smart_web_scraper, targeted_web_scraper
from .tools.advanced_scraper import universal_web_scraper, real_time_weather

def get_tools() -> list[Tool]:
    return [
        Tool.from_function(
            calculator,
            name="Calculator",
            description="Performs basic arithmetic calculations."
        ),
        Tool.from_function(
            python_repl,
            name="Python REPL",
            description="Executes Python code and returns the result."
        ),
        Tool.from_function(
            fs_write,
            name="File Write",
            description="Writes content to a file on the filesystem."
        ),
        Tool.from_function(
            fs_read,
            name="File Read",
            description="Reads content from a file on the filesystem."
        ),
        Tool.from_function(
            create_directory,
            name="Create Directory",
            description="Creates a directory and any necessary parent directories."
        ),
        Tool.from_function(
            simple_web_search,
            name="Web Search",
            description="Search the web using multiple free APIs (DuckDuckGo, Wikipedia, GitHub)."
        ),
        Tool.from_function(
            langchain_docs_search,
            name="LangChain Search",
            description="Search LangChain documentation and resources for specific topics."
        ),
        Tool.from_function(
            get_webpage_content,
            name="Get Web Page Content",
            description="Fetch the text content of a specific webpage."
        ),
        Tool.from_function(
            smart_web_scraper,
            name="Smart Web Scraper",
            description="Intelligently scrape web content based on query type (weather, news, info)."
        ),
        Tool.from_function(
            targeted_web_scraper,
            name="Targeted Web Scraper",
            description="Scrape specific information from a given URL."
        ),
        Tool.from_function(
            universal_web_scraper,
            name="Universal Web Scraper",
            description="AI-powered universal web scraper for ANY query - weather, news, prices, sports, stocks, definitions."
        ),
        Tool.from_function(
            real_time_weather,
            name="Real Time Weather",
            description="Get accurate real-time weather information for any city."
        ),
    ]
