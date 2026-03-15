"""
BRD Generation Prompts for AWS Bedrock
Contains specialized prompts for generating Business Requirement Documents
"""

def get_brd_generation_prompt(analysis_results: dict) -> str:
    """
    Generate a comprehensive prompt for BRD creation
    """
    prompt = f"""
You are an expert business analyst tasked with creating a comprehensive Business Requirement Document (BRD) based on code analysis results.

CODE ANALYSIS RESULTS:
- Programming Languages: {', '.join(analysis_results.get('languages_analyzed', []))}
- Total Functions: {len(analysis_results.get('functions_found', []))}
- Total Classes: {len(analysis_results.get('classes_found', []))}
- API Endpoints: {len(analysis_results.get('api_endpoints', []))}
- Database Operations: {len(analysis_results.get('database_operations', []))}
- External Integrations: {len(analysis_results.get('external_integrations', []))}

KEY FUNCTIONS IDENTIFIED:
{format_functions_for_brd(analysis_results.get('functions_found', []))}

API ENDPOINTS DISCOVERED:
{format_endpoints_for_brd(analysis_results.get('api_endpoints', []))}

EXTERNAL INTEGRATIONS:
{format_integrations_for_brd(analysis_results.get('external_integrations', []))}

BUSINESS LOGIC COMPONENTS:
{format_business_logic_for_brd(analysis_results.get('business_logic', []))}

Please create a professional BRD with the following structure:

# BUSINESS REQUIREMENT DOCUMENT

## 1. EXECUTIVE SUMMARY
Provide a high-level overview of the system's purpose, key capabilities, and business value.

## 2. BUSINESS OBJECTIVES
Define the primary business goals this system aims to achieve.

## 3. FUNCTIONAL REQUIREMENTS
Detail the core functionality based on the code analysis:
- User-facing features
- System capabilities
- Data processing requirements
- Integration requirements

## 4. NON-FUNCTIONAL REQUIREMENTS
Specify performance, security, scalability, and reliability requirements.

## 5. SYSTEM ARCHITECTURE OVERVIEW
Describe the high-level system architecture based on the code structure.

## 6. DATA REQUIREMENTS
Define data models, storage requirements, and data flow.

## 7. INTEGRATION REQUIREMENTS
Detail external system integrations and API requirements.

## 8. SECURITY REQUIREMENTS
Specify authentication, authorization, and data protection requirements.

## 9. PERFORMANCE REQUIREMENTS
Define response times, throughput, and scalability requirements.

## 10. RISK ASSESSMENT
Identify potential risks and mitigation strategies.

## 11. ACCEPTANCE CRITERIA
Define measurable criteria for system acceptance.

Make the document clear, concise, and suitable for both technical and non-technical stakeholders. Use professional business language and ensure all requirements are specific and measurable.
"""
    return prompt

def get_brd_section_prompt(section: str, analysis_results: dict) -> str:
    """
    Generate a prompt for a specific BRD section
    """
    section_prompts = {
        'executive_summary': get_executive_summary_prompt(analysis_results),
        'functional_requirements': get_functional_requirements_prompt(analysis_results),
        'system_architecture': get_system_architecture_prompt(analysis_results),
        'integration_requirements': get_integration_requirements_prompt(analysis_results),
        'security_requirements': get_security_requirements_prompt(analysis_results),
        'performance_requirements': get_performance_requirements_prompt(analysis_results)
    }
    
    return section_prompts.get(section, get_brd_generation_prompt(analysis_results))

def get_executive_summary_prompt(analysis_results: dict) -> str:
    """
    Generate executive summary section
    """
    return f"""
Based on the code analysis, create an executive summary for the BRD that includes:

1. System Purpose: What does this system do based on the code analysis?
2. Key Capabilities: What are the main features and functions?
3. Business Value: How does this system provide value to the organization?
4. Scope: What is included and excluded from this system?

Code Analysis Context:
- Languages: {', '.join(analysis_results.get('languages_analyzed', []))}
- Functions: {len(analysis_results.get('functions_found', []))}
- API Endpoints: {len(analysis_results.get('api_endpoints', []))}
- External Integrations: {len(analysis_results.get('external_integrations', []))}

Write a concise executive summary (2-3 paragraphs) suitable for C-level executives.
"""

def get_functional_requirements_prompt(analysis_results: dict) -> str:
    """
    Generate functional requirements section
    """
    return f"""
Based on the code analysis, create detailed functional requirements including:

1. Core Business Functions: What are the main business processes supported?
2. User Interface Requirements: What user interactions are supported?
3. Data Processing Requirements: How is data processed and transformed?
4. Integration Requirements: What external systems are integrated?

Key Functions Found:
{format_functions_for_brd(analysis_results.get('functions_found', []))}

API Endpoints:
{format_endpoints_for_brd(analysis_results.get('api_endpoints', []))}

Business Logic:
{format_business_logic_for_brd(analysis_results.get('business_logic', []))}

Format each requirement with:
- Requirement ID (e.g., FR-001)
- Description
- Priority (High/Medium/Low)
- Acceptance Criteria
"""

def get_system_architecture_prompt(analysis_results: dict) -> str:
    """
    Generate system architecture section
    """
    return f"""
Based on the code analysis, describe the system architecture including:

1. High-Level Architecture: Overall system design and components
2. Technology Stack: Programming languages and frameworks used
3. Data Flow: How data moves through the system
4. Component Relationships: How different parts interact

Code Analysis Context:
- Programming Languages: {', '.join(analysis_results.get('languages_analyzed', []))}
- Classes and Objects: {len(analysis_results.get('classes_found', []))}
- Database Operations: {len(analysis_results.get('database_operations', []))}
- External Integrations: {len(analysis_results.get('external_integrations', []))}

Create a clear architectural overview suitable for technical stakeholders.
"""

def get_integration_requirements_prompt(analysis_results: dict) -> str:
    """
    Generate integration requirements section
    """
    return f"""
Based on the code analysis, define integration requirements including:

1. External System Integrations: What third-party services are integrated?
2. API Requirements: What APIs are exposed or consumed?
3. Data Exchange Requirements: How is data shared with external systems?
4. Integration Patterns: What integration patterns are used?

External Integrations Found:
{format_integrations_for_brd(analysis_results.get('external_integrations', []))}

API Endpoints:
{format_endpoints_for_brd(analysis_results.get('api_endpoints', []))}

For each integration, specify:
- Integration Name
- Purpose
- Data Format
- Authentication Method
- Error Handling
"""

def get_security_requirements_prompt(analysis_results: dict) -> str:
    """
    Generate security requirements section
    """
    return f"""
Based on the code analysis, define security requirements including:

1. Authentication Requirements: How are users authenticated?
2. Authorization Requirements: What access controls are in place?
3. Data Protection: How is sensitive data protected?
4. Communication Security: How is data secured in transit?

Code Analysis Context:
- API Endpoints: {len(analysis_results.get('api_endpoints', []))}
- External Integrations: {len(analysis_results.get('external_integrations', []))}
- Database Operations: {len(analysis_results.get('database_operations', []))}

Identify security requirements based on the system's functionality and integrations.
"""

def get_performance_requirements_prompt(analysis_results: dict) -> str:
    """
    Generate performance requirements section
    """
    return f"""
Based on the code analysis, define performance requirements including:

1. Response Time Requirements: How fast should the system respond?
2. Throughput Requirements: How many requests can the system handle?
3. Scalability Requirements: How should the system scale?
4. Resource Utilization: What are the resource constraints?

Code Analysis Context:
- API Endpoints: {len(analysis_results.get('api_endpoints', []))}
- Functions: {len(analysis_results.get('functions_found', []))}
- External Integrations: {len(analysis_results.get('external_integrations', []))}

Define measurable performance criteria based on the system's capabilities.
"""

# Helper functions for formatting data for prompts
def format_functions_for_brd(functions: list) -> str:
    """Format functions for BRD prompts"""
    if not functions:
        return "No functions identified"
    
    formatted = []
    for func in functions[:10]:  # Limit to first 10
        name = func.get('name', 'unknown')
        file = func.get('file', 'unknown')
        args = func.get('args', [])
        docstring = func.get('docstring', '')
        
        formatted.append(f"- {name}({', '.join(args)}) in {file}")
        if docstring:
            formatted.append(f"  Description: {docstring[:100]}...")
    
    return '\n'.join(formatted)

def format_endpoints_for_brd(endpoints: list) -> str:
    """Format endpoints for BRD prompts"""
    if not endpoints:
        return "No API endpoints identified"
    
    formatted = []
    for endpoint in endpoints[:10]:  # Limit to first 10
        method = endpoint.get('method', 'unknown')
        path = endpoint.get('endpoint', 'unknown')
        file = endpoint.get('file', 'unknown')
        
        formatted.append(f"- {method} {path} (defined in {file})")
    
    return '\n'.join(formatted)

def format_integrations_for_brd(integrations: list) -> str:
    """Format integrations for BRD prompts"""
    if not integrations:
        return "No external integrations identified"
    
    formatted = []
    for integration in integrations[:10]:  # Limit to first 10
        module = integration.get('module', 'unknown')
        file = integration.get('file', 'unknown')
        
        formatted.append(f"- {module} (used in {file})")
    
    return '\n'.join(formatted)

def format_business_logic_for_brd(business_logic: list) -> str:
    """Format business logic for BRD prompts"""
    if not business_logic:
        return "No specific business logic identified"
    
    formatted = []
    for logic in business_logic[:10]:  # Limit to first 10
        name = logic.get('name', 'unknown')
        file = logic.get('file', 'unknown')
        
        formatted.append(f"- {name} in {file}")
    
    return '\n'.join(formatted)
