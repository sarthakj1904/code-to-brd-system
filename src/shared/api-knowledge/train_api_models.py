#!/usr/bin/env python3
"""
API Model Training Script
Trains models on API documentation for better integration detection
"""

import os
import sys
import json
import logging
from typing import List, Optional
import argparse
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from api_doc_trainer import APIDocTrainer
from enhanced_integration_detector import EnhancedIntegrationDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description='Train API models on documentation')
    parser.add_argument('--services', nargs='+', help='Specific services to train on')
    parser.add_argument('--all', action='store_true', help='Train on all available services')
    parser.add_argument('--update-patterns', action='store_true', help='Update integration patterns after training')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    
    # Set environment variables if not already set
    if not os.environ.get('API_KNOWLEDGE_BUCKET'):
        os.environ['API_KNOWLEDGE_BUCKET'] = 'api-knowledge-base'
    if not os.environ.get('API_DOCS_TABLE'):
        os.environ['API_DOCS_TABLE'] = 'api-documentation'
    
    try:
        # Initialize trainer
        trainer = APIDocTrainer(region_name=args.region)
        
        # Determine services to train on
        if args.all:
            services = None  # Train on all services
        elif args.services:
            services = args.services
        else:
            # Default services for initial training
            services = ['stripe', 'twilio', 'aws', 'sendgrid']
        
        logger.info(f"Starting API documentation training for services: {services or 'all'}")
        
        # Train on API documentation
        training_results = trainer.train_on_api_documentation(services)
        
        logger.info("Training completed successfully!")
        logger.info(f"Services trained: {len(training_results['services_trained'])}")
        logger.info(f"Total docs processed: {training_results['total_docs_processed']}")
        
        if training_results['errors']:
            logger.warning(f"Training errors: {training_results['errors']}")
        
        # Update integration patterns if requested
        if args.update_patterns:
            logger.info("Updating integration detection patterns...")
            pattern_results = trainer.update_integration_detection_patterns()
            logger.info(f"Pattern update result: {pattern_results}")
        
        # Test the enhanced detector
        logger.info("Testing enhanced integration detector...")
        test_enhanced_detector()
        
        # Save training results
        save_training_results(training_results)
        
        logger.info("API model training completed successfully!")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        sys.exit(1)

def test_enhanced_detector():
    """Test the enhanced integration detector"""
    try:
        detector = EnhancedIntegrationDetector()
        
        # Test code samples
        test_cases = [
            {
                'name': 'Stripe Python Code',
                'code': '''
import stripe
stripe.api_key = "sk_test_..."
charge = stripe.Charge.create(
    amount=2000,
    currency='usd',
    source='tok_visa'
)
''',
                'filename': 'payment.py',
                'language': 'python'
            },
            {
                'name': 'Twilio JavaScript Code',
                'code': '''
const twilio = require('twilio');
const client = twilio(accountSid, authToken);
client.messages.create({
    body: 'Hello from Twilio!',
    from: '+1234567890',
    to: '+0987654321'
});
''',
                'filename': 'sms.js',
                'language': 'javascript'
            },
            {
                'name': 'AWS Python Code',
                'code': '''
import boto3
s3 = boto3.client('s3')
response = s3.list_buckets()
for bucket in response['Buckets']:
    print(bucket['Name'])
''',
                'filename': 'aws_s3.py',
                'language': 'python'
            }
        ]
        
        for test_case in test_cases:
            logger.info(f"Testing: {test_case['name']}")
            integrations = detector.detect_integrations(
                test_case['code'],
                test_case['filename'],
                test_case['language']
            )
            
            logger.info(f"Detected {len(integrations)} integrations:")
            for integration in integrations:
                logger.info(f"  - {integration['service']} ({integration['type']}) - Confidence: {integration['confidence']}")
        
    except Exception as e:
        logger.error(f"Error testing enhanced detector: {str(e)}")

def save_training_results(results: dict):
    """Save training results to file"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"training_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Training results saved to {filename}")
        
    except Exception as e:
        logger.error(f"Error saving training results: {str(e)}")

def list_available_services():
    """List all available services for training"""
    trainer = APIDocTrainer()
    services = list(trainer.api_services.keys())
    
    print("Available services for training:")
    for service in services:
        config = trainer.api_services[service]
        print(f"  - {service}: {config['base_url']}")
    
    return services

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("API Documentation Training Script")
        print("Usage:")
        print("  python train_api_models.py --all                    # Train on all services")
        print("  python train_api_models.py --services stripe twilio # Train on specific services")
        print("  python train_api_models.py --list                   # List available services")
        print("  python train_api_models.py --help                   # Show help")
        
        if '--list' in sys.argv:
            list_available_services()
    else:
        main()
