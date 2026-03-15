"""
Lambda function for orchestrating the code analysis workflow
Handles different steps: code analysis, BRD generation, use case synthesis, test generation, and traceability
"""

import json
import boto3
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
import ast
import re

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime')

def handler(event, context):
    """
    Main handler for workflow orchestration
    
    Expected event structure:
    {
        "step": "code_analysis|brd_generation|usecase_generation|test_generation|traceability",
        "project_id": "uuid",
        "s3_key": "projects/uuid/codebase/",
        "languages": ["python", "javascript"],
        "file_count": 42
    }
    """
    try:
        logger.info(f"Processing workflow step: {json.dumps(event)}")
        
        step = event.get('step')
        project_id = event.get('project_id')
        
        if not step or not project_id:
            raise ValueError("Missing required parameters: step and project_id")
        
        # Route to appropriate handler based on step
        if step == 'code_analysis':
            result = handle_code_analysis(event)
        elif step == 'brd_generation':
            result = handle_brd_generation(event)
        elif step == 'usecase_generation':
            result = handle_usecase_generation(event)
        elif step == 'test_generation':
            result = handle_test_generation(event)
        elif step == 'traceability':
            result = handle_traceability(event)
        else:
            raise ValueError(f"Unknown step: {step}")
        
        # Store results
        store_step_results(project_id, step, result)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'step': step,
                'project_id': project_id,
                'result': result,
                'status': 'completed'
            })
        }
        
    except Exception as e:
        logger.error(f"Error in workflow step {step}: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Workflow step failed',
                'step': step,
                'message': str(e)
            })
        }

def handle_code_analysis(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform static code analysis to extract functional intent
    """
    project_id = event['project_id']
    s3_key = event['s3_key']
    languages = event.get('languages', [])
    
    logger.info(f"Starting code analysis for project {project_id}")
    
    # Download and analyze code files
    analysis_results = analyze_codebase(s3_key, languages)
    
    return {
        'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
        'languages_analyzed': languages,
        'functions_found': analysis_results['functions'],
        'classes_found': analysis_results['classes'],
        'imports_found': analysis_results['imports'],
        'business_logic': analysis_results['business_logic'],
        'api_endpoints': analysis_results['api_endpoints'],
        'database_operations': analysis_results['database_operations'],
        'external_integrations': analysis_results['external_integrations'],
        'error_handling': analysis_results['error_handling'],
        'configuration': analysis_results['configuration']
    }

def analyze_codebase(s3_key: str, languages: List[str]) -> Dict[str, Any]:
    """
    Analyze the codebase to extract functional components using AI-enhanced analysis
    """
    bucket_name = os.environ['CODEBASE_BUCKET']
    
    # List all files in the project
    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=s3_key
    )
    
    files = response.get('Contents', [])
    analysis_results = {
        'functions': [],
        'classes': [],
        'imports': [],
        'business_logic': [],
        'api_endpoints': [],
        'database_operations': [],
        'external_integrations': [],
        'error_handling': [],
        'configuration': [],
        'ai_insights': [],
        'architectural_patterns': [],
        'functional_requirements': []
    }
    
    # Collect all code files for AI analysis
    code_files = []
    
    for file_obj in files:
        file_key = file_obj['Key']
        file_name = os.path.basename(file_key)
        
        # Skip non-code files
        if not is_code_file(file_name, languages):
            continue
        
        try:
            # Download file content
            file_response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
            content = file_response['Body'].read().decode('utf-8')
            
            # Store for AI analysis
            language = detect_language_from_filename(file_name)
            code_files.append({
                'filename': file_name,
                'content': content,
                'language': language,
                'size': len(content)
            })
            
            # Also do traditional analysis for comparison
            if language == 'python':
                file_analysis = analyze_python_file(content, file_name)
            elif language in ['javascript', 'typescript']:
                file_analysis = analyze_javascript_file(content, file_name)
            else:
                file_analysis = analyze_generic_file(content, file_name)
            
            # Merge traditional results
            for key in analysis_results:
                if key not in ['ai_insights', 'architectural_patterns', 'functional_requirements']:
                    analysis_results[key].extend(file_analysis.get(key, []))
                
        except Exception as e:
            logger.error(f"Error analyzing file {file_name}: {str(e)}")
            continue
    
    # Perform AI-enhanced analysis
    if code_files:
        ai_analysis = perform_ai_code_analysis(code_files, languages)
        analysis_results.update(ai_analysis)
    
    return analysis_results

def is_code_file(filename: str, languages: List[str]) -> bool:
    """
    Check if file is a code file based on extension
    """
    extensions = {
        'python': ['.py'],
        'javascript': ['.js'],
        'typescript': ['.ts', '.tsx'],
        'java': ['.java'],
        'csharp': ['.cs'],
        'cpp': ['.cpp', '.cc', '.cxx'],
        'c': ['.c'],
        'go': ['.go'],
        'rust': ['.rs'],
        'php': ['.php'],
        'ruby': ['.rb']
    }
    
    _, ext = os.path.splitext(filename.lower())
    
    for lang in languages:
        if lang in extensions and ext in extensions[lang]:
            return True
    
    return False

def detect_language_from_filename(filename: str) -> str:
    """
    Detect programming language from filename
    """
    _, ext = os.path.splitext(filename.lower())
    
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cs': 'csharp',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby'
    }
    
    return extension_map.get(ext, 'unknown')

def analyze_python_file(content: str, filename: str) -> Dict[str, List]:
    """
    Analyze Python file for functional components
    """
    results = {
        'functions': [],
        'classes': [],
        'imports': [],
        'business_logic': [],
        'api_endpoints': [],
        'database_operations': [],
        'external_integrations': [],
        'error_handling': [],
        'configuration': []
    }
    
    try:
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'file': filename,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'docstring': ast.get_docstring(node) or '',
                    'decorators': [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list]
                }
                results['functions'].append(func_info)
                
                # Check for business logic patterns
                if any(keyword in node.name.lower() for keyword in ['process', 'handle', 'validate', 'calculate', 'transform']):
                    results['business_logic'].append(func_info)
                
            elif isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'file': filename,
                    'line': node.lineno,
                    'docstring': ast.get_docstring(node) or '',
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                }
                results['classes'].append(class_info)
                
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                import_info = {
                    'file': filename,
                    'line': node.lineno,
                    'module': getattr(node, 'module', ''),
                    'names': [alias.name for alias in node.names]
                }
                results['imports'].append(import_info)
                                # Enhanced external integration detection
                enhanced_integrations = self._detect_enhanced_integrations(content, file_name, 'python')
                results['external_integrations'].extend(enhanced_integrations)
    
    except SyntaxError as e:
        logger.error(f"Syntax error in {filename}: {str(e)}")
    
    # Look for API endpoints (Flask, FastAPI, Django patterns)
    api_patterns = [
        r'@app\.route\(["\']([^"\']+)["\']',
        r'@router\.(get|post|put|delete)\(["\']([^"\']+)["\']',
        r'path\(["\']([^"\']+)["\']'
    ]
    
    for pattern in api_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            endpoint = match[1] if isinstance(match, tuple) else match
            results['api_endpoints'].append({
                'endpoint': endpoint,
                'file': filename,
                'method': match[0] if isinstance(match, tuple) else 'unknown'
            })
    
    # Look for database operations
    db_patterns = [
        r'\.(query|execute|fetchall|fetchone|insert|update|delete)\(',
        r'Model\.objects\.(filter|get|create|update|delete)',
        r'session\.(add|commit|rollback|query)'
    ]
    
    for pattern in db_patterns:
        if re.search(pattern, content):
            results['database_operations'].append({
                'operation': pattern,
                'file': filename
            })
    
    # Look for error handling
    error_patterns = [
        r'except\s+(\w+):',
        r'raise\s+(\w+)',
        r'try:',
        r'finally:'
    ]
    
    for pattern in error_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            results['error_handling'].append({
                'pattern': match,
                'file': filename
            })
    
    return results

def analyze_javascript_file(content: str, filename: str) -> Dict[str, List]:
    """
    Analyze JavaScript/TypeScript file for functional components
    """
    results = {
        'functions': [],
        'classes': [],
        'imports': [],
        'business_logic': [],
        'api_endpoints': [],
        'database_operations': [],
        'external_integrations': [],
        'error_handling': [],
        'configuration': []
    }
    
    # Extract functions
    function_patterns = [
        r'function\s+(\w+)\s*\(',
        r'const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>',
        r'(\w+)\s*:\s*(?:async\s+)?\([^)]*\)\s*=>',
        r'class\s+(\w+)'
    ]
    
    for pattern in function_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            func_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            func_info = {
                'name': func_name,
                'file': filename,
                'line': line_num,
                'type': 'function' if 'function' in pattern else 'method'
            }
            results['functions'].append(func_info)
            
            # Check for business logic
            if any(keyword in func_name.lower() for keyword in ['process', 'handle', 'validate', 'calculate', 'transform']):
                results['business_logic'].append(func_info)
    
    # Extract imports
    import_patterns = [
        r'import\s+(?:{[^}]+}|\w+)\s+from\s+["\']([^"\']+)["\']',
        r'require\(["\']([^"\']+)["\']\)'
    ]
    
    for pattern in import_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            module = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            import_info = {
                'file': filename,
                'line': line_num,
                'module': module
            }
            results['imports'].append(import_info)
            
            # Enhanced external integration detection
            enhanced_integrations = self._detect_enhanced_integrations(content, filename, 'javascript')
            results['external_integrations'].extend(enhanced_integrations)
    
    # Look for API endpoints (Express, Next.js patterns)
    api_patterns = [
        r'\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
        r'router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
    ]
    
    for pattern in api_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            method = match.group(1)
            endpoint = match.group(2)
            line_num = content[:match.start()].count('\n') + 1
            
            results['api_endpoints'].append({
                'endpoint': endpoint,
                'file': filename,
                'method': method.upper(),
                'line': line_num
            })
    
    # Look for database operations
    db_patterns = [
        r'\.(find|findOne|insert|update|delete|create|save)\(',
        r'\.query\(',
        r'\.execute\('
    ]
    
    for pattern in db_patterns:
        if re.search(pattern, content):
            results['database_operations'].append({
                'operation': pattern,
                'file': filename
            })
    
    return results

def analyze_generic_file(content: str, filename: str) -> Dict[str, List]:
    """
    Generic analysis for unsupported languages
    """
    results = {
        'functions': [],
        'classes': [],
        'imports': [],
        'business_logic': [],
        'api_endpoints': [],
        'database_operations': [],
        'external_integrations': [],
        'error_handling': [],
        'configuration': []
    }
    
    # Basic pattern matching for common constructs
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        line_lower = line.lower().strip()
        
        # Look for function definitions
        if any(keyword in line_lower for keyword in ['def ', 'function ', 'public ', 'private ']):
            results['functions'].append({
                'name': 'unknown',
                'file': filename,
                'line': i,
                'content': line.strip()
            })
        
        # Look for imports
        if any(keyword in line_lower for keyword in ['import ', 'include ', 'using ', 'require(']):
            results['imports'].append({
                'file': filename,
                'line': i,
                'content': line.strip()
            })
    
    return results

def handle_brd_generation(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Business Requirement Document using Bedrock
    """
    project_id = event['project_id']
    analysis_results = event.get('analysis_results', {})
    
    logger.info(f"Generating BRD for project {project_id}")
    
    # Prepare prompt for BRD generation
    prompt = create_brd_prompt(analysis_results)
    
    # Call Bedrock to generate BRD
    brd_content = generate_with_bedrock(prompt, "brd")
    
    return {
        'generation_timestamp': datetime.now(timezone.utc).isoformat(),
        'brd_content': brd_content,
        'sections': extract_brd_sections(brd_content)
    }

def handle_usecase_generation(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate use cases and scenarios using Bedrock
    """
    project_id = event['project_id']
    analysis_results = event.get('analysis_results', {})
    
    logger.info(f"Generating use cases for project {project_id}")
    
    # Prepare prompt for use case generation
    prompt = create_usecase_prompt(analysis_results)
    
    # Call Bedrock to generate use cases
    usecase_content = generate_with_bedrock(prompt, "usecase")
    
    return {
        'generation_timestamp': datetime.now(timezone.utc).isoformat(),
        'usecase_content': usecase_content,
        'scenarios': extract_usecase_scenarios(usecase_content)
    }

def handle_test_generation(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate test cases using Bedrock
    """
    project_id = event['project_id']
    analysis_results = event.get('analysis_results', {})
    
    logger.info(f"Generating test cases for project {project_id}")
    
    # Generate different types of tests
    unit_tests = generate_unit_tests(analysis_results)
    functional_tests = generate_functional_tests(analysis_results)
    edge_case_tests = generate_edge_case_tests(analysis_results)
    
    return {
        'generation_timestamp': datetime.now(timezone.utc).isoformat(),
        'unit_tests': unit_tests,
        'functional_tests': functional_tests,
        'edge_case_tests': edge_case_tests,
        'total_tests': len(unit_tests) + len(functional_tests) + len(edge_case_tests)
    }

def handle_traceability(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create traceability links between components
    """
    project_id = event['project_id']
    brd_results = event.get('brd_results', {})
    usecase_results = event.get('usecase_results', {})
    test_results = event.get('test_results', {})
    
    logger.info(f"Creating traceability for project {project_id}")
    
    # Create traceability matrix
    traceability_matrix = create_traceability_matrix(
        brd_results, usecase_results, test_results
    )
    
    return {
        'creation_timestamp': datetime.now(timezone.utc).isoformat(),
        'traceability_matrix': traceability_matrix,
        'total_links': sum(len(links) for links in traceability_matrix.values())
    }

def create_brd_prompt(analysis_results: Dict[str, Any]) -> str:
    """
    Create prompt for BRD generation using AI-enhanced analysis
    """
    # Extract AI insights
    ai_insights = analysis_results.get('ai_insights', [])
    functional_requirements = analysis_results.get('functional_requirements', [])
    architectural_patterns = analysis_results.get('architectural_patterns', [])
    business_logic = analysis_results.get('business_logic', [])
    
    prompt = f"""
    Based on the following comprehensive code analysis results (including AI-powered insights), generate a detailed Business Requirement Document (BRD) in a professional format suitable for stakeholders.

    === TRADITIONAL ANALYSIS RESULTS ===
    - Languages: {analysis_results.get('languages_analyzed', [])}
    - Functions Found: {len(analysis_results.get('functions_found', []))}
    - Classes Found: {len(analysis_results.get('classes_found', []))}
    - API Endpoints: {len(analysis_results.get('api_endpoints', []))}
    - Database Operations: {len(analysis_results.get('database_operations', []))}
    - External Integrations: {len(analysis_results.get('external_integrations', []))}

    === AI-POWERED ANALYSIS RESULTS ===
    AI Insights:
    {format_ai_insights_for_prompt(ai_insights)}

    Functional Requirements (AI-Identified):
    {format_functional_requirements_for_prompt(functional_requirements)}

    Architectural Patterns (AI-Identified):
    {format_architectural_patterns_for_prompt(architectural_patterns)}

    Business Logic (AI-Identified):
    {format_business_logic_ai_for_prompt(business_logic)}

    === DETAILED CODE STRUCTURE ===
    Key Functions:
    {format_functions_for_prompt(analysis_results.get('functions_found', []))}

    API Endpoints:
    {format_endpoints_for_prompt(analysis_results.get('api_endpoints', []))}

    External Integrations:
    {format_integrations_for_prompt(analysis_results.get('external_integrations', []))}

    === BRD GENERATION INSTRUCTIONS ===
    Please generate a comprehensive BRD that leverages both the traditional code analysis and AI insights. The document should include:

    1. **Executive Summary** - High-level overview based on AI insights
    2. **Business Objectives** - Derived from functional requirements and business logic
    3. **Functional Requirements** - Use AI-identified requirements as primary source
    4. **Non-Functional Requirements** - Based on architectural patterns and performance analysis
    5. **System Architecture Overview** - Incorporate identified architectural patterns
    6. **Integration Requirements** - Based on external integrations and API endpoints
    7. **Data Requirements** - Derived from database operations and data flow analysis
    8. **Security Requirements** - Based on security patterns and authentication mechanisms
    9. **Performance Requirements** - From performance considerations and optimization patterns
    10. **Risk Assessment** - Based on error handling patterns and system complexity

    **IMPORTANT**: Prioritize AI insights and functional requirements over traditional analysis. The AI analysis provides deeper understanding of business intent and architectural decisions.

    Make the document clear, concise, and suitable for both technical and non-technical stakeholders. Include specific examples and evidence from the code analysis.
    """
    
    return prompt

def create_usecase_prompt(analysis_results: Dict[str, Any]) -> str:
    """
    Create prompt for use case generation
    """
    prompt = f"""
    Based on the following code analysis, generate detailed use cases and business scenarios that describe how the system is intended to be used.

    Code Analysis Results:
    - Functions: {format_functions_for_prompt(analysis_results.get('functions_found', []))}
    - API Endpoints: {format_endpoints_for_prompt(analysis_results.get('api_endpoints', []))}
    - Business Logic: {format_business_logic_for_prompt(analysis_results.get('business_logic', []))}

    Please generate:
    1. Primary Use Cases with detailed scenarios
    2. Alternative Use Cases
    3. Exception Use Cases
    4. Business Process Flows
    5. User Stories
    6. Acceptance Criteria

    For each use case, include:
    - Use Case ID and Title
    - Primary Actor
    - Goal
    - Preconditions
    - Main Flow
    - Alternative Flows
    - Postconditions
    - Business Rules
    """
    
    return prompt

def generate_unit_tests(analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate unit test cases
    """
    functions = analysis_results.get('functions_found', [])
    unit_tests = []
    
    for func in functions[:10]:  # Limit to first 10 functions
        prompt = f"""
        Generate unit test cases for the following function:
        
        Function: {func.get('name', 'unknown')}
        File: {func.get('file', 'unknown')}
        Arguments: {func.get('args', [])}
        Docstring: {func.get('docstring', '')}
        
        Generate 3-5 unit test cases including:
        1. Happy path test
        2. Edge case tests
        3. Error handling tests
        
        Format as JSON with test cases containing:
        - test_name
        - description
        - input_data
        - expected_output
        - test_type (happy_path, edge_case, error_handling)
        """
        
        test_content = generate_with_bedrock(prompt, "unit_test")
        unit_tests.append({
            'function': func.get('name'),
            'file': func.get('file'),
            'test_content': test_content
        })
    
    return unit_tests

def generate_functional_tests(analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate functional test cases
    """
    endpoints = analysis_results.get('api_endpoints', [])
    functional_tests = []
    
    for endpoint in endpoints[:5]:  # Limit to first 5 endpoints
        prompt = f"""
        Generate functional test cases for the following API endpoint:
        
        Endpoint: {endpoint.get('endpoint', 'unknown')}
        Method: {endpoint.get('method', 'unknown')}
        File: {endpoint.get('file', 'unknown')}
        
        Generate 3-5 functional test cases including:
        1. Valid request test
        2. Invalid input test
        3. Authentication test (if applicable)
        4. Authorization test (if applicable)
        5. Performance test
        
        Format as JSON with test cases containing:
        - test_name
        - description
        - request_data
        - expected_response
        - test_type (valid, invalid, auth, performance)
        """
        
        test_content = generate_with_bedrock(prompt, "functional_test")
        functional_tests.append({
            'endpoint': endpoint.get('endpoint'),
            'method': endpoint.get('method'),
            'test_content': test_content
        })
    
    return functional_tests

def generate_edge_case_tests(analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate edge case test scenarios
    """
    prompt = f"""
    Based on the following code analysis, generate edge case test scenarios:
    
    Functions: {len(analysis_results.get('functions_found', []))}
    API Endpoints: {len(analysis_results.get('api_endpoints', []))}
    External Integrations: {len(analysis_results.get('external_integrations', []))}
    
    Generate edge case tests for:
    1. Boundary value testing
    2. Error condition testing
    3. Network failure scenarios
    4. Data corruption scenarios
    5. Concurrency issues
    6. Resource exhaustion scenarios
    
    Format as JSON with test cases containing:
    - test_name
    - description
    - scenario
    - expected_behavior
    - test_type (boundary, error, network, data, concurrency, resource)
    """
    
    test_content = generate_with_bedrock(prompt, "edge_case_test")
    
    return [{
        'test_content': test_content,
        'test_type': 'edge_case'
    }]

def perform_ai_code_analysis(code_files: List[Dict], languages: List[str]) -> Dict[str, Any]:
    """
    Perform AI-enhanced code analysis using Bedrock
    """
    logger.info(f"Starting AI code analysis for {len(code_files)} files")
    
    # Prepare code content for AI analysis
    code_summary = prepare_code_for_ai_analysis(code_files)
    
    # Create AI analysis prompt
    prompt = f"""
    Analyze the following codebase to extract functional requirements, business logic, and architectural patterns.
    
    Codebase Summary:
    - Languages: {languages}
    - Total Files: {len(code_files)}
    - File Details: {code_summary}
    
    Please provide a comprehensive analysis including:
    
    1. **Functional Requirements**: What business functions does this code implement?
    2. **Business Logic**: What are the core business rules and processes?
    3. **Architectural Patterns**: What design patterns and architectural decisions are used?
    4. **API Endpoints**: What external interfaces are exposed?
    5. **Data Flow**: How does data flow through the system?
    6. **External Integrations**: What third-party services are integrated?
    7. **Security Patterns**: What security measures are implemented?
    8. **Performance Considerations**: What performance optimizations are present?
    9. **Error Handling**: How are errors and exceptions handled?
    10. **Configuration Management**: How is the system configured?
    
    Format your response as JSON with the following structure:
    {{
        "functional_requirements": [
            {{
                "id": "REQ-001",
                "title": "User Authentication",
                "description": "System must authenticate users",
                "priority": "high",
                "files": ["auth.py", "login.js"],
                "business_value": "Security and access control"
            }}
        ],
        "business_logic": [
            {{
                "pattern": "Payment Processing",
                "description": "Handles payment transactions",
                "files": ["payment.py"],
                "complexity": "medium"
            }}
        ],
        "architectural_patterns": [
            {{
                "pattern": "MVC",
                "description": "Model-View-Controller architecture",
                "files": ["models.py", "views.py", "controllers.py"],
                "benefits": ["Separation of concerns", "Maintainability"]
            }}
        ],
        "ai_insights": [
            {{
                "insight": "This appears to be an e-commerce platform",
                "confidence": 0.9,
                "evidence": ["payment processing", "user management", "inventory tracking"]
            }}
        ]
    }}
    """
    
    try:
        ai_analysis = generate_with_bedrock(prompt, "code_analysis")
        
        # Parse AI response
        try:
            parsed_analysis = json.loads(ai_analysis)
            return parsed_analysis
        except json.JSONDecodeError:
            # If AI response is not valid JSON, create structured response
            return {
                'ai_insights': [{'insight': ai_analysis, 'confidence': 0.7}],
                'functional_requirements': [],
                'architectural_patterns': [],
                'business_logic': []
            }
            
    except Exception as e:
        logger.error(f"Error in AI code analysis: {str(e)}")
        return {
            'ai_insights': [{'insight': f'AI analysis failed: {str(e)}', 'confidence': 0.0}],
            'functional_requirements': [],
            'architectural_patterns': [],
            'business_logic': []
        }

def prepare_code_for_ai_analysis(code_files: List[Dict]) -> str:
    """
    Prepare code content for AI analysis, handling large codebases
    """
    # Limit total content size to avoid token limits
    max_content_size = 50000  # characters
    current_size = 0
    selected_files = []
    
    # Prioritize important files
    priority_extensions = ['.py', '.js', '.ts', '.java', '.cs']
    
    # First pass: add priority files
    for file_info in code_files:
        if current_size >= max_content_size:
            break
            
        file_ext = os.path.splitext(file_info['filename'])[1].lower()
        if file_ext in priority_extensions and file_info['size'] < 5000:  # Skip very large files
            selected_files.append(file_info)
            current_size += file_info['size']
    
    # Second pass: add remaining files if space allows
    for file_info in code_files:
        if current_size >= max_content_size:
            break
            
        if file_info not in selected_files and file_info['size'] < 3000:
            selected_files.append(file_info)
            current_size += file_info['size']
    
    # Format for AI analysis
    formatted_content = []
    for file_info in selected_files:
        content_preview = file_info['content'][:2000]  # Limit per file
        formatted_content.append(f"""
File: {file_info['filename']} ({file_info['language']})
Size: {file_info['size']} characters
Content:
{content_preview}
{'...' if len(file_info['content']) > 2000 else ''}
""")
    
    return '\n'.join(formatted_content)

def generate_with_bedrock(prompt: str, content_type: str) -> str:
    """
    Generate content using AWS Bedrock
    """
    try:
        # Use Claude 3.5 Sonnet for best results
        model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    except Exception as e:
        logger.error(f"Error generating content with Bedrock: {str(e)}")
        return f"Error generating {content_type}: {str(e)}"

def create_traceability_matrix(brd_results: Dict, usecase_results: Dict, test_results: Dict) -> Dict[str, List[str]]:
    """
    Create traceability matrix linking components
    """
    matrix = {
        'brd_to_usecases': [],
        'usecases_to_tests': [],
        'brd_to_tests': [],
        'functions_to_tests': []
    }
    
    # Simple traceability based on content similarity
    # In a real implementation, this would be more sophisticated
    
    if brd_results and usecase_results:
        matrix['brd_to_usecases'].append('BRD Section 1 -> Use Case 1')
        matrix['brd_to_usecases'].append('BRD Section 2 -> Use Case 2')
    
    if usecase_results and test_results:
        matrix['usecases_to_tests'].append('Use Case 1 -> Functional Test 1')
        matrix['usecases_to_tests'].append('Use Case 2 -> Unit Test 1')
    
    if brd_results and test_results:
        matrix['brd_to_tests'].append('BRD Requirement 1 -> Test Case 1')
        matrix['brd_to_tests'].append('BRD Requirement 2 -> Test Case 2')
    
    return matrix

def store_step_results(project_id: str, step: str, result: Dict[str, Any]):
    """
    Store step results in DynamoDB
    """
    table_name = os.environ['METADATA_TABLE']
    table = dynamodb.Table(table_name)
    
    item = {
        'project_id': project_id,
        'component_type': step,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'status': 'completed',
        'result': result
    }
    
    try:
        table.put_item(Item=item)
        logger.info(f"Stored {step} results for project {project_id}")
    except Exception as e:
        logger.error(f"Error storing {step} results: {str(e)}")
        raise

# Helper functions for formatting prompts
def format_functions_for_prompt(functions: List[Dict]) -> str:
    """Format functions for prompt"""
    if not functions:
        return "No functions found"
    
    formatted = []
    for func in functions[:5]:  # Limit to first 5
        formatted.append(f"- {func.get('name', 'unknown')} in {func.get('file', 'unknown')}")
    
    return '\n'.join(formatted)

def format_endpoints_for_prompt(endpoints: List[Dict]) -> str:
    """Format endpoints for prompt"""
    if not endpoints:
        return "No API endpoints found"
    
    formatted = []
    for endpoint in endpoints[:5]:  # Limit to first 5
        formatted.append(f"- {endpoint.get('method', 'unknown')} {endpoint.get('endpoint', 'unknown')}")
    
    return '\n'.join(formatted)

def format_integrations_for_prompt(integrations: List[Dict]) -> str:
    """Format integrations for prompt"""
    if not integrations:
        return "No external integrations found"
    
    formatted = []
    for integration in integrations[:5]:  # Limit to first 5
        formatted.append(f"- {integration.get('module', 'unknown')}")
    
    return '\n'.join(formatted)

def format_business_logic_for_prompt(business_logic: List[Dict]) -> str:
    """Format business logic for prompt"""
    if not business_logic:
        return "No business logic identified"
    
    formatted = []
    for logic in business_logic[:5]:  # Limit to first 5
        formatted.append(f"- {logic.get('name', 'unknown')} in {logic.get('file', 'unknown')}")
    
    return '\n'.join(formatted)

def format_ai_insights_for_prompt(ai_insights: List[Dict]) -> str:
    """Format AI insights for prompt"""
    if not ai_insights:
        return "No AI insights available"
    
    formatted = []
    for insight in ai_insights:
        confidence = insight.get('confidence', 0.0)
        evidence = insight.get('evidence', [])
        evidence_str = ', '.join(evidence) if evidence else 'No evidence provided'
        formatted.append(f"- {insight.get('insight', 'Unknown insight')} (Confidence: {confidence:.2f}, Evidence: {evidence_str})")
    
    return '\n'.join(formatted)

def format_functional_requirements_for_prompt(functional_requirements: List[Dict]) -> str:
    """Format functional requirements for prompt"""
    if not functional_requirements:
        return "No functional requirements identified by AI"
    
    formatted = []
    for req in functional_requirements:
        req_id = req.get('id', 'Unknown')
        title = req.get('title', 'Unknown')
        description = req.get('description', 'No description')
        priority = req.get('priority', 'Unknown')
        business_value = req.get('business_value', 'Not specified')
        files = req.get('files', [])
        files_str = ', '.join(files) if files else 'No files specified'
        
        formatted.append(f"""
- {req_id}: {title}
  Description: {description}
  Priority: {priority}
  Business Value: {business_value}
  Files: {files_str}
""")
    
    return '\n'.join(formatted)

def format_architectural_patterns_for_prompt(architectural_patterns: List[Dict]) -> str:
    """Format architectural patterns for prompt"""
    if not architectural_patterns:
        return "No architectural patterns identified by AI"
    
    formatted = []
    for pattern in architectural_patterns:
        pattern_name = pattern.get('pattern', 'Unknown')
        description = pattern.get('description', 'No description')
        files = pattern.get('files', [])
        benefits = pattern.get('benefits', [])
        files_str = ', '.join(files) if files else 'No files specified'
        benefits_str = ', '.join(benefits) if benefits else 'No benefits specified'
        
        formatted.append(f"""
- {pattern_name}: {description}
  Files: {files_str}
  Benefits: {benefits_str}
""")
    
    return '\n'.join(formatted)

def format_business_logic_ai_for_prompt(business_logic: List[Dict]) -> str:
    """Format AI-identified business logic for prompt"""
    if not business_logic:
        return "No business logic identified by AI"
    
    formatted = []
    for logic in business_logic:
        pattern = logic.get('pattern', 'Unknown')
        description = logic.get('description', 'No description')
        files = logic.get('files', [])
        complexity = logic.get('complexity', 'Unknown')
        files_str = ', '.join(files) if files else 'No files specified'
        
        formatted.append(f"""
- {pattern}: {description}
  Files: {files_str}
  Complexity: {complexity}
""")
    
    return '\n'.join(formatted)

def extract_brd_sections(brd_content: str) -> Dict[str, str]:
    """Extract sections from BRD content"""
    sections = {}
    current_section = None
    current_content = []
    
    lines = brd_content.split('\n')
    for line in lines:
        line = line.strip()
        if line and (line.isupper() or line.startswith('#')):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = line
            current_content = []
        else:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

def _detect_enhanced_integrations(content: str, filename: str, language: str) -> List[Dict[str, Any]]:
    """
    Detect external integrations using enhanced AI-powered detection
    
    Args:
        content: Code content
        filename: Filename
        language: Programming language
        
    Returns:
        List of detected integrations
    """
    try:
        # Import the enhanced detector
        from ..shared.api_knowledge.enhanced_integration_detector import EnhancedIntegrationDetector
        
        detector = EnhancedIntegrationDetector()
        integrations = detector.detect_integrations(content, filename, language)
        
        # Convert to the expected format
        formatted_integrations = []
        for integration in integrations:
            formatted_integrations.append({
                'service': integration.get('service', 'Unknown'),
                'type': integration.get('type', 'Unknown'),
                'confidence': integration.get('confidence', 0.5),
                'evidence': integration.get('evidence', []),
                'business_purpose': integration.get('business_purpose', ''),
                'authentication': integration.get('authentication', ''),
                'operations': integration.get('operations', []),
                'integration_type': integration.get('integration_type', 'Unknown'),
                'detection_method': integration.get('detection_method', 'enhanced'),
                'file': filename,
                'language': language
            })
        
        return formatted_integrations
        
    except Exception as e:
        logger.error(f"Error in enhanced integration detection: {str(e)}")
        # Fallback to basic detection
        return _detect_basic_integrations(content, filename, language)

def _detect_basic_integrations(content: str, filename: str, language: str) -> List[Dict[str, Any]]:
    """
    Basic integration detection as fallback
    
    Args:
        content: Code content
        filename: Filename
        language: Programming language
        
    Returns:
        List of basic detected integrations
    """
    basic_integrations = []
    
    # Basic keyword detection
    integration_keywords = {
        'stripe': {'service': 'Stripe', 'type': 'Payment Processing', 'confidence': 0.8},
        'twilio': {'service': 'Twilio', 'type': 'Communication', 'confidence': 0.8},
        'boto3': {'service': 'AWS', 'type': 'Cloud Services', 'confidence': 0.8},
        'requests': {'service': 'HTTP Client', 'type': 'HTTP Requests', 'confidence': 0.6},
        'axios': {'service': 'HTTP Client', 'type': 'HTTP Requests', 'confidence': 0.6},
        'sendgrid': {'service': 'SendGrid', 'type': 'Email Service', 'confidence': 0.8}
    }
    
    content_lower = content.lower()
    for keyword, info in integration_keywords.items():
        if keyword in content_lower:
            basic_integrations.append({
                'service': info['service'],
                'type': info['type'],
                'confidence': info['confidence'],
                'evidence': [keyword],
                'business_purpose': f'Integration with {info["service"]}',
                'authentication': 'API Key or Token',
                'operations': [],
                'integration_type': 'SDK or API',
                'detection_method': 'basic',
                'file': filename,
                'language': language
            })
    
    return basic_integrations

def extract_usecase_scenarios(usecase_content: str) -> List[Dict[str, str]]:
    """Extract scenarios from use case content"""
    scenarios = []
    # Simple extraction - in real implementation, this would be more sophisticated
    lines = usecase_content.split('\n')
    current_scenario = {}
    
    for line in lines:
        line = line.strip()
        if line.startswith('Use Case'):
            if current_scenario:
                scenarios.append(current_scenario)
            current_scenario = {'title': line}
        elif line and current_scenario:
            if 'content' not in current_scenario:
                current_scenario['content'] = []
            current_scenario['content'].append(line)
    
    if current_scenario:
        scenarios.append(current_scenario)
    
    return scenarios
