"""
BRD Generator using AWS Bedrock
Handles the generation of Business Requirement Documents
"""

import json
import boto3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class BRDGenerator:
    """
    Generates Business Requirement Documents using AWS Bedrock
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize the BRD Generator
        
        Args:
            region_name: AWS region for Bedrock service
        """
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
        self.model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        
    def generate_brd(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete BRD from code analysis results
        
        Args:
            analysis_results: Results from code analysis
            
        Returns:
            Dictionary containing BRD content and metadata
        """
        try:
            logger.info("Starting BRD generation")
            
            # Generate the main BRD content
            brd_content = self._generate_main_brd(analysis_results)
            
            # Extract sections from the generated content
            sections = self._extract_brd_sections(brd_content)
            
            # Generate additional detailed sections if needed
            detailed_sections = self._generate_detailed_sections(analysis_results, sections)
            
            return {
                'brd_content': brd_content,
                'sections': sections,
                'detailed_sections': detailed_sections,
                'generation_timestamp': datetime.utcnow().isoformat(),
                'model_used': self.model_id,
                'analysis_summary': self._create_analysis_summary(analysis_results)
            }
            
        except Exception as e:
            logger.error(f"Error generating BRD: {str(e)}")
            raise
    
    def _generate_main_brd(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate the main BRD content using Bedrock
        """
        from ..prompts.brd_prompts import get_brd_generation_prompt
        
        prompt = get_brd_generation_prompt(analysis_results)
        
        try:
            response = self._call_bedrock(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error generating main BRD: {str(e)}")
            raise
    
    def _generate_detailed_sections(self, analysis_results: Dict[str, Any], sections: Dict[str, str]) -> Dict[str, str]:
        """
        Generate detailed sections for areas that need more depth
        """
        detailed_sections = {}
        
        # Generate detailed functional requirements if the section is too brief
        if 'functional_requirements' in sections and len(sections['functional_requirements']) < 500:
            detailed_sections['functional_requirements'] = self._generate_detailed_functional_requirements(analysis_results)
        
        # Generate detailed system architecture if needed
        if 'system_architecture' in sections and len(sections['system_architecture']) < 300:
            detailed_sections['system_architecture'] = self._generate_detailed_system_architecture(analysis_results)
        
        # Generate detailed integration requirements if needed
        if 'integration_requirements' in sections and len(sections['integration_requirements']) < 200:
            detailed_sections['integration_requirements'] = self._generate_detailed_integration_requirements(analysis_results)
        
        return detailed_sections
    
    def _generate_detailed_functional_requirements(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate detailed functional requirements
        """
        from ..prompts.brd_prompts import get_functional_requirements_prompt
        
        prompt = get_functional_requirements_prompt(analysis_results)
        
        try:
            response = self._call_bedrock(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error generating detailed functional requirements: {str(e)}")
            return "Error generating detailed functional requirements"
    
    def _generate_detailed_system_architecture(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate detailed system architecture
        """
        from ..prompts.brd_prompts import get_system_architecture_prompt
        
        prompt = get_system_architecture_prompt(analysis_results)
        
        try:
            response = self._call_bedrock(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error generating detailed system architecture: {str(e)}")
            return "Error generating detailed system architecture"
    
    def _generate_detailed_integration_requirements(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate detailed integration requirements
        """
        from ..prompts.brd_prompts import get_integration_requirements_prompt
        
        prompt = get_integration_requirements_prompt(analysis_results)
        
        try:
            response = self._call_bedrock(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error generating detailed integration requirements: {str(e)}")
            return "Error generating detailed integration requirements"
    
    def _call_bedrock(self, prompt: str, max_tokens: int = 4000) -> str:
        """
        Call AWS Bedrock with the given prompt
        
        Args:
            prompt: The prompt to send to Bedrock
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text from Bedrock
        """
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Error calling Bedrock: {str(e)}")
            raise
    
    def _extract_brd_sections(self, brd_content: str) -> Dict[str, str]:
        """
        Extract sections from the generated BRD content
        
        Args:
            brd_content: The full BRD content
            
        Returns:
            Dictionary mapping section names to content
        """
        sections = {}
        current_section = None
        current_content = []
        
        lines = brd_content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check if this is a section header
            if self._is_section_header(line):
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = self._normalize_section_name(line)
                current_content = []
            else:
                # Add content to current section
                if current_section:
                    current_content.append(line)
        
        # Save the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _is_section_header(self, line: str) -> bool:
        """
        Check if a line is a section header
        
        Args:
            line: Line to check
            
        Returns:
            True if the line is a section header
        """
        if not line:
            return False
        
        # Check for common section header patterns
        header_patterns = [
            line.startswith('#'),
            line.isupper() and len(line) > 5,
            line.startswith('##'),
            line.startswith('###'),
            'EXECUTIVE SUMMARY' in line.upper(),
            'BUSINESS OBJECTIVES' in line.upper(),
            'FUNCTIONAL REQUIREMENTS' in line.upper(),
            'NON-FUNCTIONAL REQUIREMENTS' in line.upper(),
            'SYSTEM ARCHITECTURE' in line.upper(),
            'INTEGRATION REQUIREMENTS' in line.upper(),
            'SECURITY REQUIREMENTS' in line.upper(),
            'PERFORMANCE REQUIREMENTS' in line.upper(),
            'RISK ASSESSMENT' in line.upper(),
            'ACCEPTANCE CRITERIA' in line.upper()
        ]
        
        return any(header_patterns)
    
    def _normalize_section_name(self, header: str) -> str:
        """
        Normalize section header to a standard name
        
        Args:
            header: Section header text
            
        Returns:
            Normalized section name
        """
        header_upper = header.upper()
        
        # Remove markdown formatting
        header = header.replace('#', '').replace('*', '').strip()
        
        # Map to standard section names
        section_mapping = {
            'EXECUTIVE SUMMARY': 'executive_summary',
            'BUSINESS OBJECTIVES': 'business_objectives',
            'FUNCTIONAL REQUIREMENTS': 'functional_requirements',
            'NON-FUNCTIONAL REQUIREMENTS': 'non_functional_requirements',
            'SYSTEM ARCHITECTURE': 'system_architecture',
            'DATA REQUIREMENTS': 'data_requirements',
            'INTEGRATION REQUIREMENTS': 'integration_requirements',
            'SECURITY REQUIREMENTS': 'security_requirements',
            'PERFORMANCE REQUIREMENTS': 'performance_requirements',
            'RISK ASSESSMENT': 'risk_assessment',
            'ACCEPTANCE CRITERIA': 'acceptance_criteria'
        }
        
        for key, value in section_mapping.items():
            if key in header_upper:
                return value
        
        # Default to a normalized version of the header
        return header.lower().replace(' ', '_').replace('#', '').replace('*', '')
    
    def _create_analysis_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of the analysis results
        
        Args:
            analysis_results: Results from code analysis
            
        Returns:
            Summary of analysis results
        """
        return {
            'languages_analyzed': analysis_results.get('languages_analyzed', []),
            'total_functions': len(analysis_results.get('functions_found', [])),
            'total_classes': len(analysis_results.get('classes_found', [])),
            'total_api_endpoints': len(analysis_results.get('api_endpoints', [])),
            'total_database_operations': len(analysis_results.get('database_operations', [])),
            'total_external_integrations': len(analysis_results.get('external_integrations', [])),
            'analysis_timestamp': analysis_results.get('analysis_timestamp', 'unknown')
        }
    
    def validate_brd_content(self, brd_content: str) -> Dict[str, Any]:
        """
        Validate the generated BRD content
        
        Args:
            brd_content: The BRD content to validate
            
        Returns:
            Validation results
        """
        validation_results = {
            'is_valid': True,
            'issues': [],
            'sections_found': [],
            'word_count': len(brd_content.split()),
            'character_count': len(brd_content)
        }
        
        # Check for required sections
        required_sections = [
            'executive summary',
            'business objectives',
            'functional requirements',
            'system architecture'
        ]
        
        content_lower = brd_content.lower()
        
        for section in required_sections:
            if section in content_lower:
                validation_results['sections_found'].append(section)
            else:
                validation_results['issues'].append(f"Missing required section: {section}")
                validation_results['is_valid'] = False
        
        # Check content quality
        if validation_results['word_count'] < 500:
            validation_results['issues'].append("BRD content is too short (less than 500 words)")
            validation_results['is_valid'] = False
        
        if validation_results['word_count'] > 10000:
            validation_results['issues'].append("BRD content is very long (more than 10,000 words)")
        
        return validation_results
