"""
Enhanced Integration Detector
Uses trained API knowledge to detect external integrations more accurately
"""

import json
import boto3
import os
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import ast

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedIntegrationDetector:
    """
    Enhanced integration detector using trained API knowledge
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize the Enhanced Integration Detector
        
        Args:
            region_name: AWS region for services
        """
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
        
        # Configuration
        self.knowledge_base_bucket = os.environ.get('API_KNOWLEDGE_BUCKET', 'api-knowledge-base')
        self.api_docs_table = os.environ.get('API_DOCS_TABLE', 'api-documentation')
        self.model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        
        # Load enhanced patterns
        self.enhanced_patterns = self._load_enhanced_patterns()
        
        # Basic patterns as fallback
        self.basic_patterns = {
            'import_patterns': [
                'requests', 'boto3', 'stripe', 'twilio', 'sendgrid', 'axios', 'fetch',
                'google-api-python-client', 'microsoft-graph', 'slack-sdk', 'github',
                'paypal-sdk', 'shopify-api', 'firebase', 'mongodb', 'redis', 'elasticsearch'
            ],
            'initialization_patterns': [
                'api_key', 'client_id', 'secret_key', 'access_token', 'bearer_token',
                'stripe.api_key', 'twilio_client', 'sendgrid_client', 'aws_access_key'
            ],
            'usage_patterns': [
                'requests.get', 'requests.post', 'stripe.Charge', 'twilio.messages',
                'sendgrid.send', 'boto3.client', 'firebase.auth', 'mongodb.collection'
            ]
        }
    
    def detect_integrations(self, code_content: str, filename: str, language: str) -> List[Dict[str, Any]]:
        """
        Detect external integrations in code using enhanced patterns
        
        Args:
            code_content: Code content to analyze
            filename: Name of the file
            language: Programming language
            
        Returns:
            List of detected integrations
        """
        integrations = []
        
        # Use AI-powered detection for complex patterns
        ai_integrations = self._detect_integrations_with_ai(code_content, filename, language)
        integrations.extend(ai_integrations)
        
        # Use pattern-based detection for known patterns
        pattern_integrations = self._detect_integrations_with_patterns(code_content, filename, language)
        integrations.extend(pattern_integrations)
        
        # Use AST-based detection for structured languages
        if language in ['python', 'javascript', 'typescript']:
            ast_integrations = self._detect_integrations_with_ast(code_content, filename, language)
            integrations.extend(ast_integrations)
        
        # Deduplicate and rank integrations
        unique_integrations = self._deduplicate_and_rank_integrations(integrations)
        
        return unique_integrations
    
    def _detect_integrations_with_ai(self, code_content: str, filename: str, language: str) -> List[Dict[str, Any]]:
        """
        Use AI to detect integrations based on trained knowledge
        
        Args:
            code_content: Code content
            filename: Filename
            language: Programming language
            
        Returns:
            List of AI-detected integrations
        """
        try:
            # Prepare code for AI analysis
            code_sample = code_content[:5000]  # Limit size for AI analysis
            
            prompt = f"""
            Analyze the following {language} code to detect external API integrations and third-party services.
            
            Code:
            {code_sample}
            
            Based on your knowledge of popular APIs and services, identify:
            
            1. **API Integrations**: External APIs being called (Stripe, Twilio, AWS, etc.)
            2. **Authentication**: How the code authenticates with external services
            3. **Data Flow**: What data is being sent/received
            4. **Service Purpose**: What business function this integration serves
            5. **Integration Type**: REST API, SDK, Webhook, etc.
            
            For each integration found, provide:
            - Service name and type
            - Confidence level (0.0 to 1.0)
            - Evidence from the code
            - Business purpose
            - Authentication method used
            - Key operations performed
            
            Format your response as JSON:
            {{
                "integrations": [
                    {{
                        "service": "Stripe",
                        "type": "Payment Processing",
                        "confidence": 0.95,
                        "evidence": ["stripe.Charge.create", "stripe.api_key"],
                        "business_purpose": "Process credit card payments",
                        "authentication": "API Key in header",
                        "operations": ["create_charge", "retrieve_customer"],
                        "integration_type": "SDK"
                    }}
                ]
            }}
            """
            
            response = self._call_bedrock(prompt)
            ai_result = json.loads(response)
            
            # Convert AI result to standard format
            integrations = []
            for integration in ai_result.get('integrations', []):
                integrations.append({
                    'service': integration.get('service', 'Unknown'),
                    'type': integration.get('type', 'Unknown'),
                    'confidence': integration.get('confidence', 0.5),
                    'evidence': integration.get('evidence', []),
                    'business_purpose': integration.get('business_purpose', ''),
                    'authentication': integration.get('authentication', ''),
                    'operations': integration.get('operations', []),
                    'integration_type': integration.get('integration_type', 'Unknown'),
                    'detection_method': 'ai',
                    'file': filename,
                    'language': language
                })
            
            return integrations
            
        except Exception as e:
            logger.error(f"Error in AI integration detection: {str(e)}")
            return []
    
    def _detect_integrations_with_patterns(self, code_content: str, filename: str, language: str) -> List[Dict[str, Any]]:
        """
        Detect integrations using pattern matching
        
        Args:
            code_content: Code content
            filename: Filename
            language: Programming language
            
        Returns:
            List of pattern-detected integrations
        """
        integrations = []
        
        # Combine enhanced and basic patterns
        all_patterns = {**self.enhanced_patterns, **self.basic_patterns}
        
        # Check import patterns
        for pattern in all_patterns.get('import_patterns', []):
            if self._pattern_matches(code_content, pattern):
                integration = self._create_integration_from_pattern(
                    pattern, 'import', code_content, filename, language
                )
                if integration:
                    integrations.append(integration)
        
        # Check initialization patterns
        for pattern in all_patterns.get('initialization_patterns', []):
            if self._pattern_matches(code_content, pattern):
                integration = self._create_integration_from_pattern(
                    pattern, 'initialization', code_content, filename, language
                )
                if integration:
                    integrations.append(integration)
        
        # Check usage patterns
        for pattern in all_patterns.get('usage_patterns', []):
            if self._pattern_matches(code_content, pattern):
                integration = self._create_integration_from_pattern(
                    pattern, 'usage', code_content, filename, language
                )
                if integration:
                    integrations.append(integration)
        
        return integrations
    
    def _detect_integrations_with_ast(self, code_content: str, filename: str, language: str) -> List[Dict[str, Any]]:
        """
        Detect integrations using AST analysis
        
        Args:
            code_content: Code content
            filename: Filename
            language: Programming language
            
        Returns:
            List of AST-detected integrations
        """
        integrations = []
        
        if language == 'python':
            integrations.extend(self._analyze_python_ast(code_content, filename))
        elif language in ['javascript', 'typescript']:
            integrations.extend(self._analyze_javascript_ast(code_content, filename))
        
        return integrations
    
    def _analyze_python_ast(self, code_content: str, filename: str) -> List[Dict[str, Any]]:
        """Analyze Python code using AST"""
        integrations = []
        
        try:
            tree = ast.parse(code_content)
            
            for node in ast.walk(tree):
                # Check import statements
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module_name = getattr(node, 'module', '') or ''
                    for alias in node.names:
                        full_name = f"{module_name}.{alias.name}" if module_name else alias.name
                        
                        # Check if this is a known integration
                        integration = self._identify_integration_from_import(full_name, 'python')
                        if integration:
                            integration.update({
                                'detection_method': 'ast',
                                'file': filename,
                                'language': 'python',
                                'line': node.lineno,
                                'evidence': [full_name]
                            })
                            integrations.append(integration)
                
                # Check function calls
                elif isinstance(node, ast.Call):
                    func_name = self._get_function_name(node)
                    if func_name:
                        integration = self._identify_integration_from_call(func_name, 'python')
                        if integration:
                            integration.update({
                                'detection_method': 'ast',
                                'file': filename,
                                'language': 'python',
                                'line': node.lineno,
                                'evidence': [func_name]
                            })
                            integrations.append(integration)
        
        except SyntaxError as e:
            logger.error(f"Syntax error in {filename}: {str(e)}")
        
        return integrations
    
    def _analyze_javascript_ast(self, code_content: str, filename: str) -> List[Dict[str, Any]]:
        """Analyze JavaScript/TypeScript code (simplified regex-based approach)"""
        integrations = []
        
        # Extract require/import statements
        import_patterns = [
            r'require\(["\']([^"\']+)["\']\)',
            r'import\s+.*\s+from\s+["\']([^"\']+)["\']',
            r'import\s+["\']([^"\']+)["\']'
        ]
        
        for pattern in import_patterns:
            matches = re.finditer(pattern, code_content)
            for match in matches:
                module_name = match.group(1)
                integration = self._identify_integration_from_import(module_name, 'javascript')
                if integration:
                    integration.update({
                        'detection_method': 'ast',
                        'file': filename,
                        'language': 'javascript',
                        'evidence': [module_name]
                    })
                    integrations.append(integration)
        
        return integrations
    
    def _identify_integration_from_import(self, import_name: str, language: str) -> Optional[Dict[str, Any]]:
        """Identify integration from import statement"""
        import_lower = import_name.lower()
        
        # Known service mappings
        service_mappings = {
            'stripe': {
                'service': 'Stripe',
                'type': 'Payment Processing',
                'confidence': 0.9,
                'business_purpose': 'Process payments and manage billing',
                'authentication': 'API Key',
                'integration_type': 'SDK'
            },
            'twilio': {
                'service': 'Twilio',
                'type': 'Communication',
                'confidence': 0.9,
                'business_purpose': 'Send SMS, make calls, handle messaging',
                'authentication': 'Account SID and Auth Token',
                'integration_type': 'SDK'
            },
            'boto3': {
                'service': 'AWS',
                'type': 'Cloud Services',
                'confidence': 0.9,
                'business_purpose': 'Access AWS cloud services',
                'authentication': 'AWS Credentials',
                'integration_type': 'SDK'
            },
            'requests': {
                'service': 'HTTP Client',
                'type': 'HTTP Requests',
                'confidence': 0.7,
                'business_purpose': 'Make HTTP requests to external APIs',
                'authentication': 'Various (API Key, OAuth, etc.)',
                'integration_type': 'HTTP Client'
            },
            'axios': {
                'service': 'HTTP Client',
                'type': 'HTTP Requests',
                'confidence': 0.7,
                'business_purpose': 'Make HTTP requests to external APIs',
                'authentication': 'Various (API Key, OAuth, etc.)',
                'integration_type': 'HTTP Client'
            }
        }
        
        for key, service_info in service_mappings.items():
            if key in import_lower:
                return service_info.copy()
        
        return None
    
    def _identify_integration_from_call(self, call_name: str, language: str) -> Optional[Dict[str, Any]]:
        """Identify integration from function call"""
        call_lower = call_name.lower()
        
        # Known API call patterns
        call_mappings = {
            'stripe.charge.create': {
                'service': 'Stripe',
                'type': 'Payment Processing',
                'confidence': 0.95,
                'business_purpose': 'Create payment charges',
                'authentication': 'API Key',
                'integration_type': 'SDK'
            },
            'twilio.messages.create': {
                'service': 'Twilio',
                'type': 'Communication',
                'confidence': 0.95,
                'business_purpose': 'Send SMS messages',
                'authentication': 'Account SID and Auth Token',
                'integration_type': 'SDK'
            },
            'requests.get': {
                'service': 'HTTP Client',
                'type': 'HTTP Requests',
                'confidence': 0.6,
                'business_purpose': 'Make GET requests to external APIs',
                'authentication': 'Various',
                'integration_type': 'HTTP Client'
            },
            'requests.post': {
                'service': 'HTTP Client',
                'type': 'HTTP Requests',
                'confidence': 0.6,
                'business_purpose': 'Make POST requests to external APIs',
                'authentication': 'Various',
                'integration_type': 'HTTP Client'
            }
        }
        
        for key, service_info in call_mappings.items():
            if key in call_lower:
                return service_info.copy()
        
        return None
    
    def _pattern_matches(self, content: str, pattern: str) -> bool:
        """Check if pattern matches in content"""
        return pattern.lower() in content.lower()
    
    def _create_integration_from_pattern(self, pattern: str, pattern_type: str, 
                                       content: str, filename: str, language: str) -> Optional[Dict[str, Any]]:
        """Create integration object from pattern match"""
        integration = self._identify_integration_from_import(pattern, language)
        if integration:
            integration.update({
                'detection_method': 'pattern',
                'pattern_type': pattern_type,
                'file': filename,
                'language': language,
                'evidence': [pattern]
            })
            return integration
        return None
    
    def _get_function_name(self, node: ast.Call) -> Optional[str]:
        """Extract function name from AST call node"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return f"{self._get_attr_name(node.func)}.{node.func.attr}"
        return None
    
    def _get_attr_name(self, node: ast.Attribute) -> str:
        """Get attribute name from AST attribute node"""
        if isinstance(node.value, ast.Name):
            return node.value.id
        elif isinstance(node.value, ast.Attribute):
            return f"{self._get_attr_name(node.value)}.{node.value.attr}"
        return ""
    
    def _deduplicate_and_rank_integrations(self, integrations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates and rank integrations by confidence"""
        # Group by service
        service_groups = {}
        for integration in integrations:
            service = integration.get('service', 'Unknown')
            if service not in service_groups:
                service_groups[service] = []
            service_groups[service].append(integration)
        
        # Select best integration for each service
        unique_integrations = []
        for service, group in service_groups.items():
            # Sort by confidence and select the best one
            best_integration = max(group, key=lambda x: x.get('confidence', 0))
            
            # Merge evidence from all detections
            all_evidence = []
            for integration in group:
                all_evidence.extend(integration.get('evidence', []))
            best_integration['evidence'] = list(set(all_evidence))
            
            unique_integrations.append(best_integration)
        
        # Sort by confidence
        unique_integrations.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return unique_integrations
    
    def _load_enhanced_patterns(self) -> Dict[str, List[str]]:
        """Load enhanced patterns from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.knowledge_base_bucket,
                Key="integration-patterns/enhanced_patterns.json"
            )
            patterns = json.loads(response['Body'].read())
            return patterns
        except Exception as e:
            logger.warning(f"Could not load enhanced patterns: {str(e)}")
            return {}
    
    def _call_bedrock(self, prompt: str, max_tokens: int = 4000) -> str:
        """Call AWS Bedrock"""
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
