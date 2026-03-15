#!/usr/bin/env python3
"""
Google Gemini AI Client for Code-to-BRD System
Free alternative to AWS Bedrock
"""

import google.generativeai as genai
import json
import os
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    """Google Gemini AI client for BRD generation"""
    
    def __init__(self, api_key: str = None):
        """Initialize Gemini client"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def generate_brd(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate BRD using Gemini"""
        try:
            prompt = self._create_brd_prompt(analysis_results)
            response = self.model.generate_content(prompt)
            
            return {
                "brd_content": response.text,
                "model_used": "gemini-1.5-flash",
                "generation_timestamp": self._get_timestamp()
            }
        except Exception as e:
            logger.error(f"Error generating BRD: {str(e)}")
            raise
    
    def generate_use_cases(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate use cases using Gemini"""
        try:
            prompt = self._create_usecase_prompt(analysis_results)
            response = self.model.generate_content(prompt)
            
            return {
                "usecase_content": response.text,
                "model_used": "gemini-1.5-flash",
                "generation_timestamp": self._get_timestamp()
            }
        except Exception as e:
            logger.error(f"Error generating use cases: {str(e)}")
            raise
    
    def generate_tests(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test cases using Gemini"""
        try:
            prompt = self._create_test_prompt(analysis_results)
            response = self.model.generate_content(prompt)
            
            return {
                "test_content": response.text,
                "model_used": "gemini-1.5-flash",
                "generation_timestamp": self._get_timestamp()
            }
        except Exception as e:
            logger.error(f"Error generating tests: {str(e)}")
            raise
    
    def _create_brd_prompt(self, analysis_results: Dict[str, Any]) -> str:
        """Create BRD generation prompt"""
        return f"""
You are a business analyst expert. Analyze the following code analysis results and generate a comprehensive Business Requirements Document (BRD).

Code Analysis Results:
{json.dumps(analysis_results, indent=2)}

Please generate a BRD that includes:
1. Executive Summary
2. Business Objectives
3. Functional Requirements
4. Non-Functional Requirements
5. User Stories
6. Acceptance Criteria
7. Assumptions and Dependencies

Format the output as a professional BRD document suitable for stakeholders.
"""
    
    def _create_usecase_prompt(self, analysis_results: Dict[str, Any]) -> str:
        """Create use case generation prompt"""
        return f"""
You are a business analyst expert. Based on the following code analysis, generate detailed use cases and business scenarios.

Code Analysis Results:
{json.dumps(analysis_results, indent=2)}

Please generate:
1. Primary Use Cases
2. Secondary Use Cases
3. Edge Cases
4. Business Scenarios
5. User Journeys

Format as a comprehensive use case document.
"""
    
    def _create_test_prompt(self, analysis_results: Dict[str, Any]) -> str:
        """Create test generation prompt"""
        return f"""
You are a QA engineer expert. Based on the following code analysis, generate comprehensive test cases.

Code Analysis Results:
{json.dumps(analysis_results, indent=2)}

Please generate:
1. Unit Test Cases
2. Integration Test Cases
3. API Test Cases
4. End-to-End Test Cases
5. Performance Test Cases

Format as detailed test specifications with test data and expected results.
"""
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
