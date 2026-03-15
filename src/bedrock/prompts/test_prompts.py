"""
Test Case Generation Prompts for AWS Bedrock
Contains specialized prompts for generating unit, functional, and edge case tests
"""

def get_unit_test_prompt(function_info: dict) -> str:
    """
    Generate unit test prompt for a specific function
    """
    prompt = f"""
You are an expert software tester tasked with creating comprehensive unit tests for the following function:

FUNCTION DETAILS:
- Name: {function_info.get('name', 'unknown')}
- File: {function_info.get('file', 'unknown')}
- Arguments: {', '.join(function_info.get('args', []))}
- Docstring: {function_info.get('docstring', 'No documentation available')}
- Decorators: {', '.join(function_info.get('decorators', []))}

Please generate comprehensive unit tests that include:

1. HAPPY PATH TESTS (2-3 tests)
   - Test normal operation with valid inputs
   - Test expected return values
   - Test typical use cases

2. EDGE CASE TESTS (2-3 tests)
   - Test boundary conditions
   - Test with minimal/maximal inputs
   - Test with edge values

3. ERROR HANDLING TESTS (2-3 tests)
   - Test with invalid inputs
   - Test exception handling
   - Test error conditions

For each test, provide:
- Test name (descriptive)
- Test description
- Input data
- Expected output/behavior
- Test type (happy_path, edge_case, error_handling)

Format the tests as executable code with proper assertions. Use appropriate testing framework conventions (pytest for Python, Jest for JavaScript, etc.).

Example format:
```python
def test_function_name_happy_path():
    \"\"\"Test normal operation with valid inputs\"\"\"
    # Arrange
    input_data = "..."
    
    # Act
    result = function_name(input_data)
    
    # Assert
    assert result == expected_output
```

Generate tests that are:
- Comprehensive and thorough
- Easy to understand and maintain
- Focused on the function's behavior
- Include proper error handling
"""
    return prompt

def get_functional_test_prompt(endpoint_info: dict) -> str:
    """
    Generate functional test prompt for a specific API endpoint
    """
    prompt = f"""
You are an expert software tester tasked with creating comprehensive functional tests for the following API endpoint:

ENDPOINT DETAILS:
- Method: {endpoint_info.get('method', 'unknown')}
- Path: {endpoint_info.get('endpoint', 'unknown')}
- File: {endpoint_info.get('file', 'unknown')}
- Line: {endpoint_info.get('line', 'unknown')}

Please generate comprehensive functional tests that include:

1. VALID REQUEST TESTS (2-3 tests)
   - Test with valid request data
   - Test expected response format
   - Test successful operation

2. INVALID INPUT TESTS (2-3 tests)
   - Test with missing required fields
   - Test with invalid data types
   - Test with malformed requests

3. AUTHENTICATION/AUTHORIZATION TESTS (2-3 tests)
   - Test with valid authentication
   - Test with invalid authentication
   - Test with insufficient permissions

4. PERFORMANCE TESTS (1-2 tests)
   - Test response time requirements
   - Test concurrent requests

For each test, provide:
- Test name (descriptive)
- Test description
- Request data (headers, body, query parameters)
- Expected response (status code, headers, body)
- Test type (valid, invalid, auth, performance)

Format the tests as executable code using appropriate testing frameworks (requests for Python, supertest for Node.js, etc.).

Example format:
```python
def test_endpoint_valid_request():
    \"\"\"Test endpoint with valid request data\"\"\"
    # Arrange
    url = "http://localhost:8000/api/endpoint"
    headers = {{"Content-Type": "application/json"}}
    data = {{"key": "value"}}
    
    # Act
    response = requests.post(url, json=data, headers=headers)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

Generate tests that are:
- Comprehensive and realistic
- Cover all major scenarios
- Include proper error handling
- Test both success and failure cases
"""
    return prompt

def get_edge_case_test_prompt(analysis_results: dict) -> str:
    """
    Generate edge case test prompt based on overall system analysis
    """
    prompt = f"""
You are an expert software tester tasked with creating comprehensive edge case tests for the entire system based on code analysis.

SYSTEM ANALYSIS:
- Programming Languages: {', '.join(analysis_results.get('languages_analyzed', []))}
- Total Functions: {len(analysis_results.get('functions_found', []))}
- API Endpoints: {len(analysis_results.get('api_endpoints', []))}
- External Integrations: {len(analysis_results.get('external_integrations', []))}
- Database Operations: {len(analysis_results.get('database_operations', []))}

KEY FUNCTIONS:
{format_functions_for_test(analysis_results.get('functions_found', []))}

API ENDPOINTS:
{format_endpoints_for_test(analysis_results.get('api_endpoints', []))}

EXTERNAL INTEGRATIONS:
{format_integrations_for_test(analysis_results.get('external_integrations', []))}

Please generate comprehensive edge case tests covering:

1. BOUNDARY VALUE TESTING
   - Test with minimum and maximum values
   - Test with null/empty values
   - Test with boundary conditions

2. ERROR CONDITION TESTING
   - Test with invalid data formats
   - Test with corrupted data
   - Test with unexpected data types

3. NETWORK FAILURE SCENARIOS
   - Test with network timeouts
   - Test with connection failures
   - Test with partial data transmission

4. DATA CORRUPTION SCENARIOS
   - Test with malformed data
   - Test with incomplete data
   - Test with conflicting data

5. CONCURRENCY ISSUES
   - Test with simultaneous requests
   - Test with race conditions
   - Test with resource conflicts

6. RESOURCE EXHAUSTION SCENARIOS
   - Test with memory limits
   - Test with disk space limits
   - Test with CPU limits

For each test category, provide 2-3 specific test cases with:
- Test name (descriptive)
- Test description
- Scenario description
- Expected behavior
- Test type (boundary, error, network, data, concurrency, resource)

Format the tests as executable code with proper setup and teardown.

Example format:
```python
def test_boundary_value_maximum_input():
    \"\"\"Test system behavior with maximum input values\"\"\"
    # Arrange
    max_input = "A" * 10000  # Maximum string length
    
    # Act
    result = process_input(max_input)
    
    # Assert
    assert result is not None
    assert len(result) <= expected_max_length
```

Generate tests that are:
- Realistic and practical
- Cover critical edge cases
- Include proper error handling
- Test system resilience
"""
    return prompt

def get_integration_test_prompt(analysis_results: dict) -> str:
    """
    Generate integration test prompt for external systems
    """
    prompt = f"""
You are an expert software tester tasked with creating integration tests for external system interactions.

EXTERNAL INTEGRATIONS IDENTIFIED:
{format_integrations_for_test(analysis_results.get('external_integrations', []))}

API ENDPOINTS:
{format_endpoints_for_test(analysis_results.get('api_endpoints', []))}

Please generate comprehensive integration tests covering:

1. EXTERNAL SERVICE INTEGRATION TESTS
   - Test successful integration calls
   - Test service unavailability
   - Test service response delays
   - Test service error responses

2. DATA INTEGRATION TESTS
   - Test data format compatibility
   - Test data transformation
   - Test data validation
   - Test data synchronization

3. AUTHENTICATION INTEGRATION TESTS
   - Test valid authentication tokens
   - Test expired authentication tokens
   - Test invalid authentication tokens
   - Test authentication refresh

4. ERROR HANDLING INTEGRATION TESTS
   - Test network failures
   - Test service timeouts
   - Test malformed responses
   - Test rate limiting

For each integration, provide 3-4 test cases with:
- Test name (descriptive)
- Test description
- Integration scenario
- Expected behavior
- Error handling

Format the tests as executable code with proper mocking and stubbing.

Example format:
```python
def test_external_service_successful_call():
    \"\"\"Test successful integration with external service\"\"\"
    # Arrange
    mock_response = {{"status": "success", "data": "test_data"}}
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.status_code = 200
        
        # Act
        result = call_external_service("test_data")
        
        # Assert
        assert result["status"] == "success"
        mock_post.assert_called_once()
```

Generate tests that are:
- Comprehensive and realistic
- Include proper mocking
- Test both success and failure scenarios
- Cover all integration points
"""
    return prompt

def get_performance_test_prompt(analysis_results: dict) -> str:
    """
    Generate performance test prompt
    """
    prompt = f"""
You are an expert performance tester tasked with creating performance tests for the system.

SYSTEM ANALYSIS:
- API Endpoints: {len(analysis_results.get('api_endpoints', []))}
- Functions: {len(analysis_results.get('functions_found', []))}
- External Integrations: {len(analysis_results.get('external_integrations', []))}

API ENDPOINTS:
{format_endpoints_for_test(analysis_results.get('api_endpoints', []))}

Please generate comprehensive performance tests covering:

1. LOAD TESTING
   - Test with normal expected load
   - Test with peak load conditions
   - Test with gradual load increase

2. STRESS TESTING
   - Test beyond normal capacity
   - Test system breaking point
   - Test recovery after stress

3. VOLUME TESTING
   - Test with large data sets
   - Test with maximum data volumes
   - Test data processing performance

4. RESPONSE TIME TESTING
   - Test individual endpoint response times
   - Test end-to-end response times
   - Test database query performance

For each test category, provide 2-3 test cases with:
- Test name (descriptive)
- Test description
- Performance criteria
- Expected metrics
- Test configuration

Format the tests as executable code using performance testing frameworks.

Example format:
```python
def test_api_endpoint_response_time():
    \"\"\"Test API endpoint response time under normal load\"\"\"
    # Arrange
    url = "http://localhost:8000/api/endpoint"
    concurrent_users = 10
    duration = 60  # seconds
    
    # Act
    results = run_load_test(url, concurrent_users, duration)
    
    # Assert
    assert results.avg_response_time < 200  # milliseconds
    assert results.percentile_95 < 500  # milliseconds
    assert results.error_rate < 0.01  # 1%
```

Generate tests that are:
- Realistic and measurable
- Include proper performance metrics
- Test critical performance scenarios
- Cover all major system components
"""
    return prompt

# Helper functions for formatting data for prompts
def format_functions_for_test(functions: list) -> str:
    """Format functions for test prompts"""
    if not functions:
        return "No functions identified"
    
    formatted = []
    for func in functions[:10]:  # Limit to first 10
        name = func.get('name', 'unknown')
        file = func.get('file', 'unknown')
        args = func.get('args', [])
        
        formatted.append(f"- {name}({', '.join(args)}) in {file}")
    
    return '\n'.join(formatted)

def format_endpoints_for_test(endpoints: list) -> str:
    """Format endpoints for test prompts"""
    if not endpoints:
        return "No API endpoints identified"
    
    formatted = []
    for endpoint in endpoints[:10]:  # Limit to first 10
        method = endpoint.get('method', 'unknown')
        path = endpoint.get('endpoint', 'unknown')
        
        formatted.append(f"- {method} {path}")
    
    return '\n'.join(formatted)

def format_integrations_for_test(integrations: list) -> str:
    """Format integrations for test prompts"""
    if not integrations:
        return "No external integrations identified"
    
    formatted = []
    for integration in integrations[:10]:  # Limit to first 10
        module = integration.get('module', 'unknown')
        file = integration.get('file', 'unknown')
        
        formatted.append(f"- {module} (used in {file})")
    
    return '\n'.join(formatted)
