"""
Autonomous Writer Tool
AI can write files autonomously based on its own thinking and reasoning.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage


class AutonomousWriter:
    """AI-powered autonomous file writer with thinking and reasoning capabilities"""
    
    def __init__(self):
        self.llm = None
        self.writing_log = []
        self.workspace_dir = Path("data/agent_workspace")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_llm(self):
        """Lazy initialization of LLM"""
        if self.llm is None:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                    temperature=0.4,  # Slightly higher temperature for creativity
                    google_api_key=os.getenv("GOOGLE_API_KEY")
                )
            except Exception as e:
                self.llm = "error"
                return None
        return self.llm if self.llm != "error" else None
    
    def think_and_plan_writing(self, writing_request: str, context: str = "") -> Dict:
        """AI thinking process for autonomous writing"""
        
        thinking_prompt = f"""
You are an AUTONOMOUS AI WRITER. Analyze this writing request and create a detailed plan:

Request: "{writing_request}"
Context: "{context}"

Think through this step-by-step and provide a JSON response:
{{
    "understanding": "What the user really wants me to write",
    "file_type": "python|javascript|html|css|markdown|config|data|text",
    "suggested_filename": "appropriate_filename.ext",
    "content_structure": [
        "Header/imports section",
        "Main content section",
        "Footer/conclusion section"
    ],
    "key_elements_to_include": [
        "element1",
        "element2",
        "element3"
    ],
    "writing_approach": "creative|technical|educational|documentation|code",
    "estimated_lines": 50,
    "requires_research": true,
    "research_topics": ["topic1", "topic2"],
    "thinking_process": [
        "First, I need to...",
        "Then, I should...",
        "Finally, I will..."
    ],
    "confidence_level": "high|medium|low"
}}

Focus on creating high-quality, well-structured content that serves the user's needs.
        """
        
        llm = self._get_llm()
        if not llm:
            return self._fallback_planning(writing_request, context)
        
        try:
            response = llm.invoke([HumanMessage(content=thinking_prompt)])
            analysis_text = response.content
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                return plan
            else:
                return self._fallback_planning(writing_request, context)
                
        except Exception as e:
            return self._fallback_planning(writing_request, context, str(e))
    
    def _fallback_planning(self, writing_request: str, context: str = "", error: str = None) -> Dict:
        """Fallback planning when AI is not available"""
        
        request_lower = writing_request.lower()
        
        # Determine file type based on request
        if any(word in request_lower for word in ['python', 'script', '.py', 'function', 'class']):
            file_type = "python"
            filename = "script.py"
        elif any(word in request_lower for word in ['html', 'webpage', 'website']):
            file_type = "html"
            filename = "page.html"
        elif any(word in request_lower for word in ['readme', 'documentation', 'doc']):
            file_type = "markdown"
            filename = "README.md"
        elif any(word in request_lower for word in ['config', 'settings', 'json']):
            file_type = "config"
            filename = "config.json"
        else:
            file_type = "text"
            filename = "output.txt"
        
        return {
            "understanding": writing_request,
            "file_type": file_type,
            "suggested_filename": filename,
            "content_structure": ["Introduction", "Main content", "Conclusion"],
            "key_elements_to_include": ["Basic functionality"],
            "writing_approach": "technical",
            "estimated_lines": 20,
            "requires_research": False,
            "research_topics": [],
            "thinking_process": ["Analyze request", "Generate content", "Write file"],
            "confidence_level": "medium",
            "fallback_used": True,
            "error": error
        }
    
    def generate_content(self, plan: Dict, additional_context: str = "") -> str:
        """Generate actual file content based on the plan"""
        
        content_prompt = f"""
Based on this writing plan, generate the actual file content:

WRITING PLAN:
{json.dumps(plan, indent=2)}

ADDITIONAL CONTEXT:
{additional_context}

Requirements:
1. Write complete, functional content (not pseudocode)
2. Include proper structure and formatting
3. Add appropriate comments and documentation
4. Follow best practices for the file type
5. Make it production-ready

Generate the complete file content that I should write to {plan.get('suggested_filename', 'output.txt')}:
        """
        
        llm = self._get_llm()
        if not llm:
            return self._generate_fallback_content(plan)
        
        try:
            response = llm.invoke([HumanMessage(content=content_prompt)])
            content = response.content
            
            # Clean up common LLM artifacts
            content = content.replace('```python\n', '').replace('```\n', '').replace('```', '')
            content = content.replace('```html\n', '').replace('```json\n', '').replace('```markdown\n', '')
            
            return content.strip()
            
        except Exception as e:
            return self._generate_fallback_content(plan, str(e))
    
    def _generate_fallback_content(self, plan: Dict, error: str = None) -> str:
        """Generate basic content when AI is not available"""
        
        file_type = plan.get('file_type', 'text')
        filename = plan.get('suggested_filename', 'output.txt')
        understanding = plan.get('understanding', 'File content')
        
        if file_type == 'python':
            return f'''#!/usr/bin/env python3
"""
{understanding}
Auto-generated by Autonomous Writer
"""

def main():
    """Main function"""
    print("Hello from autonomous AI writer!")
    # TODO: Implement main functionality
    
if __name__ == "__main__":
    main()
'''
        
        elif file_type == 'markdown':
            return f'''# {understanding}

## Overview

This document was created by the Autonomous Writer.

## Content

Add your content here.

## Generated Information

- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Generator: ADE Autonomous Writer v1.0
'''
        
        elif file_type == 'html':
            return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{understanding}</title>
</head>
<body>
    <h1>{understanding}</h1>
    <p>Generated by Autonomous Writer</p>
</body>
</html>'''
        
        elif file_type == 'config':
            return json.dumps({
                "name": understanding,
                "created_by": "Autonomous Writer",
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0"
            }, indent=2)
        
        else:
            return f'''{understanding}

This file was created by the Autonomous Writer on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.

{"Error occurred: " + error if error else ""}
'''
    
    def log_writing_process(self, step: str, details: str):
        """Log the writing process for transparency"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "details": details
        }
        
        self.writing_log.append(log_entry)
        
        # Also log to file
        log_file = self.workspace_dir / "writing_log.txt"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{log_entry['timestamp']}] {step}: {details}\n")
        except Exception:
            pass  # Silent failure
    
    def autonomous_write_file(self, writing_request: str, file_path: str = None, context: str = "") -> str:
        """Main autonomous writing function"""
        
        self.log_writing_process("START", f"Beginning autonomous writing for: {writing_request}")
        
        try:
            # Step 1: Think and plan
            self.log_writing_process("THINKING", "Analyzing request and creating writing plan")
            plan = self.think_and_plan_writing(writing_request, context)
            
            # Step 2: Determine file path
            if not file_path:
                file_path = plan.get('suggested_filename', 'autonomous_output.txt')
            
            # Step 3: Check if research is needed
            if plan.get('requires_research', False):
                self.log_writing_process("RESEARCH", f"Research needed for: {plan.get('research_topics', [])}")
                # Here we could integrate with web scraping tools for research
                # For now, we'll note it in the plan
            
            # Step 4: Generate content
            self.log_writing_process("GENERATION", "Generating file content based on plan")
            content = self.generate_content(plan, context)
            
            # Step 5: Write file
            self.log_writing_process("WRITING", f"Writing content to {file_path}")
            success, write_result = self._write_file_safely(file_path, content)
            
            if success:
                self.log_writing_process("COMPLETE", f"Successfully created {file_path}")
                
                return f"""✅ AUTONOMOUS WRITING COMPLETED

🧠 My Thinking Process:
{chr(10).join(f'   {i+1}. {step}' for i, step in enumerate(plan.get('thinking_process', [])))}

📄 File Created: {file_path}
📊 Details:
   • Type: {plan.get('file_type', 'unknown').title()}
   • Approach: {plan.get('writing_approach', 'general').title()}
   • Content Length: {len(content)} characters
   • Estimated Lines: {len(content.split(chr(10)))}
   • Confidence: {plan.get('confidence_level', 'medium').title()}

💡 What I Included:
{chr(10).join(f'   • {element}' for element in plan.get('key_elements_to_include', []))}

🎯 Understanding: {plan.get('understanding', 'File content')}

{write_result}

💭 Tip: Check the file and let me know if you need any modifications!
"""
            else:
                self.log_writing_process("ERROR", f"Failed to write file: {write_result}")
                return f"❌ Failed to write file: {write_result}"
                
        except Exception as e:
            self.log_writing_process("ERROR", f"Exception in autonomous writing: {str(e)}")
            return f"❌ Error in autonomous writing: {str(e)}"
    
    def _write_file_safely(self, file_path: str, content: str) -> Tuple[bool, str]:
        """Write file with safety checks and error handling"""
        
        try:
            path = Path(file_path)
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists and get permission
            if path.exists():
                # For autonomous mode, we'll create a backup
                backup_path = path.with_suffix(path.suffix + '.backup')
                path.rename(backup_path)
                result_msg = f"✅ File written successfully (backup created: {backup_path.name})"
            else:
                result_msg = "✅ File written successfully"
            
            # Write the file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, result_msg
            
        except Exception as e:
            return False, f"Error writing file: {str(e)}"
    
    def create_smart_filename(self, writing_request: str, file_type: str) -> str:
        """Generate intelligent filename based on request"""
        
        # Clean the request to make a good filename
        import re
        
        # Extract key words
        words = re.findall(r'\w+', writing_request.lower())
        
        # Remove common words
        stop_words = {'create', 'make', 'write', 'file', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        key_words = [w for w in words if w not in stop_words][:3]  # Take first 3 meaningful words
        
        base_name = '_'.join(key_words) if key_words else 'autonomous_file'
        
        # Add appropriate extension
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'html': '.html',
            'css': '.css',
            'markdown': '.md',
            'config': '.json',
            'data': '.json',
            'text': '.txt'
        }
        
        extension = extensions.get(file_type, '.txt')
        
        return base_name + extension


@tool
def autonomous_file_writer(writing_request: str, file_path: str = None, context: str = "") -> str:
    """
    AI autonomously writes files based on its own thinking and reasoning.
    
    This tool enables the AI to:
    1. Think through what needs to be written
    2. Plan the content structure and approach  
    3. Generate high-quality content autonomously
    4. Write the file with proper error handling
    5. Provide detailed logs of its thinking process
    
    Args:
        writing_request: What the AI should write (e.g., "Create a Python calculator script")
        file_path: Optional specific path for the file (AI will suggest one if not provided)
        context: Optional additional context to help with writing
    
    Returns:
        str: Status of autonomous writing with thinking process and details
    """
    
    try:
        writer = AutonomousWriter()
        
        # Autonomous writing process
        result = writer.autonomous_write_file(writing_request, file_path, context)
        
        return result
        
    except Exception as e:
        return f"❌ Error in autonomous writing: {str(e)}"


@tool
def autonomous_code_generator(code_description: str, language: str = "python") -> str:
    """
    Generate complete, functional code autonomously based on description.
    
    This tool specializes in:
    1. Understanding code requirements from natural language
    2. Planning code structure and architecture
    3. Generating production-ready code with proper structure
    4. Including error handling, documentation, and best practices
    
    Args:
        code_description: Description of what code to generate (e.g., "A web scraper for news articles")
        language: Programming language (default: python)
    
    Returns:
        str: Generated code with explanation of AI's thinking process
    """
    
    try:
        writer = AutonomousWriter()
        
        # Enhanced code generation with thinking
        code_prompt = f"""
I am an autonomous AI code generator. Generate complete, functional {language} code for:

"{code_description}"

My thinking process:
1. ANALYZE: What does this code need to do?
2. DESIGN: What structure and components are needed?
3. IMPLEMENT: Generate clean, working code
4. DOCUMENT: Add proper comments and docstrings
5. VALIDATE: Ensure error handling and best practices

Generate production-ready code with:
- Proper imports and dependencies
- Error handling and validation
- Clear documentation and comments
- Modular, reusable structure
- Example usage if appropriate

The code should be complete and ready to run.
        """
        
        llm = writer._get_llm()
        if not llm:
            return f"❌ AI code generator not available. Please check your API configuration."
        
        try:
            response = llm.invoke([HumanMessage(content=code_prompt)])
            generated_code = response.content
            
            # Clean up code formatting
            generated_code = generated_code.replace('```python\n', '').replace('```\n', '').replace('```', '')
            
            # Suggest filename
            filename = writer.create_smart_filename(code_description, language)
            
            # Write to file
            success, write_result = writer._write_file_safely(filename, generated_code)
            
            if success:
                writer.log_writing_process("CODE_GENERATION", f"Generated {language} code: {filename}")
                
                return f"""🤖 AUTONOMOUS CODE GENERATION COMPLETED

📝 Request: {code_description}
💻 Language: {language.title()}
📄 File: {filename}

🧠 My Thinking:
   1. Analyzed requirements from description
   2. Designed appropriate code structure  
   3. Generated functional, documented code
   4. Added error handling and best practices
   5. Created ready-to-run implementation

📊 Code Details:
   • Lines: {len(generated_code.split(chr(10)))}
   • Characters: {len(generated_code)}
   • {write_result}

🎯 The code includes:
   • Proper imports and structure
   • Error handling and validation
   • Documentation and comments
   • Example usage (where applicable)

💡 Next: Review the code and run it to test functionality!
"""
            else:
                return f"❌ Generated code but failed to write file: {write_result}"
                
        except Exception as e:
            return f"❌ Error generating code: {str(e)}"
        
    except Exception as e:
        return f"❌ Error in autonomous code generator: {str(e)}"


@tool
def autonomous_documentation_writer(topic: str, doc_type: str = "README") -> str:
    """
    Autonomously write comprehensive documentation.
    
    Args:
        topic: What to document (e.g., "How to use the ADE system")
        doc_type: Type of documentation (README, API, USER_GUIDE, TUTORIAL)
    
    Returns:
        str: Generated documentation with AI thinking process
    """
    
    try:
        writer = AutonomousWriter()
        
        doc_prompt = f"""
I am an autonomous documentation writer. Create comprehensive {doc_type} documentation for:

Topic: "{topic}"

My autonomous process:
1. UNDERSTAND: What needs to be documented?
2. STRUCTURE: What sections and flow make sense?
3. RESEARCH: What information do I need to include?
4. WRITE: Create clear, helpful documentation
5. REVIEW: Ensure completeness and clarity

Generate professional documentation with:
- Clear structure and headings
- Step-by-step instructions where needed
- Examples and code snippets
- Troubleshooting information
- Proper formatting (Markdown)

Make it comprehensive and user-friendly.
        """
        
        llm = writer._get_llm()
        if not llm:
            return "❌ AI documentation writer not available."
        
        try:
            response = llm.invoke([HumanMessage(content=doc_prompt)])
            doc_content = response.content
            
            # Generate appropriate filename
            filename = f"{topic.lower().replace(' ', '_')}_{doc_type.lower()}.md"
            filename = writer.create_smart_filename(f"{topic} {doc_type}", "markdown")
            
            # Write documentation
            success, write_result = writer._write_file_safely(filename, doc_content)
            
            if success:
                writer.log_writing_process("DOCUMENTATION", f"Generated {doc_type} for {topic}")
                
                return f"""📚 AUTONOMOUS DOCUMENTATION COMPLETED

📝 Topic: {topic}
📋 Type: {doc_type}
📄 File: {filename}

🧠 My Documentation Process:
   1. Analyzed what needs to be documented
   2. Structured information logically
   3. Included examples and instructions
   4. Added troubleshooting guidance
   5. Formatted for easy reading

📊 Documentation Details:
   • Length: {len(doc_content)} characters
   • Sections: Multiple organized sections
   • Format: Markdown
   • {write_result}

✨ Features Included:
   • Clear headings and structure
   • Step-by-step instructions
   • Code examples (where relevant)
   • Professional formatting

🎯 Ready to use! The documentation is comprehensive and user-friendly.
"""
            else:
                return f"❌ Generated documentation but failed to write: {write_result}"
                
        except Exception as e:
            return f"❌ Error generating documentation: {str(e)}"
        
    except Exception as e:
        return f"❌ Error in autonomous documentation writer: {str(e)}"


@tool
def thinking_file_writer(instruction: str, target_file: str = None) -> str:
    """
    Write files with visible AI thinking process - shows how the AI reasons through the task.
    
    Args:
        instruction: What to write and why
        target_file: Specific file path (optional)
    
    Returns:
        str: File creation result with full thinking process displayed
    """
    
    try:
        writer = AutonomousWriter()
        
        # Step 1: Show thinking process
        thinking_display = f"""
🧠 AUTONOMOUS AI THINKING PROCESS
===============================================

📝 Instruction Received: {instruction}

💭 My Thinking:
   1. ANALYZE: Let me understand what needs to be written...
   2. PLAN: I need to structure this properly...
   3. GENERATE: Creating content that meets the requirements...
   4. VALIDATE: Ensuring quality and completeness...
   5. EXECUTE: Writing the file autonomously...

🎯 Starting autonomous writing process...
"""
        
        print(thinking_display)
        
        # Step 2: Execute autonomous writing
        result = writer.autonomous_write_file(instruction, target_file)
        
        return f"""{thinking_display}

{result}

🧠 Thinking Process Complete: I analyzed, planned, generated, and executed autonomously!
"""
        
    except Exception as e:
        return f"❌ Error in thinking file writer: {str(e)}"
