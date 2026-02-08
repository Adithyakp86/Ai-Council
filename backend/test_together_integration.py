"""Test script for Together AI integration."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.cloud_ai.together_adapter import TogetherAdapter


def test_together_integration():
    """Test Together AI integration with all supported models."""
    
    # Get API key from environment
    api_key = os.getenv('TOGETHER_API_KEY')
    
    if not api_key:
        print('❌ TOGETHER_API_KEY not found in environment')
        print('   Please add your Together AI API key to backend/.env')
        print('   Get your key from: https://api.together.xyz')
        return False
    
    print('=' * 70)
    print('TOGETHER AI INTEGRATION TEST')
    print('=' * 70)
    print()
    print('Testing Together AI integration with all supported models...')
    print()
    
    # Test cases for each model
    test_cases = [
        {
            'name': 'Mixtral-8x7B-Instruct',
            'model_id': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
            'prompt': 'What is 2+2? Answer in one word.',
            'description': 'Fast reasoning and code generation'
        },
        {
            'name': 'Llama-2-70B-Chat',
            'model_id': 'togethercomputer/llama-2-70b-chat',
            'prompt': 'Say hello in one friendly sentence.',
            'description': 'Research and creative output'
        },
        {
            'name': 'Nous-Hermes-2-Yi-34B',
            'model_id': 'NousResearch/Nous-Hermes-2-Yi-34B',
            'prompt': 'Write a haiku about artificial intelligence.',
            'description': 'Balanced multi-task performance'
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f'{i}. Testing {test["name"]}')
        print(f'   Model ID: {test["model_id"]}')
        print(f'   Use Case: {test["description"]}')
        print(f'   Prompt: "{test["prompt"]}"')
        print()
        
        try:
            # Create adapter
            adapter = TogetherAdapter(test['model_id'], api_key)
            
            # Generate response
            print('   Generating response...')
            response = adapter.generate_response(
                prompt=test['prompt'],
                temperature=0.7,
                max_tokens=200
            )
            
            # Display response
            print(f'   Response: {response.strip()}')
            print()
            print('   ✅ Success!')
            results.append(True)
            
        except Exception as e:
            print(f'   ❌ Error: {str(e)}')
            results.append(False)
        
        print()
        print('-' * 70)
        print()
    
    # Summary
    print('=' * 70)
    print('TEST SUMMARY')
    print('=' * 70)
    print()
    
    success_count = sum(results)
    total_count = len(results)
    
    for i, (test, result) in enumerate(zip(test_cases, results), 1):
        status = '✅ PASS' if result else '❌ FAIL'
        print(f'{i}. {test["name"]}: {status}')
    
    print()
    print(f'Results: {success_count}/{total_count} tests passed')
    print()
    
    if success_count == total_count:
        print('🎉 All Together AI models are working correctly!')
        print()
        print('Next steps:')
        print('1. Submit a test query through the web interface')
        print('2. Monitor costs in the Together AI dashboard')
        print('3. Configure other providers for redundancy')
        print()
        return True
    else:
        print('⚠️  Some tests failed. Please check:')
        print('1. Your API key is valid and has credits')
        print('2. Your internet connection is working')
        print('3. Together AI service is operational (https://status.together.ai)')
        print()
        return False


if __name__ == '__main__':
    success = test_together_integration()
    sys.exit(0 if success else 1)
