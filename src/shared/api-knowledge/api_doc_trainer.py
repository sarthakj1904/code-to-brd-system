"""
API Documentation Trainer
Trains models on API documentation to improve external integration detection
"""

import json
import requests
import boto3
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import hashlib

# Configure logging
logger = logging.getLogger(__name__)

class APIDocTrainer:
    """
    Trains models on API documentation for better integration detection
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize the API Documentation Trainer
        
        Args:
            region_name: AWS region for services
        """
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        
        # Configuration
        self.knowledge_base_bucket = os.environ.get('API_KNOWLEDGE_BUCKET', 'api-knowledge-base')
        self.api_docs_table = os.environ.get('API_DOCS_TABLE', 'api-documentation')
        self.model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        
        # Popular API services to train on
        self.api_services = {
            'stripe': {
                'base_url': 'https://stripe.com/docs/api',
                'patterns': ['stripe', 'stripe-python', 'stripe-node'],
                'endpoints': ['/charges', '/customers', '/payments', '/subscriptions']
            },
            'twilio': {
                'base_url': 'https://www.twilio.com/docs',
                'patterns': ['twilio', 'twilio-python', 'twilio-node'],
                'endpoints': ['/sms', '/voice', '/video', '/messaging']
            },
            'sendgrid': {
                'base_url': 'https://docs.sendgrid.com/api-reference',
                'patterns': ['sendgrid', 'sendgrid-python', 'sendgrid-node'],
                'endpoints': ['/mail-send', '/contacts', '/templates']
            },
            'aws': {
                'base_url': 'https://docs.aws.amazon.com',
                'patterns': ['boto3', 'aws-sdk', 'aws-cli'],
                'endpoints': ['/s3', '/dynamodb', '/lambda', '/ec2']
            },
            'google': {
                'base_url': 'https://developers.google.com',
                'patterns': ['google-api', 'google-cloud', 'gcp'],
                'endpoints': ['/maps', '/analytics', '/drive', '/sheets']
            },
            'microsoft': {
                'base_url': 'https://docs.microsoft.com/en-us/graph',
                'patterns': ['microsoft-graph', 'azure', 'office365'],
                'endpoints': ['/users', '/mail', '/calendar', '/teams']
            },
            'slack': {
                'base_url': 'https://api.slack.com',
                'patterns': ['slack-sdk', 'slack-api', 'slack-bolt'],
                'endpoints': ['/chat', '/conversations', '/users', '/files']
            },
            'github': {
                'base_url': 'https://docs.github.com/en/rest',
                'patterns': ['github-api', 'octokit', 'github-sdk'],
                'endpoints': ['/repos', '/issues', '/pull-requests', '/actions']
            },
            'paypal': {
                'base_url': 'https://developer.paypal.com/docs/api',
                'patterns': ['paypal-sdk', 'paypal-api', 'paypal-rest'],
                'endpoints': ['/payments', '/orders', '/payouts', '/webhooks']
            },
            'shopify': {
                'base_url': 'https://shopify.dev/api',
                'patterns': ['shopify-api', 'shopify-sdk', 'shopify-node'],
                'endpoints': ['/products', '/orders', '/customers', '/inventory']
            }
        }
    
    def train_on_api_documentation(self, services: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Train the model on API documentation for specified services
        
        Args:
            services: List of service names to train on. If None, trains on all services
            
        Returns:
            Training results
        """
        if services is None:
            services = list(self.api_services.keys())
        
        training_results = {
            'services_trained': [],
            'total_docs_processed': 0,
            'training_timestamp': datetime.now(timezone.utc).isoformat(),
            'errors': []
        }
        
        for service in services:
            if service not in self.api_services:
                training_results['errors'].append(f"Unknown service: {service}")
                continue
            
            try:
                logger.info(f"Training on {service} API documentation")
                service_result = self._train_on_service(service)
                training_results['services_trained'].append(service_result)
                training_results['total_docs_processed'] += service_result['docs_processed']
                
            except Exception as e:
                error_msg = f"Error training on {service}: {str(e)}"
                logger.error(error_msg)
                training_results['errors'].append(error_msg)
        
        # Store training results
        self._store_training_results(training_results)
        
        return training_results
    
    def _train_on_service(self, service: str) -> Dict[str, Any]:
        """
        Train on a specific service's API documentation
        
        Args:
            service: Service name
            
        Returns:
            Service training results
        """
        service_config = self.api_services[service]
        base_url = service_config['base_url']
        
        # Scrape API documentation
        docs_data = self._scrape_api_documentation(base_url, service)
        
        # Process and structure the documentation
        structured_docs = self._structure_documentation(docs_data, service)
        
        # Generate training data using AI
        training_data = self._generate_training_data(structured_docs, service)
        
        # Store in knowledge base
        self._store_api_knowledge(service, training_data)
        
        return {
            'service': service,
            'docs_processed': len(docs_data),
            'training_data_generated': len(training_data),
            'base_url': base_url
        }
    
    def _scrape_api_documentation(self, base_url: str, service: str) -> List[Dict[str, Any]]:
        """
        Scrape API documentation from a service's website
        
        Args:
            base_url: Base URL of the API documentation
            service: Service name
            
        Returns:
            List of scraped documentation data
        """
        docs_data = []
        
        try:
            # Get main documentation page
            response = requests.get(base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract API endpoints and documentation
            if service == 'stripe':
                docs_data.extend(self._scrape_stripe_docs(soup, base_url))
            elif service == 'twilio':
                docs_data.extend(self._scrape_twilio_docs(soup, base_url))
            elif service == 'aws':
                docs_data.extend(self._scrape_aws_docs(soup, base_url))
            else:
                docs_data.extend(self._scrape_generic_docs(soup, base_url, service))
            
        except Exception as e:
            logger.error(f"Error scraping {service} documentation: {str(e)}")
        
        return docs_data
    
    def _scrape_stripe_docs(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Scrape Stripe-specific documentation"""
        docs = []
        
        # Find API endpoint sections
        endpoint_sections = soup.find_all(['div', 'section'], class_=re.compile(r'endpoint|api|method'))
        
        for section in endpoint_sections:
            doc_data = {
                'type': 'api_endpoint',
                'service': 'stripe',
                'content': section.get_text(strip=True),
                'url': base_url,
                'scraped_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Extract HTTP method and endpoint
            method_elem = section.find(['code', 'span'], class_=re.compile(r'method|verb'))
            if method_elem:
                doc_data['http_method'] = method_elem.get_text(strip=True)
            
            endpoint_elem = section.find(['code', 'span'], class_=re.compile(r'endpoint|path'))
            if endpoint_elem:
                doc_data['endpoint'] = endpoint_elem.get_text(strip=True)
            
            docs.append(doc_data)
        
        return docs
    
    def _scrape_twilio_docs(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Scrape Twilio-specific documentation"""
        docs = []
        
        # Find code examples and API references
        code_blocks = soup.find_all(['pre', 'code'], class_=re.compile(r'code|example|api'))
        
        for block in code_blocks:
            doc_data = {
                'type': 'code_example',
                'service': 'twilio',
                'content': block.get_text(strip=True),
                'url': base_url,
                'scraped_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Extract language if available
            lang_elem = block.find_parent(['div', 'section'])
            if lang_elem:
                lang_text = lang_elem.get_text().lower()
                if 'python' in lang_text:
                    doc_data['language'] = 'python'
                elif 'javascript' in lang_text or 'node' in lang_text:
                    doc_data['language'] = 'javascript'
            
            docs.append(doc_data)
        
        return docs
    
    def _scrape_aws_docs(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Scrape AWS-specific documentation"""
        docs = []
        
        # Find service documentation sections
        service_sections = soup.find_all(['div', 'section'], class_=re.compile(r'service|api|reference'))
        
        for section in service_sections:
            doc_data = {
                'type': 'service_documentation',
                'service': 'aws',
                'content': section.get_text(strip=True),
                'url': base_url,
                'scraped_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Extract service name
            title_elem = section.find(['h1', 'h2', 'h3'])
            if title_elem:
                doc_data['service_name'] = title_elem.get_text(strip=True)
            
            docs.append(doc_data)
        
        return docs
    
    def _scrape_generic_docs(self, soup: BeautifulSoup, base_url: str, service: str) -> List[Dict[str, Any]]:
        """Generic documentation scraper for other services"""
        docs = []
        
        # Find common documentation patterns
        doc_sections = soup.find_all(['div', 'section', 'article'], class_=re.compile(r'doc|api|reference|guide'))
        
        for section in doc_sections:
            content = section.get_text(strip=True)
            if len(content) > 100:  # Only include substantial content
                doc_data = {
                    'type': 'documentation',
                    'service': service,
                    'content': content,
                    'url': base_url,
                    'scraped_at': datetime.now(timezone.utc).isoformat()
                }
                docs.append(doc_data)
        
        return docs
    
    def _structure_documentation(self, docs_data: List[Dict[str, Any]], service: str) -> Dict[str, Any]:
        """
        Structure the scraped documentation using AI
        
        Args:
            docs_data: Raw scraped documentation
            service: Service name
            
        Returns:
            Structured documentation
        """
        # Combine all documentation content
        combined_content = '\n\n'.join([doc['content'] for doc in docs_data])
        
        # Use AI to structure the documentation
        prompt = f"""
        Analyze and structure the following API documentation for {service}:
        
        {combined_content[:10000]}  # Limit content size
        
        Please extract and structure the following information:
        
        1. **API Endpoints**: List all available endpoints with HTTP methods
        2. **Authentication Methods**: How to authenticate with the API
        3. **Request/Response Formats**: Data formats and schemas
        4. **SDK/Library Usage**: How to use the official SDKs
        5. **Code Examples**: Common usage patterns
        6. **Error Handling**: Error codes and handling
        7. **Rate Limits**: API rate limiting information
        8. **Webhooks**: Webhook configuration and events
        
        Format your response as JSON with the following structure:
        {{
            "service": "{service}",
            "endpoints": [
                {{
                    "method": "POST",
                    "path": "/api/v1/charges",
                    "description": "Create a charge",
                    "parameters": ["amount", "currency", "source"],
                    "response_format": "JSON"
                }}
            ],
            "authentication": {{
                "type": "API Key",
                "header": "Authorization",
                "format": "Bearer sk_test_..."
            }},
            "sdk_usage": [
                {{
                    "language": "python",
                    "import": "import stripe",
                    "initialization": "stripe.api_key = 'sk_test_...'",
                    "common_patterns": ["stripe.Charge.create()", "stripe.Customer.create()"]
                }}
            ],
            "code_examples": [
                {{
                    "language": "python",
                    "description": "Create a charge",
                    "code": "charge = stripe.Charge.create(amount=2000, currency='usd', source='tok_visa')"
                }}
            ],
            "error_handling": [
                {{
                    "error_code": "card_declined",
                    "description": "The card was declined",
                    "handling": "Show error message to user"
                }}
            ],
            "rate_limits": {{
                "requests_per_second": 100,
                "burst_limit": 1000
            }},
            "webhooks": [
                {{
                    "event": "charge.succeeded",
                    "description": "A charge was successfully created",
                    "payload": "{{'id': 'ch_123', 'amount': 2000}}"
                }}
            ]
        }}
        """
        
        try:
            response = self._call_bedrock(prompt)
            structured_docs = json.loads(response)
            return structured_docs
            
        except Exception as e:
            logger.error(f"Error structuring {service} documentation: {str(e)}")
            return {
                'service': service,
                'error': str(e),
                'raw_content': combined_content[:1000]
            }
    
    def _generate_training_data(self, structured_docs: Dict[str, Any], service: str) -> List[Dict[str, Any]]:
        """
        Generate training data for integration detection
        
        Args:
            structured_docs: Structured documentation
            service: Service name
            
        Returns:
            List of training data items
        """
        training_data = []
        
        # Generate patterns for SDK detection
        if 'sdk_usage' in structured_docs:
            for sdk in structured_docs['sdk_usage']:
                training_item = {
                    'type': 'sdk_pattern',
                    'service': service,
                    'language': sdk.get('language', 'unknown'),
                    'import_patterns': [sdk.get('import', '')],
                    'initialization_patterns': [sdk.get('initialization', '')],
                    'usage_patterns': sdk.get('common_patterns', []),
                    'confidence': 0.9
                }
                training_data.append(training_item)
        
        # Generate patterns for API endpoint detection
        if 'endpoints' in structured_docs:
            for endpoint in structured_docs['endpoints']:
                training_item = {
                    'type': 'endpoint_pattern',
                    'service': service,
                    'http_method': endpoint.get('method', 'unknown'),
                    'path_pattern': endpoint.get('path', ''),
                    'description': endpoint.get('description', ''),
                    'parameters': endpoint.get('parameters', []),
                    'confidence': 0.8
                }
                training_data.append(training_item)
        
        # Generate patterns for authentication detection
        if 'authentication' in structured_docs:
            auth = structured_docs['authentication']
            training_item = {
                'type': 'auth_pattern',
                'service': service,
                'auth_type': auth.get('type', 'unknown'),
                'header_pattern': auth.get('header', ''),
                'format_pattern': auth.get('format', ''),
                'confidence': 0.9
            }
            training_data.append(training_item)
        
        # Generate patterns for error handling detection
        if 'error_handling' in structured_docs:
            for error in structured_docs['error_handling']:
                training_item = {
                    'type': 'error_pattern',
                    'service': service,
                    'error_code': error.get('error_code', ''),
                    'error_description': error.get('description', ''),
                    'handling_pattern': error.get('handling', ''),
                    'confidence': 0.7
                }
                training_data.append(training_item)
        
        return training_data
    
    def _store_api_knowledge(self, service: str, training_data: List[Dict[str, Any]]):
        """
        Store API knowledge in the knowledge base
        
        Args:
            service: Service name
            training_data: Training data to store
        """
        try:
            table = self.dynamodb.Table(self.api_docs_table)
            
            for item in training_data:
                # Create unique ID for the training item
                item_id = hashlib.md5(
                    f"{service}_{item['type']}_{json.dumps(item, sort_keys=True)}".encode()
                ).hexdigest()
                
                # Store in DynamoDB
                table.put_item(Item={
                    'id': item_id,
                    'service': service,
                    'type': item['type'],
                    'data': item,
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'ttl': int((datetime.now(timezone.utc).timestamp() + (365 * 24 * 60 * 60)))  # 1 year TTL
                })
            
            # Also store in S3 for backup and bulk access
            s3_key = f"api-knowledge/{service}/{datetime.now().strftime('%Y%m%d')}/training_data.json"
            self.s3_client.put_object(
                Bucket=self.knowledge_base_bucket,
                Key=s3_key,
                Body=json.dumps(training_data, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"Stored {len(training_data)} training items for {service}")
            
        except Exception as e:
            logger.error(f"Error storing API knowledge for {service}: {str(e)}")
            raise
    
    def _store_training_results(self, training_results: Dict[str, Any]):
        """Store training results"""
        try:
            table = self.dynamodb.Table(self.api_docs_table)
            
            table.put_item(Item={
                'id': f"training_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'type': 'training_results',
                'data': training_results,
                'created_at': datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error storing training results: {str(e)}")
    
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
    
    def get_api_knowledge(self, service: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve API knowledge from the knowledge base
        
        Args:
            service: Optional service name to filter by
            
        Returns:
            List of API knowledge items
        """
        try:
            table = self.dynamodb.Table(self.api_docs_table)
            
            if service:
                response = table.query(
                    IndexName='service-index',  # Assuming GSI on service
                    KeyConditionExpression='service = :service',
                    ExpressionAttributeValues={':service': service}
                )
            else:
                response = table.scan()
            
            return [item['data'] for item in response.get('Items', [])]
            
        except Exception as e:
            logger.error(f"Error retrieving API knowledge: {str(e)}")
            return []
    
    def update_integration_detection_patterns(self) -> Dict[str, Any]:
        """
        Update the integration detection patterns based on trained knowledge
        
        Returns:
            Updated patterns
        """
        try:
            # Get all API knowledge
            api_knowledge = self.get_api_knowledge()
            
            # Generate enhanced patterns
            enhanced_patterns = self._generate_enhanced_patterns(api_knowledge)
            
            # Store updated patterns
            self._store_enhanced_patterns(enhanced_patterns)
            
            return {
                'status': 'success',
                'patterns_updated': len(enhanced_patterns),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating integration patterns: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def _generate_enhanced_patterns(self, api_knowledge: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate enhanced integration detection patterns"""
        patterns = {
            'import_patterns': [],
            'initialization_patterns': [],
            'usage_patterns': [],
            'endpoint_patterns': [],
            'auth_patterns': [],
            'error_patterns': []
        }
        
        for knowledge in api_knowledge:
            if knowledge['type'] == 'sdk_pattern':
                patterns['import_patterns'].extend(knowledge.get('import_patterns', []))
                patterns['initialization_patterns'].extend(knowledge.get('initialization_patterns', []))
                patterns['usage_patterns'].extend(knowledge.get('usage_patterns', []))
            
            elif knowledge['type'] == 'endpoint_pattern':
                patterns['endpoint_patterns'].append(knowledge.get('path_pattern', ''))
            
            elif knowledge['type'] == 'auth_pattern':
                patterns['auth_patterns'].append(knowledge.get('format_pattern', ''))
            
            elif knowledge['type'] == 'error_pattern':
                patterns['error_patterns'].append(knowledge.get('error_code', ''))
        
        return patterns
    
    def _store_enhanced_patterns(self, patterns: Dict[str, List[str]]):
        """Store enhanced patterns for use in integration detection"""
        try:
            s3_key = "integration-patterns/enhanced_patterns.json"
            self.s3_client.put_object(
                Bucket=self.knowledge_base_bucket,
                Key=s3_key,
                Body=json.dumps(patterns, indent=2),
                ContentType='application/json'
            )
            
            logger.info("Stored enhanced integration patterns")
            
        except Exception as e:
            logger.error(f"Error storing enhanced patterns: {str(e)}")
            raise
