#!/usr/bin/env python3
"""
AI Council CLI Example
======================

Shows how to use AI Council from command line.
"""

import sys
import asyncio
from ai_council.main import AICouncilApp

async def main():
    """Demonstrate CLI usage."""
    
    # Simulate command line arguments
    test_queries = [
        "What are the benefits of microservices architecture?",
        "Write a Python function to calculate fibonacci numbers",
        "Research the latest AI developments in 2024"
    ]
    
    print("🖥️  AI Council CLI Demonstration")
    print("="*50)
    
    app = AICouncilApp()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- CLI QUERY {i} ---")
        print(f"Query: {query}")
        
        # Simulate CLI arguments
        sys.argv = [
            "ai_council",
            "--query", query,
            "--mode", "balanced",
            "--verbose"
        ]
        
        try:
            await app.run()
            print("✅ CLI execution successful")
        except Exception as e:
            print(f"❌ CLI error: {e}")

if __name__ == "__main__":
    asyncio.run(main())