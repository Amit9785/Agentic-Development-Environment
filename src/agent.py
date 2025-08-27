import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from .memory import build_memories
from .tool_registry import get_tools

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

def build_agent(verbose: bool = True):
    try:
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            temperature=0.2,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    except Exception as e:
        print(f"Error initializing Google AI model: {e}")
        print("Please check your GOOGLE_API_KEY in the .env file")
        raise
    
    memory, ltm = build_memories()
    tools = get_tools()

    # Custom system prompt to make agent more proactive about web searches
    system_prompt = """
You are ADE (Agentic Development Environment), a helpful AI assistant with access to various tools.

IMPORTANT INSTRUCTIONS:
- For WEATHER questions, ALWAYS use Real Time Weather or Advanced Web Scraper first
- For questions about current information (news, recent events, prices, etc.), use Advanced Web Scraper
- For factual information, definitions, or general knowledge, use Advanced Web Scraper
- For programming/LangChain questions, use LangChain Search first
- For file operations, use File Write, File Read, or Create Directory tools
- For calculations, use Calculator or Python REPL
- Always try to provide helpful, accurate information using the available tools

Tool Priority:
1. Real Time Weather - Best for weather queries (temperature, conditions, etc.)
2. Advanced Web Scraper - Best for current info, news, general facts
3. Smart Web Scraper - Fallback for web scraping
4. Web Search - Basic searches
5. LangChain Search - For LangChain-specific questions
6. Targeted Web Scraper - For scraping specific URLs

Example behaviors:
- "Tell me about Jaipur weather" → Use Real Time Weather immediately
- "What's the temperature in Delhi?" → Use Real Time Weather immediately
- "What's the current price of Bitcoin?" → Use Advanced Web Scraper
- "Latest news about AI" → Use Advanced Web Scraper
- "Create a file called test.py" → Use File Write tool
- "What are LangChain tools?" → Use LangChain Search first

Be proactive and always try to get the most accurate, real-time information!
"""
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=verbose,
        handle_parsing_errors=True,
        max_iterations=3,
        early_stopping_method="generate",
        agent_kwargs={
            "system_message": system_prompt
        }
    )

    return agent, ltm
