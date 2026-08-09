"""
Main application entry point for the Airport Investment Agent.
"""

import logging
import sys
from agent.chat import ChatInterface
from config.settings import Settings


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Initialize and run the Airport Investment Agent."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        settings = Settings()
        logger.info("Starting Airport Investment Agent...")
        
        # Launch interactive chat interface
        chat = ChatInterface(settings)
        chat.chat()
        
    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running agent: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

