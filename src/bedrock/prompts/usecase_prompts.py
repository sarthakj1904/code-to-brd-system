"""
Use Case Generation Prompts for AWS Bedrock
Contains specialized prompts for generating use cases and business scenarios
"""

def get_usecase_generation_prompt(analysis_results: dict) -> str:
    """
    Generate a comprehensive prompt for use case creation
    """
    prompt = f"""
You are an expert business analyst tasked with creating detailed use cases and business scenarios based on code analysis results.

CODE ANALYSIS RESULTS:
- Programming Languages: {', '.join(analysis_results.get('languages_analyzed', []))}
- Total Functions: {len(analysis_results.get('functions_found', []))}
- Total Classes: {len(analysis_results.get('classes_found', []))}
- API Endpoints: {len(analysis_results.get('api_endpoints', []))}
- Business Logic Functions: {len(analysis_results.get('business_logic', []))}

KEY FUNCTIONS IDENTIFIED:
{format_functions_for_usecase(analysis_results.get('functions_found', []))}

API ENDPOINTS DISCOVERED:
{format_endpoints_for_usecase(analysis_results.get('api_endpoints', []))}

BUSINESS LOGIC COMPONENTS:
{format_business_logic_for_usecase(analysis_results.get('business_logic', []))}

Please create comprehensive use cases with the following structure:

# USE CASES AND BUSINESS SCENARIOS

## 1. PRIMARY USE CASES
Create 5-8 primary use cases that represent the main business processes supported by this system.

For each use case, include:
- Use Case ID (e.g., UC-001)
- Use Case Name
- Primary Actor
- Goal
- Preconditions
- Main Flow (step-by-step)
- Alternative Flows
- Exception Flows
- Postconditions
- Business Rules
- Priority (High/Medium/Low)

## 2. USER STORIES
Create user stories in the format: "As a [user type], I want [functionality] so that [benefit]"

## 3. BUSINESS PROCESS FLOWS
Describe the high-level business processes and how they flow through the system.

## 4. ACCEPTANCE CRITERIA
Define specific, measurable criteria for each use case.

## 5. EXCEPTION SCENARIOS
Describe what happens when things go wrong or unexpected conditions occur.

Make the use cases clear, detailed, and focused on business value. Ensure they align with the functionality discovered in the code analysis.
"""
    return prompt

def get_usecase_section_prompt(section: str, analysis_results: dict) -> str:
    """
    Generate a prompt for a specific use case section
    """
    section_prompts = {
        'primary_use_cases': get_primary_usecases_prompt(analysis_results),
        'user_stories': get_user_stories_prompt(analysis_results),
        'business_processes': get_business_processes_prompt(analysis_results),
        'acceptance_criteria': get_acceptance_criteria_prompt(analysis_results),
        'exception_scenarios': get_exception_scenarios_prompt(analysis_results)
    }
    
    return section_prompts.get(section, get_usecase_generation_prompt(analysis_results))

def get_primary_usecases_prompt(analysis_results: dict) -> str:
    """
    Generate primary use cases section
    """
    return f"""
Based on the code analysis, create 5-8 primary use cases that represent the main business processes.

Code Analysis Context:
- API Endpoints: {len(analysis_results.get('api_endpoints', []))}
- Business Logic Functions: {len(analysis_results.get('business_logic', []))}
- Functions: {len(analysis_results.get('functions_found', []))}

Key Functions:
{format_functions_for_usecase(analysis_results.get('functions_found', []))}

API Endpoints:
{format_endpoints_for_usecase(analysis_results.get('api_endpoints', []))}

For each use case, provide:
1. Use Case ID and Name
2. Primary Actor (who performs this use case)
3. Goal (what the actor wants to achieve)
4. Preconditions (what must be true before starting)
5. Main Flow (step-by-step process)
6. Alternative Flows (other ways to achieve the goal)
7. Exception Flows (what happens when errors occur)
8. Postconditions (what is true after completion)
9. Business Rules (constraints and rules)
10. Priority Level

Focus on business value and user experience rather than technical implementation details.
"""

def get_user_stories_prompt(analysis_results: dict) -> str:
    """
    Generate user stories section
    """
    return f"""
Based on the code analysis, create user stories that describe the functionality from a user's perspective.

Code Analysis Context:
- API Endpoints: {len(analysis_results.get('api_endpoints', []))}
- Business Logic Functions: {len(analysis_results.get('business_logic', []))}

Key Functions:
{format_functions_for_usecase(analysis_results.get('functions_found', []))}

Create user stories in the format:
"As a [user type], I want [functionality] so that [benefit]"

Include:
1. Epic-level user stories (high-level functionality)
2. Feature-level user stories (specific features)
3. Story-level user stories (detailed functionality)

For each user story, include:
- Story ID
- User Type
- Functionality
- Business Benefit
- Acceptance Criteria
- Priority

Identify different user types based on the system's functionality (e.g., end users, administrators, system integrators).
"""

def get_business_processes_prompt(analysis_results: dict) -> str:
    """
    Generate business process flows section
    """
    return f"""
Based on the code analysis, describe the business processes and how they flow through the system.

Code Analysis Context:
- Functions: {len(analysis_results.get('functions_found', []))}
- API Endpoints: {len(analysis_results.get('api_endpoints', []))}
- External Integrations: {len(analysis_results.get('external_integrations', []))}

Business Logic Functions:
{format_business_logic_for_usecase(analysis_results.get('business_logic', []))}

API Endpoints:
{format_endpoints_for_usecase(analysis_results.get('api_endpoints', []))}

Describe:
1. End-to-End Business Processes
2. Process Flow Diagrams (in text format)
3. Decision Points
4. Parallel Processes
5. Integration Points
6. Data Flow
7. Process Triggers
8. Process Outcomes

Focus on the business value and user experience rather than technical implementation.
"""

def get_acceptance_criteria_prompt(analysis_results: dict) -> str:
    """
    Generate acceptance criteria section
    """
    return f"""
Based on the code analysis, define specific, measurable acceptance criteria for the system functionality.

Code Analysis Context:
- API Endpoints: {len(analysis_results.get('api_endpoints', []))}
- Functions: {len(analysis_results.get('functions_found', []))}
- Business Logic: {len(analysis_results.get('business_logic', []))}

Key Functions:
{format_functions_for_usecase(analysis_results.get('functions_found', []))}

API Endpoints:
{format_endpoints_for_usecase(analysis_results.get('api_endpoints', []))}

Create acceptance criteria that are:
1. Specific and Measurable
2. Testable
3. Business-Focused
4. Clear and Unambiguous

For each major function or endpoint, define:
- Functional Acceptance Criteria
- Performance Acceptance Criteria
- Security Acceptance Criteria
- Usability Acceptance Criteria
- Integration Acceptance Criteria

Format as:
- Given [context]
- When [action]
- Then [expected outcome]
"""

def get_exception_scenarios_prompt(analysis_results: dict) -> str:
    """
    Generate exception scenarios section
    """
    return f"""
Based on the code analysis, identify exception scenarios and error conditions that the system should handle.

Code Analysis Context:
- Functions: {len(analysis_results.get('functions_found', []))}
- API Endpoints: {len(analysis_results.get('api_endpoints', []))}
- External Integrations: {len(analysis_results.get('external_integrations', []))}

Business Logic Functions:
{format_business_logic_for_usecase(analysis_results.get('business_logic', []))}

External Integrations:
{format_integrations_for_usecase(analysis_results.get('external_integrations', []))}

Identify exception scenarios for:
1. Input Validation Errors
2. Authentication/Authorization Failures
3. External Service Failures
4. Data Processing Errors
5. Network Connectivity Issues
6. Resource Exhaustion
7. Concurrent Access Issues
8. Data Integrity Violations

For each exception scenario, describe:
- Exception Condition
- Triggering Event
- Expected System Response
- User Experience
- Recovery Actions
- Prevention Measures
"""

# Helper functions for formatting data for prompts
def format_functions_for_usecase(functions: list) -> str:
    """Format functions for use case prompts"""
    if not functions:
        return "No functions identified"
    
    formatted = []
    for func in functions[:15]:  # Limit to first 15
        name = func.get('name', 'unknown')
        file = func.get('file', 'unknown')
        args = func.get('args', [])
        docstring = func.get('docstring', '')
        
        formatted.append(f"- {name}({', '.join(args)}) in {file}")
        if docstring:
            formatted.append(f"  Description: {docstring[:80]}...")
    
    return '\n'.join(formatted)

def format_endpoints_for_usecase(endpoints: list) -> str:
    """Format endpoints for use case prompts"""
    if not endpoints:
        return "No API endpoints identified"
    
    formatted = []
    for endpoint in endpoints[:15]:  # Limit to first 15
        method = endpoint.get('method', 'unknown')
        path = endpoint.get('endpoint', 'unknown')
        file = endpoint.get('file', 'unknown')
        
        formatted.append(f"- {method} {path} (defined in {file})")
    
    return '\n'.join(formatted)

def format_business_logic_for_usecase(business_logic: list) -> str:
    """Format business logic for use case prompts"""
    if not business_logic:
        return "No specific business logic identified"
    
    formatted = []
    for logic in business_logic[:15]:  # Limit to first 15
        name = logic.get('name', 'unknown')
        file = logic.get('file', 'unknown')
        
        formatted.append(f"- {name} in {file}")
    
    return '\n'.join(formatted)

def format_integrations_for_usecase(integrations: list) -> str:
    """Format integrations for use case prompts"""
    if not integrations:
        return "No external integrations identified"
    
    formatted = []
    for integration in integrations[:10]:  # Limit to first 10
        module = integration.get('module', 'unknown')
        file = integration.get('file', 'unknown')
        
        formatted.append(f"- {module} (used in {file})")
    
    return '\n'.join(formatted)
