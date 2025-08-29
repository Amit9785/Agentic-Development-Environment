"""
Intelligent File Analyzer Tool
Reads and analyzes files with AI-powered summaries and insights.
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import json
import re


class IntelligentFileAnalyzer:
    """AI-powered file analyzer with smart content understanding"""
    
    def __init__(self):
        self.llm = None
        self.analysis_cache = {}
        
    def _get_llm(self):
        """Lazy initialization of LLM"""
        if self.llm is None:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                    temperature=0.2,  # Lower temperature for consistent analysis
                    google_api_key=os.getenv("GOOGLE_API_KEY")
                )
            except Exception as e:
                self.llm = "error"
                return None
        return self.llm if self.llm != "error" else None
    
    def detect_file_type(self, file_path: str) -> Dict:
        """Detect and analyze file type"""
        
        path = Path(file_path)
        
        if not path.exists():
            return {
                "exists": False,
                "error": f"File not found: {file_path}"
            }
        
        # Basic file info
        stat = path.stat()
        mime_type, encoding = mimetypes.guess_type(str(path))
        
        # Determine category based on extension and content
        suffix = path.suffix.lower()
        
        categories = {
            'code': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.php', '.rb', '.swift'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.xml'],
            'documentation': ['.md', '.txt', '.rst', '.tex', '.rtf'],
            'data': ['.csv', '.xlsx', '.json', '.xml', '.sql'],
            'web': ['.html', '.htm', '.css', '.js', '.ts'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
            'binary': ['.exe', '.dll', '.so', '.dylib', '.bin']
        }
        
        file_category = 'unknown'
        for category, extensions in categories.items():
            if suffix in extensions:
                file_category = category
                break
        
        return {
            "exists": True,
            "path": str(path.absolute()),
            "name": path.name,
            "suffix": suffix,
            "size": stat.st_size,
            "size_human": self._format_size(stat.st_size),
            "modified": stat.st_mtime,
            "category": file_category,
            "mime_type": mime_type,
            "encoding": encoding,
            "is_text": self._is_text_file(path),
            "is_binary": stat.st_size > 1024*1024 or file_category == 'binary'  # Files > 1MB or binary extensions
        }
    
    def _format_size(self, size: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def _is_text_file(self, path: Path) -> bool:
        """Check if file is likely text-based"""
        try:
            # Read first 1KB to check for binary content
            with open(path, 'rb') as f:
                chunk = f.read(1024)
                
            # If we find null bytes, it's likely binary
            if b'\x00' in chunk:
                return False
                
            # Try to decode as UTF-8
            try:
                chunk.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
                
        except Exception:
            return False
    
    def read_file_content(self, file_path: str, max_lines: int = 1000) -> Tuple[str, Dict]:
        """Read file content safely with limits"""
        
        path = Path(file_path)
        file_info = self.detect_file_type(file_path)
        
        if not file_info.get("exists", False):
            return "", file_info
        
        if not file_info.get("is_text", False):
            return "", {**file_info, "error": "File is binary or too large to read"}
        
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        file_info["truncated"] = True
                        file_info["truncated_at_line"] = max_lines
                        break
                    lines.append(line.rstrip())
                
                content = '\n'.join(lines)
                file_info["lines_read"] = len(lines)
                return content, file_info
                
        except Exception as e:
            return "", {**file_info, "error": f"Could not read file: {str(e)}"}
    
    def analyze_content_with_ai(self, content: str, file_info: Dict) -> Dict:
        """Use AI to analyze file content and generate insights"""
        
        # Create cache key
        cache_key = f"{file_info['path']}_{file_info['modified']}"
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        analysis_prompt = f"""
Analyze this file content and provide a comprehensive summary:

File Info:
- Path: {file_info['path']}
- Category: {file_info['category']}
- Size: {file_info['size_human']}
- Lines: {file_info.get('lines_read', 0)}

Content:
{content[:3000]}  # First 3000 chars to stay within limits

Provide analysis in this JSON format:
{{
    "summary": "Brief 2-3 sentence summary of what this file does",
    "purpose": "Main purpose/function of this file",
    "file_type": "Specific type (e.g., 'Python script', 'Config file', 'Documentation')",
    "key_components": ["component1", "component2", "component3"],
    "technologies": ["tech1", "tech2"],
    "complexity": "low|medium|high",
    "main_functions": ["function1", "function2"],
    "dependencies": ["dep1", "dep2"],
    "key_insights": [
        "Important insight 1",
        "Important insight 2"
    ],
    "potential_issues": ["issue1", "issue2"],
    "improvement_suggestions": ["suggestion1", "suggestion2"],
    "code_quality": "excellent|good|fair|poor",
    "estimated_lines_of_logic": 50
}}

Focus on practical insights that would help a developer understand and work with this file.
        """
        
        llm = self._get_llm()
        if not llm:
            return self._fallback_content_analysis(content, file_info)
        
        try:
            response = llm.invoke([HumanMessage(content=analysis_prompt)])
            analysis_text = response.content
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                
                # Cache the result
                self.analysis_cache[cache_key] = analysis
                return analysis
            else:
                return self._fallback_content_analysis(content, file_info)
                
        except Exception as e:
            return self._fallback_content_analysis(content, file_info, str(e))
    
    def _fallback_content_analysis(self, content: str, file_info: Dict, error: str = None) -> Dict:
        """Fallback analysis when AI is not available"""
        
        lines = content.split('\n')
        words = content.split()
        
        # Simple heuristics
        functions = len(re.findall(r'def\s+\w+', content))  # Python functions
        classes = len(re.findall(r'class\s+\w+', content))   # Python classes
        imports = len(re.findall(r'^(import|from)\s+', content, re.MULTILINE))  # Import statements
        
        # Determine complexity
        if len(lines) > 500 or functions > 10:
            complexity = "high"
        elif len(lines) > 100 or functions > 5:
            complexity = "medium"
        else:
            complexity = "low"
        
        return {
            "summary": f"File with {len(lines)} lines and {len(words)} words",
            "purpose": f"File in {file_info['category']} category", 
            "file_type": file_info['category'].title(),
            "key_components": [f"{functions} functions", f"{classes} classes", f"{imports} imports"],
            "technologies": ["Python"] if file_info['suffix'] == '.py' else ["Unknown"],
            "complexity": complexity,
            "main_functions": [],
            "dependencies": [],
            "key_insights": [f"Contains {len(lines)} lines of content"],
            "potential_issues": [],
            "improvement_suggestions": [],
            "code_quality": "unknown",
            "estimated_lines_of_logic": len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            "fallback_used": True,
            "error": error
        }
    
    def format_analysis_report(self, file_info: Dict, content_analysis: Dict) -> str:
        """Format comprehensive analysis report"""
        
        report = []
        
        # Header
        report.append("="*80)
        report.append("📄 INTELLIGENT FILE ANALYSIS REPORT")
        report.append("="*80)
        
        # Basic file information
        report.append(f"\n📁 FILE INFORMATION:")
        report.append(f"   Path: {file_info['path']}")
        report.append(f"   Name: {file_info['name']}")
        report.append(f"   Size: {file_info['size_human']} ({file_info['size']} bytes)")
        report.append(f"   Category: {file_info['category'].title()}")
        report.append(f"   Type: {content_analysis.get('file_type', 'Unknown')}")
        
        if file_info.get('lines_read'):
            report.append(f"   Lines: {file_info['lines_read']}")
        
        # AI Analysis
        report.append(f"\n🧠 AI ANALYSIS:")
        report.append(f"   Summary: {content_analysis.get('summary', 'No summary available')}")
        report.append(f"   Purpose: {content_analysis.get('purpose', 'Unknown')}")
        report.append(f"   Complexity: {content_analysis.get('complexity', 'unknown').title()}")
        
        if content_analysis.get('code_quality') != 'unknown':
            report.append(f"   Code Quality: {content_analysis['code_quality'].title()}")
        
        # Key Components
        if content_analysis.get('key_components'):
            report.append(f"\n🔧 KEY COMPONENTS:")
            for component in content_analysis['key_components']:
                report.append(f"   • {component}")
        
        # Technologies
        if content_analysis.get('technologies'):
            report.append(f"\n💻 TECHNOLOGIES:")
            for tech in content_analysis['technologies']:
                report.append(f"   • {tech}")
        
        # Main Functions
        if content_analysis.get('main_functions'):
            report.append(f"\n⚙️ MAIN FUNCTIONS:")
            for func in content_analysis['main_functions']:
                report.append(f"   • {func}")
        
        # Dependencies
        if content_analysis.get('dependencies'):
            report.append(f"\n📦 DEPENDENCIES:")
            for dep in content_analysis['dependencies']:
                report.append(f"   • {dep}")
        
        # Key Insights
        if content_analysis.get('key_insights'):
            report.append(f"\n💡 KEY INSIGHTS:")
            for insight in content_analysis['key_insights']:
                report.append(f"   • {insight}")
        
        # Potential Issues
        if content_analysis.get('potential_issues'):
            report.append(f"\n⚠️ POTENTIAL ISSUES:")
            for issue in content_analysis['potential_issues']:
                report.append(f"   • {issue}")
        
        # Improvement Suggestions
        if content_analysis.get('improvement_suggestions'):
            report.append(f"\n🚀 IMPROVEMENT SUGGESTIONS:")
            for suggestion in content_analysis['improvement_suggestions']:
                report.append(f"   • {suggestion}")
        
        # Statistics
        report.append(f"\n📊 STATISTICS:")
        report.append(f"   Estimated Logic Lines: {content_analysis.get('estimated_lines_of_logic', 0)}")
        
        if content_analysis.get('fallback_used'):
            report.append(f"\n⚠️  Note: Used fallback analysis (AI not available)")
            if content_analysis.get('error'):
                report.append(f"   Error: {content_analysis['error']}")
        
        report.append("="*80)
        
        return '\n'.join(report)


# Tool function for LangChain integration
@tool  
def intelligent_file_analyzer(file_path: str) -> str:
    """
    Read and analyze any file with AI-powered insights and summaries.
    
    This tool will:
    1. Detect file type and basic properties
    2. Read file content safely (with limits for large files)
    3. Use AI to analyze content and generate insights
    4. Provide comprehensive summary with key information
    
    Args:
        file_path: Path to the file to analyze (e.g., "C:\\path\\to\\file.py" or "src/main.py")
    
    Returns:
        str: Comprehensive analysis report with file summary and insights
    """
    
    try:
        analyzer = IntelligentFileAnalyzer()
        
        # Step 1: Detect file type and basic info
        file_info = analyzer.detect_file_type(file_path)
        
        if not file_info.get("exists", False):
            return f"❌ {file_info.get('error', 'File not found')}"
        
        # Step 2: Read content if it's a text file
        if file_info.get("is_binary", False):
            return f"""📄 FILE ANALYSIS: {file_info['name']}

📁 Basic Information:
   Path: {file_info['path']}
   Size: {file_info['size_human']}
   Type: {file_info['category'].title()}
   
⚠️  This file is binary and cannot be analyzed for content.
   
🔍 Detected as: {file_info.get('mime_type', 'Unknown type')}
"""
        
        content, updated_info = analyzer.read_file_content(file_path)
        file_info.update(updated_info)
        
        if not content and file_info.get("error"):
            return f"❌ {file_info['error']}"
        
        # Step 3: AI Analysis
        content_analysis = analyzer.analyze_content_with_ai(content, file_info)
        
        # Step 4: Format and return comprehensive report
        report = analyzer.format_analysis_report(file_info, content_analysis)
        
        return report
        
    except Exception as e:
        return f"❌ Error analyzing file: {str(e)}"


@tool
def quick_file_summary(file_path: str) -> str:
    """
    Get a quick summary of a file without full analysis.
    
    Args:
        file_path: Path to the file to summarize
    
    Returns:
        str: Quick summary of the file
    """
    
    try:
        analyzer = IntelligentFileAnalyzer()
        file_info = analyzer.detect_file_type(file_path)
        
        if not file_info.get("exists", False):
            return f"❌ {file_info.get('error', 'File not found')}"
        
        if file_info.get("is_binary", False):
            return f"📄 {file_info['name']}: Binary file ({file_info['size_human']}) - {file_info['category']}"
        
        content, _ = analyzer.read_file_content(file_path, max_lines=100)  # Quick read
        
        if not content:
            return f"📄 {file_info['name']}: Empty or unreadable file ({file_info['size_human']})"
        
        # Quick analysis without AI
        lines = content.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        # Extract first few meaningful lines for preview
        preview_lines = []
        for line in lines[:10]:
            if line.strip() and not line.strip().startswith('#'):
                preview_lines.append(line.strip()[:60])
                if len(preview_lines) >= 3:
                    break
        
        summary = f"""📄 {file_info['name']} ({file_info['size_human']})
   Category: {file_info['category'].title()}
   Lines: {len(lines)} ({len(non_empty_lines)} non-empty)
   Preview: {' | '.join(preview_lines) if preview_lines else 'No preview available'}"""
        
        return summary
        
    except Exception as e:
        return f"❌ Error getting file summary: {str(e)}"
