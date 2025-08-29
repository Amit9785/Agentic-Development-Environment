from langchain.agents import Tool
from .tools.calc import calculator
from .tools.py_repl import python_repl
from .tools.fs import fs_write, fs_read, create_directory
from .tools.search import simple_web_search, langchain_docs_search, get_webpage_content
from .tools.web_scraper import smart_web_scraper, targeted_web_scraper
from .tools.advanced_scraper import universal_web_scraper, real_time_weather

# New Advanced Tools
from .tools.project_creator import advanced_project_creator
from .tools.file_analyzer import intelligent_file_analyzer, quick_file_summary
from .tools.autonomous_writer import (
    autonomous_file_writer, autonomous_code_generator, 
    autonomous_documentation_writer, thinking_file_writer
)
from .tools.error_handler import (
    intelligent_error_handler, self_diagnostic_tool, error_recovery_assistant
)

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
        
        # Advanced AI-Powered Tools
        Tool.from_function(
            advanced_project_creator,
            name="Advanced Project Creator",
            description="AI creates complete projects with permission system, console UI, and intelligent structure generation."
        ),
        Tool.from_function(
            intelligent_file_analyzer,
            name="Intelligent File Analyzer",
            description="AI-powered file analysis with comprehensive insights, summaries, and code quality assessment."
        ),
        Tool.from_function(
            quick_file_summary,
            name="Quick File Summary",
            description="Get a quick summary of any file without full analysis."
        ),
        Tool.from_function(
            autonomous_file_writer,
            name="Autonomous File Writer",
            description="AI autonomously writes files based on its own thinking and reasoning process."
        ),
        Tool.from_function(
            autonomous_code_generator,
            name="Autonomous Code Generator",
            description="Generate complete, functional code autonomously with AI thinking process."
        ),
        Tool.from_function(
            autonomous_documentation_writer,
            name="Autonomous Documentation Writer",
            description="AI autonomously writes comprehensive documentation with intelligent structure."
        ),
        Tool.from_function(
            thinking_file_writer,
            name="Thinking File Writer",
            description="Write files with visible AI thinking process - shows how AI reasons through tasks."
        ),
        Tool.from_function(
            intelligent_error_handler,
            name="Intelligent Error Handler",
            description="AI-powered error analysis with automatic recovery strategies and self-healing."
        ),
        Tool.from_function(
            self_diagnostic_tool,
            name="Self Diagnostic Tool",
            description="Run comprehensive system diagnostics to identify and resolve issues."
        ),
        Tool.from_function(
            error_recovery_assistant,
            name="Error Recovery Assistant",
            description="Get AI assistance for error recovery when automatic recovery fails."
        ),
    ]
