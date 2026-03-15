"""
Lambda function for processing codebase uploads
Validates, extracts, and initiates the analysis workflow
"""

import json
import boto3
import uuid
import zipfile
import tarfile
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
stepfunctions = boto3.client('stepfunctions')

def handler(event, context):
    """
    Main handler for code upload processing
    
    Expected event structure:
    {
        "body": "base64_encoded_file_content",
        "filename": "codebase.zip",
        "content_type": "application/zip"
    }
    """
    try:
        logger.info(f"Processing upload event: {json.dumps(event)}")
        
        # Parse the request
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
            
        filename = body.get('filename', 'unknown')
        content_type = body.get('content_type', 'application/octet-stream')
        
        # Generate unique project ID
        project_id = str(uuid.uuid4())
        
        # Process the uploaded file
        file_info = process_uploaded_file(body, project_id, filename)
        
        # Store metadata in DynamoDB
        store_project_metadata(project_id, filename, file_info)
        
        # Start the analysis workflow
        execution_arn = start_analysis_workflow(project_id, file_info)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'project_id': project_id,
                'execution_arn': execution_arn,
                'status': 'processing_started',
                'message': 'Codebase uploaded successfully and analysis started'
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def process_uploaded_file(body: Dict, project_id: str, filename: str) -> Dict[str, Any]:
    """
    Process the uploaded file and extract code information
    """
    try:
        # Get file content (assuming base64 encoded)
        import base64
        file_content = base64.b64decode(body['body'])
        
        # Create temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file
            upload_path = os.path.join(temp_dir, filename)
            with open(upload_path, 'wb') as f:
                f.write(file_content)
            
            # Extract and analyze the archive
            extracted_info = extract_and_analyze_archive(upload_path, temp_dir)
            
            # Upload extracted files to S3
            s3_key = f"projects/{project_id}/codebase/"
            upload_to_s3(temp_dir, s3_key, extracted_info['files'])
            
            return {
                's3_key': s3_key,
                'file_count': extracted_info['file_count'],
                'languages': extracted_info['languages'],
                'total_size': extracted_info['total_size'],
                'structure': extracted_info['structure']
            }
            
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise

def extract_and_analyze_archive(archive_path: str, extract_dir: str) -> Dict[str, Any]:
    """
    Extract archive and analyze the codebase structure
    """
    file_count = 0
    languages = set()
    total_size = 0
    structure = {}
    
    try:
        # Extract based on file extension
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        elif archive_path.endswith(('.tar.gz', '.tgz')):
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_dir)
        elif archive_path.endswith('.tar'):
            with tarfile.open(archive_path, 'r') as tar_ref:
                tar_ref.extractall(extract_dir)
        else:
            # Single file upload
            os.makedirs(extract_dir, exist_ok=True)
            import shutil
            shutil.copy2(archive_path, extract_dir)
        
        # Analyze extracted files
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, extract_dir)
                
                # Skip hidden files and common non-code files
                if file.startswith('.') or file in ['node_modules', '__pycache__', '.git']:
                    continue
                
                file_count += 1
                file_size = os.path.getsize(file_path)
                total_size += file_size
                
                # Detect programming language
                language = detect_language(file)
                if language:
                    languages.add(language)
                
                # Build structure
                path_parts = relative_path.split(os.sep)
                current = structure
                for part in path_parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                current[path_parts[-1]] = {
                    'size': file_size,
                    'language': language
                }
    
    except Exception as e:
        logger.error(f"Error extracting archive: {str(e)}")
        raise
    
    return {
        'file_count': file_count,
        'languages': list(languages),
        'total_size': total_size,
        'structure': structure,
        'files': get_file_list(extract_dir)
    }

def detect_language(filename: str) -> str:
    """
    Detect programming language based on file extension
    """
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cs': 'csharp',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.m': 'matlab',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.less': 'less',
        '.xml': 'xml',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.txt': 'text'
    }
    
    _, ext = os.path.splitext(filename.lower())
    return extension_map.get(ext, 'unknown')

def get_file_list(directory: str) -> List[str]:
    """
    Get list of all files in directory
    """
    files = []
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if not filename.startswith('.'):
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, directory)
                files.append(relative_path)
    return files

def upload_to_s3(source_dir: str, s3_key_prefix: str, files: List[str]):
    """
    Upload extracted files to S3
    """
    bucket_name = os.environ['CODEBASE_BUCKET']
    
    for file_path in files:
        local_path = os.path.join(source_dir, file_path)
        s3_key = f"{s3_key_prefix}{file_path}"
        
        try:
            s3_client.upload_file(local_path, bucket_name, s3_key)
            logger.info(f"Uploaded {file_path} to s3://{bucket_name}/{s3_key}")
        except Exception as e:
            logger.error(f"Error uploading {file_path}: {str(e)}")
            raise

def store_project_metadata(project_id: str, filename: str, file_info: Dict[str, Any]):
    """
    Store project metadata in DynamoDB
    """
    table_name = os.environ['METADATA_TABLE']
    table = dynamodb.Table(table_name)
    
    metadata = {
        'project_id': project_id,
        'component_type': 'project',
        'filename': filename,
        'created_at': datetime.utcnow().isoformat(),
        'status': 'processing',
        'file_count': file_info['file_count'],
        'languages': file_info['languages'],
        'total_size': file_info['total_size'],
        's3_key': file_info['s3_key'],
        'structure': file_info['structure']
    }
    
    try:
        table.put_item(Item=metadata)
        logger.info(f"Stored metadata for project {project_id}")
    except Exception as e:
        logger.error(f"Error storing metadata: {str(e)}")
        raise

def start_analysis_workflow(project_id: str, file_info: Dict[str, Any]) -> str:
    """
    Start the Step Functions workflow for analysis
    """
    state_machine_arn = os.environ.get('STATE_MACHINE_ARN')
    if not state_machine_arn:
        # In a real deployment, this would be passed as an environment variable
        # For now, we'll construct it based on the stack name
        state_machine_arn = f"arn:aws:states:{os.environ['AWS_REGION']}:{os.environ['AWS_ACCOUNT_ID']}:stateMachine:code-to-brd-workflow"
    
    input_data = {
        'project_id': project_id,
        's3_key': file_info['s3_key'],
        'languages': file_info['languages'],
        'file_count': file_info['file_count']
    }
    
    try:
        response = stepfunctions.start_execution(
            stateMachineArn=state_machine_arn,
            name=f"code-analysis-{project_id}",
            input=json.dumps(input_data)
        )
        
        logger.info(f"Started workflow execution: {response['executionArn']}")
        return response['executionArn']
        
    except Exception as e:
        logger.error(f"Error starting workflow: {str(e)}")
        raise
