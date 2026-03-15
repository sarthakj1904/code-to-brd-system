#!/usr/bin/env python3
"""
Hugging Face Inference API Client for Code-to-BRD System
Free alternative to AWS Bedrock using open source models
"""

import requests
import json
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class HuggingFaceClient:
    """Hugging Face Inference API client for BRD generation"""
    
    def __init__(self, api_key: str = None):
        """Initialize Hugging Face client"""
        self.api_key = api_key or os.getenv('HUGGINGFACE_API_KEY')
        self.base_url = "https://api-inference.huggingface.co/models"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else None
        }
        
        # Use free models that don't require API key
        self.models = {
            "text_generation": "microsoft/DialoGPT-medium",
            "summarization": "facebook/bart-large-cnn",
            "question_answering": "deepset/roberta-base-squad2"
        }
    
    def generate_brd(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate BRD using Hugging Face models"""
        try:
            # Use a text generation model for BRD creation
            prompt = self._create_brd_prompt(analysis_results)
            response = self._call_model("text_generation", prompt)
            
            return {
                "brd_content": response,
                "model_used": "huggingface-dialogpt",
                "generation_timestamp": self._get_timestamp()
            }
        except Exception as e:
            logger.error(f"Error generating BRD: {str(e)}")
            raise
    
    def generate_use_cases(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate use cases using Hugging Face models"""
        try:
            prompt = self._create_usecase_prompt(analysis_results)
            response = self._call_model("text_generation", prompt)
            
            return {
                "usecase_content": response,
                "model_used": "huggingface-dialogpt",
                "generation_timestamp": self._get_timestamp()
            }
        except Exception as e:
            logger.error(f"Error generating use cases: {str(e)}")
            raise
    
    def generate_tests(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test cases using Hugging Face models"""
        try:
            prompt = self._create_test_prompt(analysis_results)
            response = self._call_model("text_generation", prompt)
            
            return {
                "test_content": response,
                "model_used": "huggingface-dialogpt",
                "generation_timestamp": self._get_timestamp()
            }
        except Exception as e:
            logger.error(f"Error generating tests: {str(e)}")
            raise
    
    def _call_model(self, model_type: str, prompt: str) -> str:
        """Call Hugging Face model"""
        model_name = self.models[model_type]
        url = f"{self.base_url}/{model_name}"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 1000,
                "temperature": 0.7,
                "do_sample": True
            }
        }
        
        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            return str(result)
        else:
            raise Exception(f"API call failed: {response.status_code} - {response.text}")
    
    def _create_brd_prompt(self, analysis_results: Dict[str, Any]) -> str:
        """Create BRD generation prompt"""
        return f"""
Generate a Business Requirements Document for this code analysis:
{json.dumps(analysis_results, indent=2)}

Include: Executive Summary, Business Objectives, Functional Requirements, User Stories.
"""
    
    def _create_usecase_prompt(self, analysis_results: Dict[str, Any]) -> str:
        """Create use case generation prompt"""
        return f"""
Generate use cases for this code analysis:
{json.dumps(analysis_results, indent=2)}

Include: Primary use cases, Secondary use cases, Edge cases, Business scenarios.
"""
    
    def _create_test_prompt(self, analysis_results: Dict[str, Any]) -> str:
        """Create test generation prompt"""
        return f"""
Generate test cases for this code analysis:
{json.dumps(analysis_results, indent=2)}

Include: Unit tests, Integration tests, API tests, End-to-end tests.
"""
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
