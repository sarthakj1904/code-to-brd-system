#!/usr/bin/env python3
"""
Test script for Code-to-BRD System deployment
Tests the API endpoints and functionality
"""

import requests
import json
import base64
import zipfile
import tempfile
import os
import time
from typing import Dict, Any

class CodeToBrdTester:
    """
    Test class for the Code-to-BRD system
    """
    
    def __init__(self, api_endpoint: str):
        """
        Initialize the tester
        
        Args:
            api_endpoint: The API Gateway endpoint URL
        """
        self.api_endpoint = api_endpoint.rstrip('/')
        self.session = requests.Session()
        
    def test_api_health(self) -> bool:
        """
        Test if the API is responding
        
        Returns:
            True if API is healthy
        """
        try:
            response = self.session.get(f"{self.api_endpoint}/projects")
            return response.status_code in [200, 404]  # 404 is OK if no projects exist
        except Exception as e:
            print(f"❌ API health check failed: {e}")
            return False
    
    def create_test_codebase(self) -> str:
        """
        Create a test codebase for testing
        
        Returns:
            Base64 encoded zip file content
        """
        # Create a simple test Python application
        test_code = '''
def calculate_total(items):
    """Calculate total price of items"""
    total = 0
    for item in items:
        total += item.get('price', 0)
    return total

def process_order(order_data):
    """Process customer order"""
    if not order_data.get('items'):
        raise ValueError("Order must contain items")
    
    total = calculate_total(order_data['items'])
    return {
        'order_id': order_data.get('id'),
        'total': total,
        'status': 'processed'
    }

def send_notification(message, recipient):
    """Send notification to recipient"""
    # Mock notification sending
    print(f"Sending notification to {recipient}: {message}")
    return True

class OrderProcessor:
    """Order processing service"""
    
    def __init__(self):
        self.processed_orders = []
    
    def process_order(self, order_data):
        """Process an order"""
        result = process_order(order_data)
        self.processed_orders.append(result)
        return result
    
    def get_processed_orders(self):
        """Get all processed orders"""
        return self.processed_orders
'''
        
        # Create a simple API endpoint file
        api_code = '''
from flask import Flask, request, jsonify
from order_processor import OrderProcessor

app = Flask(__name__)
processor = OrderProcessor()

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    data = request.get_json()
    try:
        result = processor.process_order(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all processed orders"""
    orders = processor.get_processed_orders()
    return jsonify({'orders': orders})

if __name__ == '__main__':
    app.run(debug=True)
'''
        
        # Create a requirements file
        requirements = '''
Flask==2.3.3
requests==2.31.0
'''
        
        # Create a README file
        readme = '''
# Test E-commerce Order Processing System

This is a simple order processing system that:
- Calculates order totals
- Processes customer orders
- Sends notifications
- Provides REST API endpoints

## API Endpoints

- POST /api/orders - Create a new order
- GET /api/orders - Get all processed orders

## Usage

```python
from order_processor import OrderProcessor

processor = OrderProcessor()
order_data = {
    'id': '12345',
    'items': [
        {'name': 'Product 1', 'price': 10.99},
        {'name': 'Product 2', 'price': 5.99}
    ]
}

result = processor.process_order(order_data)
print(result)
```
'''
        
        # Create zip file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            with zipfile.ZipFile(temp_file.name, 'w') as zip_file:
                zip_file.writestr('order_processor.py', test_code)
                zip_file.writestr('app.py', api_code)
                zip_file.writestr('requirements.txt', requirements)
                zip_file.writestr('README.md', readme)
            
            # Read and encode the zip file
            with open(temp_file.name, 'rb') as f:
                zip_content = f.read()
            
            # Clean up
            os.unlink(temp_file.name)
        
        return base64.b64encode(zip_content).decode('utf-8')
    
    def upload_codebase(self, zip_content: str, filename: str = "test-codebase.zip") -> Dict[str, Any]:
        """
        Upload a codebase to the system
        
        Args:
            zip_content: Base64 encoded zip file content
            filename: Name of the file
            
        Returns:
            Upload response
        """
        payload = {
            'body': zip_content,
            'filename': filename,
            'content_type': 'application/zip'
        }
        
        try:
            response = self.session.post(
                f"{self.api_endpoint}/upload",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            raise
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """
        Get project status
        
        Args:
            project_id: Project ID
            
        Returns:
            Project status
        """
        try:
            response = self.session.get(f"{self.api_endpoint}/projects/{project_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get project status: {e}")
            raise
    
    def wait_for_completion(self, project_id: str, timeout: int = 300) -> bool:
        """
        Wait for project processing to complete
        
        Args:
            project_id: Project ID
            timeout: Timeout in seconds
            
        Returns:
            True if completed successfully
        """
        print(f"⏳ Waiting for project {project_id} to complete processing...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status = self.get_project_status(project_id)
                project_status = status.get('status', 'unknown')
                
                print(f"📊 Project status: {project_status}")
                
                if project_status == 'completed':
                    print("✅ Project processing completed!")
                    return True
                elif project_status == 'failed':
                    print("❌ Project processing failed!")
                    return False
                
                time.sleep(10)  # Wait 10 seconds before checking again
                
            except Exception as e:
                print(f"⚠️ Error checking status: {e}")
                time.sleep(10)
        
        print("⏰ Timeout waiting for completion")
        return False
    
    def get_brd(self, project_id: str) -> Dict[str, Any]:
        """
        Get generated BRD
        
        Args:
            project_id: Project ID
            
        Returns:
            BRD content
        """
        try:
            response = self.session.get(f"{self.api_endpoint}/projects/{project_id}/brd")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get BRD: {e}")
            raise
    
    def get_usecases(self, project_id: str) -> Dict[str, Any]:
        """
        Get generated use cases
        
        Args:
            project_id: Project ID
            
        Returns:
            Use cases content
        """
        try:
            response = self.session.get(f"{self.api_endpoint}/projects/{project_id}/usecases")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get use cases: {e}")
            raise
    
    def get_tests(self, project_id: str) -> Dict[str, Any]:
        """
        Get generated test cases
        
        Args:
            project_id: Project ID
            
        Returns:
            Test cases content
        """
        try:
            response = self.session.get(f"{self.api_endpoint}/projects/{project_id}/tests")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get test cases: {e}")
            raise
    
    def get_traceability(self, project_id: str) -> Dict[str, Any]:
        """
        Get traceability matrix
        
        Args:
            project_id: Project ID
            
        Returns:
            Traceability matrix
        """
        try:
            response = self.session.get(f"{self.api_endpoint}/projects/{project_id}/traceability")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get traceability: {e}")
            raise
    
    def run_full_test(self) -> bool:
        """
        Run a complete test of the system
        
        Returns:
            True if all tests pass
        """
        print("🧪 Starting full system test...")
        
        # Test 1: API Health
        print("\n1️⃣ Testing API health...")
        if not self.test_api_health():
            return False
        print("✅ API is healthy")
        
        # Test 2: Create and upload test codebase
        print("\n2️⃣ Creating and uploading test codebase...")
        zip_content = self.create_test_codebase()
        upload_response = self.upload_codebase(zip_content)
        project_id = upload_response['project_id']
        print(f"✅ Codebase uploaded, project ID: {project_id}")
        
        # Test 3: Wait for processing
        print("\n3️⃣ Waiting for processing to complete...")
        if not self.wait_for_completion(project_id):
            return False
        
        # Test 4: Get BRD
        print("\n4️⃣ Testing BRD generation...")
        try:
            brd = self.get_brd(project_id)
            print(f"✅ BRD generated ({len(brd.get('brd_content', ''))} characters)")
        except Exception as e:
            print(f"❌ BRD generation failed: {e}")
            return False
        
        # Test 5: Get use cases
        print("\n5️⃣ Testing use case generation...")
        try:
            usecases = self.get_usecases(project_id)
            print(f"✅ Use cases generated ({len(usecases.get('usecase_content', ''))} characters)")
        except Exception as e:
            print(f"❌ Use case generation failed: {e}")
            return False
        
        # Test 6: Get test cases
        print("\n6️⃣ Testing test case generation...")
        try:
            tests = self.get_tests(project_id)
            total_tests = tests.get('total_tests', 0)
            print(f"✅ Test cases generated ({total_tests} total tests)")
        except Exception as e:
            print(f"❌ Test case generation failed: {e}")
            return False
        
        # Test 7: Get traceability
        print("\n7️⃣ Testing traceability matrix...")
        try:
            traceability = self.get_traceability(project_id)
            total_links = traceability.get('total_links', 0)
            print(f"✅ Traceability matrix created ({total_links} links)")
        except Exception as e:
            print(f"❌ Traceability generation failed: {e}")
            return False
        
        print("\n🎉 All tests passed! The system is working correctly.")
        return True

def main():
    """
    Main test function
    """
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python test-deployment.py <API_ENDPOINT>")
        print("Example: python test-deployment.py https://abc123.execute-api.us-east-1.amazonaws.com/prod")
        sys.exit(1)
    
    api_endpoint = sys.argv[1]
    
    print("🚀 Code-to-BRD System Test Suite")
    print(f"📍 API Endpoint: {api_endpoint}")
    print("=" * 50)
    
    tester = CodeToBrdTester(api_endpoint)
    
    if tester.run_full_test():
        print("\n✅ All tests passed! System is ready for use.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
