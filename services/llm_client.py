"""
LLM Client Service for Code Review Assistant
Handles communication with OpenRouter API for code analysis
"""

import requests
import json
import os
from typing import List, Dict, Any, Optional
import time
from datetime import datetime

class CodeReviewLLM:
    """Client for interacting with OpenRouter API for code review"""
    
    def __init__(self):
        """Initialize the LLM client with API configuration"""
        # Force reload environment variables
        from dotenv import load_dotenv
        load_dotenv(override=True)
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "qwen/qwen-2.5-coder-32b-instruct:free"
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        # Debug: Print API key info (first 20 chars only for security)
        print(f"🔑 Using API Key: {self.api_key[:20]}... (length: {len(self.api_key)})")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "CodeReviewAssistant"
        }
    
    def review_code(self, file_contents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send code files to LLM for review
        
        Args:
            file_contents: List of dictionaries containing file info and content
            
        Returns:
            Dictionary with success status, review content, and metadata
        """
        try:
            # Prepare the prompt
            prompt = self._build_review_prompt(file_contents)
            
            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 4000,
                "stream": False
            }
            
            # Make the API request using the exact format from OpenRouter docs
            response = requests.post(
                url=self.base_url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=60
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse the response
            response_data = response.json()
            
            if 'choices' not in response_data or not response_data['choices']:
                return {
                    'success': False,
                    'error': 'No response from LLM',
                    'review': None,
                    'metadata': {}
                }
            
            # Extract the review content
            review_content = response_data['choices'][0]['message']['content']
            
            # Extract metadata
            metadata = {
                'model_used': self.model,
                'timestamp': datetime.now().isoformat(),
                'files_reviewed': len(file_contents),
                'file_names': [f['name'] for f in file_contents],
                'total_tokens': response_data.get('usage', {}).get('total_tokens', 0),
                'prompt_tokens': response_data.get('usage', {}).get('prompt_tokens', 0),
                'completion_tokens': response_data.get('usage', {}).get('completion_tokens', 0)
            }
            
            return {
                'success': True,
                'review': review_content,
                'metadata': metadata,
                'error': None
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout - LLM took too long to respond',
                'review': None,
                'metadata': {}
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API request failed: {str(e)}',
                'review': None,
                'metadata': {}
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Failed to parse API response: {str(e)}',
                'review': None,
                'metadata': {}
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'review': None,
                'metadata': {}
            }
    
    def _build_review_prompt(self, file_contents: List[Dict[str, Any]]) -> str:
        """
        Build a comprehensive prompt for code review
        
        Args:
            file_contents: List of file dictionaries
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            "You are an expert code reviewer. Please analyze the following code files and provide a comprehensive review.",
            "",
            "**Review Requirements:**",
            "1. **Code Quality & Readability**: Assess code clarity, naming conventions, and structure",
            "2. **Modularity & Architecture**: Evaluate code organization, separation of concerns, and reusability",
            "3. **Potential Bugs**: Identify logical errors, edge cases, and potential runtime issues",
            "4. **Security Issues**: Look for vulnerabilities, input validation, and security best practices",
            "5. **Performance**: Comment on efficiency, optimization opportunities, and resource usage",
            "6. **Best Practices**: Suggest improvements based on language-specific conventions",
            "7. **Suggestions**: Provide actionable recommendations for improvement",
            "",
            "**Response Format:**",
            "Please structure your response using clear markdown sections with headers:",
            "- ## Code Quality & Readability",
            "- ## Modularity & Architecture", 
            "- ## Potential Bugs",
            "- ## Security Issues",
            "- ## Performance Analysis",
            "- ## Best Practices",
            "- ## Improvement Suggestions",
            "",
            "**Code Files to Review:**",
            ""
        ]
        
        # Add each file's content
        for i, file_info in enumerate(file_contents, 1):
            prompt_parts.extend([
                f"### File {i}: {file_info['name']}",
                f"**Size:** {file_info['size']} bytes",
                f"**Type:** {file_info['type']}",
                "",
                "```",
                file_info['content'],
                "```",
                ""
            ])
        
        prompt_parts.extend([
            "",
            "Please provide a thorough analysis following the format above. Be specific and actionable in your recommendations."
        ])
        
        return "\n".join(prompt_parts)
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to OpenRouter API
        
        Returns:
            Dictionary with test results
        """
        try:
            # Simple test request
            test_payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, please respond with 'Connection successful'"
                    }
                ],
                "max_tokens": 10
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=json.dumps(test_payload),
                timeout=30
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            if 'choices' in response_data and response_data['choices']:
                return {
                    'success': True,
                    'message': 'Connection successful',
                    'response': response_data['choices'][0]['message']['content']
                }
            else:
                return {
                    'success': False,
                    'message': 'No response from API',
                    'response': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}',
                'response': None
            }

