#!/usr/bin/env python3
"""
AI Council - How to Use Guide
=============================

This script shows you exactly how to use AI Council in different ways.
"""

def show_usage_guide():
    """Display comprehensive usage guide."""
    
    print("🎯 AI COUNCIL - HOW TO USE")
    print("="*50)
    
    print("\n1. 📚 BASIC EXAMPLES (Ready to run)")
    print("   Run these examples to see AI Council in action:")
    print("   ")
    print("   • Basic Infrastructure Demo:")
    print("     python examples/basic_usage.py")
    print("   ")
    print("   • Complete Integration Demo:")
    print("     python examples/complete_integration.py")
    print("   ")
    print("   • Orchestration Layer Demo:")
    print("     python examples/orchestration_example.py")
    print("   ")
    print("   • Configuration Management Demo:")
    print("     python examples/configuration_example.py")
    
    print("\n2. 🔧 PROGRAMMATIC USAGE")
    print("   Use AI Council in your Python code:")
    print("   ")
    print("   ```python")
    print("   from ai_council.factory import AICouncilFactory")
    print("   from ai_council.core.models import ExecutionMode")
    print("   ")
    print("   # Initialize")
    print("   factory = AICouncilFactory()")
    print("   ai_council = factory.create_ai_council_sync()")
    print("   ")
    print("   # Process request")
    print("   response = ai_council.process_request_sync(")
    print("       'Explain quantum computing',")
    print("       ExecutionMode.BALANCED")
    print("   )")
    print("   ")
    print("   print(response.content)")
    print("   ```")
    
    print("\n3. ⚙️  EXECUTION MODES")
    print("   Choose the right mode for your needs:")
    print("   ")
    print("   • FAST: Quick responses, lower cost")
    print("     - Best for: Simple questions, quick tasks")
    print("     - Trade-off: Speed vs Quality")
    print("   ")
    print("   • BALANCED: Good quality, reasonable cost")
    print("     - Best for: Most general use cases")
    print("     - Trade-off: Balanced approach")
    print("   ")
    print("   • BEST_QUALITY: Highest quality, higher cost")
    print("     - Best for: Complex analysis, critical tasks")
    print("     - Trade-off: Quality vs Cost/Speed")
    
    print("\n4. 📝 TASK TYPES")
    print("   AI Council handles different types of tasks:")
    print("   ")
    print("   • reasoning: Logical analysis and problem solving")
    print("   • research: Information gathering and analysis")
    print("   • code_generation: Writing and debugging code")
    print("   • creative_output: Creative writing and content")
    print("   • fact_checking: Verifying information accuracy")
    print("   • verification: Validating results and claims")
    
    print("\n5. 🎛️  CONFIGURATION")
    print("   Customize AI Council for your needs:")
    print("   ")
    print("   • Use config/ai_council_example.yaml as template")
    print("   • Modify execution modes, models, and routing rules")
    print("   • See examples/configuration_example.py for details")
    
    print("\n6. 🧪 TESTING")
    print("   Validate your setup:")
    print("   ")
    print("   • Run all tests: python -m pytest tests/ -v")
    print("   • Validate infrastructure: python scripts/validate_infrastructure.py")
    print("   • Check system status: See system_validation_report.md")
    
    print("\n7. 🚀 PRODUCTION DEPLOYMENT")
    print("   For production use:")
    print("   ")
    print("   • Replace mock models with real AI model APIs")
    print("   • Configure proper API keys and endpoints")
    print("   • Set up monitoring and logging")
    print("   • Use production-grade configuration")
    
    print("\n8. 📖 NEXT STEPS")
    print("   ")
    print("   1. Start with: python examples/basic_usage.py")
    print("   2. Explore: python examples/complete_integration.py")
    print("   3. Customize: Modify config/ai_council_example.yaml")
    print("   4. Integrate: Use the programmatic API in your code")
    print("   5. Deploy: Set up real AI models for production")
    
    print("\n" + "="*50)
    print("🎉 AI Council is ready to orchestrate your AI models!")
    print("Start with the basic examples and work your way up.")
    print("="*50)

if __name__ == "__main__":
    show_usage_guide()