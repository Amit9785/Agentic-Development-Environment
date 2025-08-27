import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table
from langchain.schema import HumanMessage

from .agent import build_agent

class AutonomousADE:
    """Enhanced ADE with Autonomous Thinking Capabilities"""
    
    def __init__(self):
        load_dotenv()
        self.console = Console()
        self.mode = "autonomous"  # Start in autonomous mode
        
        # Setup workspace for autonomous thinking
        self.workspace_dir = Path("data/agent_workspace")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.thinking_log = self.workspace_dir / "thinking_log.txt"
        
        # Setup agents
        self.agent = None
        self.ltm = None
        self.setup_agents()
        
        # Log initialization
        self.log_thought("🧠 Autonomous ADE initialized and ready to think independently")
    
    def setup_agents(self):
        """Setup both standard and enhanced autonomous agent"""
        try:
            self.agent, self.ltm = build_agent(verbose=True)
            
            # Enhance the agent with autonomous thinking prompt
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.thinking_llm = ChatGoogleGenerativeAI(
                model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                temperature=0.3,
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
        except Exception as e:
            self.console.print(f"[red]Error setting up agents: {e}[/red]")
    
    def log_thought(self, thought: str):
        """Log agent's thinking process"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {thought}\n"
        
        try:
            with open(self.thinking_log, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            pass  # Silently fail to avoid disruption
    
    def think_and_plan(self, user_input: str) -> str:
        """Autonomous thinking process"""
        self.log_thought(f"🤔 Analyzing request: {user_input}")
        
        thinking_prompt = f"""
You are an AUTONOMOUS THINKING AGENT. Analyze this user request:
"{user_input}"

Think step-by-step:
1. What does the user really want?
2. What information do I need to gather?
3. What files should I read or create?
4. What tools should I use?
5. What's the best execution plan?

Provide a concise thinking process and execution strategy.
        """
        
        try:
            response = self.thinking_llm.invoke([HumanMessage(content=thinking_prompt)])
            thinking = response.content
            self.log_thought(f"💭 Thinking complete: {thinking[:200]}...")
            return thinking
        except Exception as e:
            self.log_thought(f"Thinking error: {e}")
            return "Will proceed with standard processing."
    
    def autonomous_execute(self, user_input: str) -> str:
        """Execute with autonomous thinking"""
        if self.mode == "autonomous":
            # Step 1: Think and plan
            thinking = self.think_and_plan(user_input)
            
            # Step 2: Create enhanced prompt
            enhanced_prompt = f"""
USER REQUEST: {user_input}

AUTONOMOUS THINKING: {thinking}

Now I will execute this autonomously:
- Read files if I need context
- Search web for current information
- Create/modify files as needed
- Use multiple tools in sequence
- Provide complete solutions

Executing now...
            """
            
            self.log_thought("------Starting autonomous execution---------")
            
            try:
                result = self.agent.invoke({"input": enhanced_prompt})
                response = result.get("output", "No response generated")
                
                self.log_thought("♫♫ Autonomous execution completed")
                
                return f"""
AUTONOMOUS EXECUTION COMPLETE

-- My Thinking: --
{thinking}

--Result: --
{response}

--💡 Tip: Use '/thoughts' to see my full thinking log
                """
                
            except Exception as e:
                error_msg = f" Error in autonomous execution: {str(e)}"
                self.log_thought(error_msg)
                return error_msg
        else:
            # Standard mode
            try:
                result = self.agent.invoke({"input": user_input})
                return result.get("output", "No response generated")
            except Exception as e:
                return f"Error: {str(e)}"
    
    def display_banner(self):
        """Display enhanced banner"""
        title = Text(" AUTONOMOUS ADE", style="bold cyan")
        subtitle = Text("Agentic Development Environment with Autonomous Thinking", style="italic")
        mode_text = Text(f"Mode: {self.mode.upper()}", 
                        style="bold green" if self.mode == "autonomous" else "bold yellow")
        
        banner_text = Text()
        banner_text.append(title)
        banner_text.append("\n")
        banner_text.append(subtitle)
        banner_text.append("\n")
        banner_text.append(mode_text)
        
        panel = Panel(banner_text, border_style="cyan", padding=(1, 2))
        self.console.print(panel)
    
    def show_help(self):
        """Show available commands"""
        table = Table(title="Available Commands", show_header=True)
        table.add_column("Command", style="cyan", width=15)
        table.add_column("Description", style="white")
        
        table.add_row("/mode", "Switch between 'autonomous' and 'standard' modes")
        table.add_row("/thoughts", "View the agent's thinking log")
        table.add_row("/workspace", "View agent workspace status")
        table.add_row("/help", "Show this help message")
        table.add_row("/clear", "Clear the thinking log")
        table.add_row("exit/quit", "Exit the application")
        table.add_row("", "")
        table.add_row("Any other input", "Will be processed by the active agent")
        
        self.console.print(table)
    
    def show_thoughts(self):
        """Show thinking log"""
        try:
            if self.thinking_log.exists():
                with open(self.thinking_log, "r", encoding="utf-8") as f:
                    thoughts = f.read()
                if thoughts.strip():
                    panel = Panel(thoughts, title="🧠 Agent Thinking Log", border_style="blue")
                    self.console.print(panel)
                else:
                    self.console.print("[yellow]No thoughts logged yet.[/yellow]")
            else:
                self.console.print("[yellow]No thinking log found.[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Error reading thoughts: {e}[/red]")
    
    def show_workspace(self):
        """Show workspace status"""
        try:
            files = list(self.workspace_dir.glob("*"))
            status = f"**Workspace:** {self.workspace_dir}\n\n**Files:**\n"
            
            for file in files:
                size = file.stat().st_size if file.is_file() else "DIR"
                modified = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                status += f"- {file.name} ({size} bytes) - {modified}\n"
            
            panel = Panel(status, title="🔍 Agent Workspace", border_style="green")
            self.console.print(panel)
        except Exception as e:
            self.console.print(f"[red]Error showing workspace: {e}[/red]")
    
    def run(self):
        """Main application loop"""
        self.display_banner()
        self.console.print("\n[bold]Welcome to Autonomous ADE! Type '/help' for commands.[/bold]\n")
        
        # Seed memory
        seed_path = "data/seed_memory.txt"
        if os.path.exists(seed_path) and self.ltm:
            try:
                with open(seed_path, "r", encoding="utf-8") as f:
                    seed = f.read().strip()
                    if seed:
                        self.ltm.add_text(seed, {"source": "seed_memory"})
                        self.console.print("[green]✅ Loaded seed memory[/green]")
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load seed memory: {e}[/yellow]")
        
        while True:
            try:
                # Enhanced prompt with mode indicator
                mode_icon = "🧠" if self.mode == "autonomous" else "🤖"
                user_input = Prompt.ask(f"\n[bold cyan]{mode_icon} You[/bold cyan]").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in {"exit", "quit", "/quit"}:
                    self.console.print("[yellow]👋 Goodbye![/yellow]")
                    break
                
                elif user_input.lower() == "/mode":
                    self.mode = "standard" if self.mode == "autonomous" else "autonomous"
                    self.console.print(f"[green]Switched to {self.mode.upper()} mode[/green]")
                    continue
                
                elif user_input.lower() == "/help":
                    self.show_help()
                    continue
                
                elif user_input.lower() == "/thoughts":
                    self.show_thoughts()
                    continue
                
                elif user_input.lower() == "/workspace":
                    self.show_workspace()
                    continue
                
                elif user_input.lower() == "/clear":
                    try:
                        with open(self.thinking_log, "w") as f:
                            f.write("")
                        self.console.print("[green]✅ Thinking log cleared[/green]")
                    except Exception as e:
                        self.console.print(f"[red]Error clearing log: {e}[/red]")
                    continue
                
                # Handle memory commands
                elif user_input.lower().startswith(("remember ", "save ")):
                    if self.ltm:
                        try:
                            self.ltm.add_text(user_input, {"source": "user-remember"})
                            self.console.print("[green]✅ Saved to long-term memory[/green]")
                        except Exception as e:
                            self.console.print(f"[red]Could not save to memory: {e}[/red]")
                    else:
                        self.console.print("[yellow]Long-term memory not available[/yellow]")
                    continue
                
                # Process through autonomous or standard agent
                response = self.autonomous_execute(user_input)
                
                # Display response with appropriate styling
                title = "🧠 Autonomous Agent" if self.mode == "autonomous" else "🤖 Standard Agent"
                border_style = "cyan" if self.mode == "autonomous" else "yellow"
                
                panel = Panel(response, title=title, border_style=border_style)
                self.console.print(panel)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Unexpected error: {str(e)}[/red]")

def main():
    """Enhanced main function with autonomous capabilities"""
    app = AutonomousADE()
    app.run()

if __name__ == "__main__":
    main()
