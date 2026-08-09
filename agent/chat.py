"""
Chat interface for the Airport Investment Agent.
Provides conversational interaction with the agent.
"""

from typing import Optional
from agent.agent import AirportInvestmentAgent
from config.settings import Settings
import textwrap


class ChatInterface:
    """Interactive chat interface for the Airport Investment Agent."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the chat interface."""
        self.settings = settings or Settings()
        self.agent = AirportInvestmentAgent(self.settings)
        self.conversation_history = []
        self.session_active = True
    
    def display_welcome(self):
        """Display welcome message."""
        print("\n" + "=" * 70)
        print("AIRPORT INVESTMENT INTELLIGENCE AGENT")
        print("=" * 70)
        print("\nWelcome! I'm your AI assistant for airport investment analysis.")
        print("I can help you identify promising airport expansion opportunities.\n")
        print("EXAMPLE QUESTIONS:")
        print("  • Which airports in New England are strong candidates for terminal expansion?")
        print("  • Compare LA and Santa Ana airport congestion levels")
        print("  • What is the percentage of long haul flights out of Anchorage airport?")
        print("  • What is the unmet flight demand in SFO airport and why?\n")
        print("SUPPORTED AIRPORTS: LAX, SNA, SFO, BOS, MHT, PVD, BDL, ANC\n")
        print("Type 'help' for commands, 'quit' to exit.\n")
        print("=" * 70 + "\n")
    
    def display_help(self):
        """Display help information."""
        help_text = """
COMMANDS:
  quit           - Exit the chat
  help           - Show this help message
  report [CODE]  - Generate detailed report for airport (e.g., report LAX)
  compare [A,B]  - Compare two airports (e.g., compare LAX,SNA)
  region [REGION]- Analyze all airports in a region (e.g., region "New England")

QUERY TYPES:
  1. Expansion opportunities: "Which airports in [region] need expansion?"
  2. Congestion comparison: "Compare [airport1] and [airport2] congestion"
  3. Flight statistics: "What percentage of [airport] flights are long-haul?"
  4. Unmet demand: "What is the capacity situation at [airport]?"
  5. General questions: Ask anything about airport investments!

METRICS EXPLAINED:
  Score (0-10):
    8.0+  = STRONG BUY
    6.5-8 = BUY
    5.0-6.5 = HOLD
    3.0-5 = WEAK
    <3.0  = AVOID
"""
        print(help_text)
    
    def format_response(self, text: str, width: int = 70) -> str:
        """Format response text for readability."""
        return '\n'.join(textwrap.wrap(text, width=width))
    
    def process_command(self, user_input: str) -> bool:
        """
        Process user command.
        Returns False if user wants to quit, True otherwise.
        """
        command = user_input.strip().lower()
        
        if command == 'quit':
            print("\nThank you for using the Airport Investment Agent. Goodbye!")
            return False
        
        elif command == 'help':
            self.display_help()
            return True
        
        elif command.startswith('report'):
            parts = command.split()
            if len(parts) > 1:
                airport_code = parts[1].upper()
                print(f"\nGenerating report for {airport_code}...\n")
                try:
                    report = self.agent.generate_report(airport_code)
                    print(report)
                except Exception as e:
                    print(f"Error generating report: {e}")
            else:
                print("Usage: report [AIRPORT_CODE]")
            return True
        
        elif command.startswith('compare'):
            parts = command.split()
            if len(parts) > 1:
                airports_str = parts[1]
                if ',' in airports_str:
                    airports = [a.strip().upper() for a in airports_str.split(',')]
                    print(f"\nComparing airports: {', '.join(airports)}...\n")
                    try:
                        response, _ = self.agent.process_query(
                            f"Compare {' and '.join(airports)} airports"
                        )
                        print(response)
                    except Exception as e:
                        print(f"Error comparing airports: {e}")
                else:
                    print("Usage: compare [AIRPORT1],[AIRPORT2]")
            return True
        
        elif command.startswith('region'):
            region = command.replace('region', '').strip()
            if region:
                print(f"\nAnalyzing {region} region...\n")
                try:
                    response, _ = self.agent.process_query(
                        f"Analyze airports in {region}"
                    )
                    print(response)
                except Exception as e:
                    print(f"Error analyzing region: {e}")
            else:
                print("Usage: region [REGION_NAME]")
            return True
        
        else:
            return True
    
    def chat(self):
        """Start the chat interface."""
        self.display_welcome()
        
        while self.session_active:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Check if it's a command
                if user_input.lower() in ['quit', 'help'] or user_input.lower().startswith('report') or \
                   user_input.lower().startswith('compare') or user_input.lower().startswith('region'):
                    if not self.process_command(user_input):
                        self.session_active = False
                    continue
                
                # Process as natural language query
                print("\nAgent: Analyzing your question...\n")
                
                response, data = self.agent.process_query(user_input)
                print(response)
                
                # Store in conversation history
                self.conversation_history.append({
                    'user': user_input,
                    'agent': response
                })
                
                print()
            
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                self.session_active = False
            
            except Exception as e:
                print(f"\nError processing query: {e}")
                print("Please try again or type 'help' for available commands.\n")
    
    def save_conversation(self, filepath: str):
        """Save conversation history to file."""
        try:
            with open(filepath, 'w') as f:
                for turn in self.conversation_history:
                    f.write(f"User: {turn['user']}\n")
                    f.write(f"Agent: {turn['agent']}\n")
                    f.write("-" * 70 + "\n\n")
            print(f"Conversation saved to {filepath}")
        except Exception as e:
            print(f"Error saving conversation: {e}")
