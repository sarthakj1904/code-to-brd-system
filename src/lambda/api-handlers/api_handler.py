"""
Lambda function for API Gateway handlers
Provides REST endpoints for project management and artifact retrieval
"""

import json
import boto3
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import parse_qs

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def handler(event, context):
    """
    Main API handler for Code-to-BRD system
    
    Supported endpoints:
    - GET /projects - List all projects
    - GET /projects/{project_id} - Get project details and artifacts
    - GET /projects/{project_id}/brd - Get BRD document
    - GET /projects/{project_id}/usecases - Get use cases
    - GET /projects/{project_id}/tests - Get test cases
    - GET /projects/{project_id}/traceability - Get traceability matrix
    """
    try:
        logger.info(f"API request: {json.dumps(event)}")
        
        # Parse the request
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        
        # Route the request
        if http_method == 'GET':
            if path == '/projects':
                return handle_list_projects()
            elif path.startswith('/projects/'):
                project_id = path_parameters.get('project_id')
                if not project_id:
                    return create_error_response(400, "Missing project_id")
                
                # Check for specific artifact requests
                if path.endswith('/brd'):
                    return handle_get_brd(project_id)
                elif path.endswith('/usecases'):
                    return handle_get_usecases(project_id)
                elif path.endswith('/tests'):
                    return handle_get_tests(project_id)
                elif path.endswith('/traceability'):
                    return handle_get_traceability(project_id)
                else:
                    return handle_get_project(project_id)
            else:
                return create_error_response(404, "Endpoint not found")
        else:
            return create_error_response(405, f"Method {http_method} not allowed")
            
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return create_error_response(500, "Internal server error")

def handle_list_projects() -> Dict[str, Any]:
    """
    List all projects with their status
    """
    try:
        table_name = os.environ['METADATA_TABLE']
        table = dynamodb.Table(table_name)
        
        # Query for all projects
        response = table.query(
            IndexName='component-lookup',
            KeyConditionExpression='component_type = :component_type',
            ExpressionAttributeValues={
                ':component_type': 'project'
            }
        )
        
        projects = []
        for item in response['Items']:
            projects.append({
                'project_id': item['project_id'],
                'filename': item.get('filename', 'unknown'),
                'created_at': item.get('created_at'),
                'status': item.get('status', 'unknown'),
                'languages': item.get('languages', []),
                'file_count': item.get('file_count', 0)
            })
        
        return create_success_response({
            'projects': projects,
            'total': len(projects)
        })
        
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        return create_error_response(500, "Failed to list projects")

def handle_get_project(project_id: str) -> Dict[str, Any]:
    """
    Get project details and status
    """
    try:
        table_name = os.environ['METADATA_TABLE']
        table = dynamodb.Table(table_name)
        
        # Get project metadata
        project_response = table.get_item(
            Key={
                'project_id': project_id,
                'component_type': 'project'
            }
        )
        
        if 'Item' not in project_response:
            return create_error_response(404, "Project not found")
        
        project = project_response['Item']
        
        # Get all components for this project
        components_response = table.query(
            KeyConditionExpression='project_id = :project_id',
            ExpressionAttributeValues={
                ':project_id': project_id
            }
        )
        
        components = {}
        for item in components_response['Items']:
            component_type = item['component_type']
            if component_type != 'project':
                components[component_type] = {
                    'status': item.get('status', 'unknown'),
                    'created_at': item.get('created_at'),
                    'has_result': 'result' in item
                }
        
        return create_success_response({
            'project_id': project_id,
            'filename': project.get('filename'),
            'created_at': project.get('created_at'),
            'status': project.get('status'),
            'languages': project.get('languages', []),
            'file_count': project.get('file_count', 0),
            'total_size': project.get('total_size', 0),
            's3_key': project.get('s3_key'),
            'components': components
        })
        
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {str(e)}")
        return create_error_response(500, "Failed to get project details")

def handle_get_brd(project_id: str) -> Dict[str, Any]:
    """
    Get BRD document for a project
    """
    try:
        table_name = os.environ['METADATA_TABLE']
        table = dynamodb.Table(table_name)
        
        # Get BRD results
        response = table.get_item(
            Key={
                'project_id': project_id,
                'component_type': 'brd_generation'
            }
        )
        
        if 'Item' not in response:
            return create_error_response(404, "BRD not found for this project")
        
        brd_data = response['Item']
        result = brd_data.get('result', {})
        
        # Store BRD in S3 for download
        bucket_name = os.environ['ARTIFACTS_BUCKET']
        s3_key = f"projects/{project_id}/brd.md"
        
        brd_content = result.get('brd_content', '')
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=brd_content,
            ContentType='text/markdown'
        )
        
        # Generate download URL
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=3600  # 1 hour
        )
        
        return create_success_response({
            'project_id': project_id,
            'brd_content': brd_content,
            'sections': result.get('sections', {}),
            'generation_timestamp': result.get('generation_timestamp'),
            'download_url': download_url
        })
        
    except Exception as e:
        logger.error(f"Error getting BRD for project {project_id}: {str(e)}")
        return create_error_response(500, "Failed to get BRD")

def handle_get_usecases(project_id: str) -> Dict[str, Any]:
    """
    Get use cases for a project
    """
    try:
        table_name = os.environ['METADATA_TABLE']
        table = dynamodb.Table(table_name)
        
        # Get use case results
        response = table.get_item(
            Key={
                'project_id': project_id,
                'component_type': 'usecase_generation'
            }
        )
        
        if 'Item' not in response:
            return create_error_response(404, "Use cases not found for this project")
        
        usecase_data = response['Item']
        result = usecase_data.get('result', {})
        
        # Store use cases in S3 for download
        bucket_name = os.environ['ARTIFACTS_BUCKET']
        s3_key = f"projects/{project_id}/usecases.md"
        
        usecase_content = result.get('usecase_content', '')
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=usecase_content,
            ContentType='text/markdown'
        )
        
        # Generate download URL
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=3600  # 1 hour
        )
        
        return create_success_response({
            'project_id': project_id,
            'usecase_content': usecase_content,
            'scenarios': result.get('scenarios', []),
            'generation_timestamp': result.get('generation_timestamp'),
            'download_url': download_url
        })
        
    except Exception as e:
        logger.error(f"Error getting use cases for project {project_id}: {str(e)}")
        return create_error_response(500, "Failed to get use cases")

def handle_get_tests(project_id: str) -> Dict[str, Any]:
    """
    Get test cases for a project
    """
    try:
        table_name = os.environ['METADATA_TABLE']
        table = dynamodb.Table(table_name)
        
        # Get test results
        response = table.get_item(
            Key={
                'project_id': project_id,
                'component_type': 'test_generation'
            }
        )
        
        if 'Item' not in response:
            return create_error_response(404, "Test cases not found for this project")
        
        test_data = response['Item']
        result = test_data.get('result', {})
        
        # Store tests in S3 for download
        bucket_name = os.environ['ARTIFACTS_BUCKET']
        
        # Create combined test document
        test_content = create_combined_test_document(result)
        s3_key = f"projects/{project_id}/tests.md"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=test_content,
            ContentType='text/markdown'
        )
        
        # Generate download URL
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=3600  # 1 hour
        )
        
        return create_success_response({
            'project_id': project_id,
            'unit_tests': result.get('unit_tests', []),
            'functional_tests': result.get('functional_tests', []),
            'edge_case_tests': result.get('edge_case_tests', []),
            'total_tests': result.get('total_tests', 0),
            'generation_timestamp': result.get('generation_timestamp'),
            'download_url': download_url
        })
        
    except Exception as e:
        logger.error(f"Error getting tests for project {project_id}: {str(e)}")
        return create_error_response(500, "Failed to get test cases")

def handle_get_traceability(project_id: str) -> Dict[str, Any]:
    """
    Get traceability matrix for a project
    """
    try:
        table_name = os.environ['METADATA_TABLE']
        table = dynamodb.Table(table_name)
        
        # Get traceability results
        response = table.get_item(
            Key={
                'project_id': project_id,
                'component_type': 'traceability'
            }
        )
        
        if 'Item' not in response:
            return create_error_response(404, "Traceability matrix not found for this project")
        
        traceability_data = response['Item']
        result = traceability_data.get('result', {})
        
        return create_success_response({
            'project_id': project_id,
            'traceability_matrix': result.get('traceability_matrix', {}),
            'total_links': result.get('total_links', 0),
            'creation_timestamp': result.get('creation_timestamp')
        })
        
    except Exception as e:
        logger.error(f"Error getting traceability for project {project_id}: {str(e)}")
        return create_error_response(500, "Failed to get traceability matrix")

def create_combined_test_document(test_result: Dict[str, Any]) -> str:
    """
    Create a combined test document from all test types
    """
    content = ["# Test Cases\n"]
    
    # Unit Tests
    unit_tests = test_result.get('unit_tests', [])
    if unit_tests:
        content.append("## Unit Tests\n")
        for test in unit_tests:
            content.append(f"### {test.get('function', 'Unknown Function')}\n")
            content.append(f"**File:** {test.get('file', 'Unknown')}\n")
            content.append(f"**Test Content:**\n```\n{test.get('test_content', '')}\n```\n")
    
    # Functional Tests
    functional_tests = test_result.get('functional_tests', [])
    if functional_tests:
        content.append("## Functional Tests\n")
        for test in functional_tests:
            content.append(f"### {test.get('endpoint', 'Unknown Endpoint')}\n")
            content.append(f"**Method:** {test.get('method', 'Unknown')}\n")
            content.append(f"**Test Content:**\n```\n{test.get('test_content', '')}\n```\n")
    
    # Edge Case Tests
    edge_case_tests = test_result.get('edge_case_tests', [])
    if edge_case_tests:
        content.append("## Edge Case Tests\n")
        for test in edge_case_tests:
            content.append(f"**Test Content:**\n```\n{test.get('test_content', '')}\n```\n")
    
    return '\n'.join(content)

def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a successful API response
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(data, default=str)
    }

def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Create an error API response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps({
            'error': message,
            'timestamp': datetime.utcnow().isoformat()
        })
    }
