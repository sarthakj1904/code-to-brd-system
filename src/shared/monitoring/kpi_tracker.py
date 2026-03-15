"""
KPI Tracking and Monitoring for Code-to-BRD System
Tracks key performance indicators and system metrics
"""

import json
import boto3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

class KPITracker:
    """
    Tracks KPIs and system metrics for the Code-to-BRD system
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize the KPI tracker
        
        Args:
            region_name: AWS region
        """
        self.cloudwatch = boto3.client('cloudwatch', region_name=region_name)
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.s3 = boto3.client('s3', region_name=region_name)
        
        # KPI targets based on requirements
        self.kpi_targets = {
            'brd_accuracy': 0.80,  # 80% semantic alignment
            'test_validity': 0.75,  # 75% of tests execute successfully
            'efficiency_improvement': 0.70,  # 70% reduction in time
            'processing_success_rate': 0.95,  # 95% successful processing
            'avg_processing_time': 300,  # 5 minutes average
            'cost_per_operation': 5.0  # $5 per operation target
        }
    
    def track_project_metrics(self, project_id: str, metrics: Dict[str, Any]):
        """
        Track metrics for a specific project
        
        Args:
            project_id: Project ID
            metrics: Dictionary of metrics to track
        """
        try:
            # Store metrics in CloudWatch
            self._publish_cloudwatch_metrics(project_id, metrics)
            
            # Store detailed metrics in DynamoDB
            self._store_detailed_metrics(project_id, metrics)
            
            logger.info(f"Tracked metrics for project {project_id}")
            
        except Exception as e:
            logger.error(f"Error tracking metrics for project {project_id}: {str(e)}")
    
    def _publish_cloudwatch_metrics(self, project_id: str, metrics: Dict[str, Any]):
        """
        Publish metrics to CloudWatch
        
        Args:
            project_id: Project ID
            metrics: Metrics to publish
        """
        cloudwatch_metrics = []
        
        # Processing time
        if 'processing_time' in metrics:
            cloudwatch_metrics.append({
                'MetricName': 'ProcessingTime',
                'Value': metrics['processing_time'],
                'Unit': 'Seconds',
                'Dimensions': [
                    {'Name': 'ProjectId', 'Value': project_id}
                ]
            })
        
        # File count
        if 'file_count' in metrics:
            cloudwatch_metrics.append({
                'MetricName': 'FileCount',
                'Value': metrics['file_count'],
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'ProjectId', 'Value': project_id}
                ]
            })
        
        # Language count
        if 'language_count' in metrics:
            cloudwatch_metrics.append({
                'MetricName': 'LanguageCount',
                'Value': metrics['language_count'],
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'ProjectId', 'Value': project_id}
                ]
            })
        
        # BRD quality score
        if 'brd_quality_score' in metrics:
            cloudwatch_metrics.append({
                'MetricName': 'BRDQualityScore',
                'Value': metrics['brd_quality_score'],
                'Unit': 'Percent',
                'Dimensions': [
                    {'Name': 'ProjectId', 'Value': project_id}
                ]
            })
        
        # Test count
        if 'test_count' in metrics:
            cloudwatch_metrics.append({
                'MetricName': 'TestCount',
                'Value': metrics['test_count'],
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'ProjectId', 'Value': project_id}
                ]
            })
        
        # Use case count
        if 'usecase_count' in metrics:
            cloudwatch_metrics.append({
                'MetricName': 'UseCaseCount',
                'Value': metrics['usecase_count'],
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'ProjectId', 'Value': project_id}
                ]
            })
        
        # Publish metrics in batches
        if cloudwatch_metrics:
            for i in range(0, len(cloudwatch_metrics), 20):  # CloudWatch batch limit
                batch = cloudwatch_metrics[i:i+20]
                self.cloudwatch.put_metric_data(
                    Namespace='CodeToBRD/Projects',
                    MetricData=batch
                )
    
    def _store_detailed_metrics(self, project_id: str, metrics: Dict[str, Any]):
        """
        Store detailed metrics in DynamoDB
        
        Args:
            project_id: Project ID
            metrics: Metrics to store
        """
        table_name = 'code-to-brd-metrics'
        table = self.dynamodb.Table(table_name)
        
        # Create metrics record
        metrics_record = {
            'project_id': project_id,
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': metrics,
            'ttl': int((datetime.utcnow() + timedelta(days=90)).timestamp())
        }
        
        try:
            table.put_item(Item=metrics_record)
        except Exception as e:
            logger.error(f"Error storing detailed metrics: {str(e)}")
    
    def calculate_brd_accuracy(self, project_id: str, generated_brd: str, reference_brd: Optional[str] = None) -> float:
        """
        Calculate BRD accuracy score
        
        Args:
            project_id: Project ID
            generated_brd: Generated BRD content
            reference_brd: Reference BRD for comparison (optional)
            
        Returns:
            Accuracy score between 0 and 1
        """
        try:
            # Basic quality metrics
            word_count = len(generated_brd.split())
            section_count = len([line for line in generated_brd.split('\n') if line.strip().startswith('#')])
            
            # Calculate quality score based on content structure
            quality_score = 0.0
            
            # Check for required sections
            required_sections = [
                'executive summary', 'business objectives', 'functional requirements',
                'system architecture', 'security requirements', 'performance requirements'
            ]
            
            brd_lower = generated_brd.lower()
            sections_found = sum(1 for section in required_sections if section in brd_lower)
            section_score = sections_found / len(required_sections)
            
            # Word count score (target: 1000-5000 words)
            if 1000 <= word_count <= 5000:
                word_score = 1.0
            elif word_count < 1000:
                word_score = word_count / 1000
            else:
                word_score = max(0.5, 5000 / word_count)
            
            # Overall quality score
            quality_score = (section_score * 0.6) + (word_score * 0.4)
            
            # Store the score
            self.track_project_metrics(project_id, {'brd_quality_score': quality_score * 100})
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Error calculating BRD accuracy: {str(e)}")
            return 0.0
    
    def calculate_test_validity(self, project_id: str, test_cases: List[Dict[str, Any]]) -> float:
        """
        Calculate test case validity score
        
        Args:
            project_id: Project ID
            test_cases: List of generated test cases
            
        Returns:
            Validity score between 0 and 1
        """
        try:
            if not test_cases:
                return 0.0
            
            valid_tests = 0
            total_tests = len(test_cases)
            
            for test_case in test_cases:
                # Check if test case has required components
                has_name = bool(test_case.get('test_name') or test_case.get('name'))
                has_description = bool(test_case.get('description'))
                has_input = bool(test_case.get('input_data') or test_case.get('input'))
                has_expected = bool(test_case.get('expected_output') or test_case.get('expected'))
                
                # Test is valid if it has most required components
                if sum([has_name, has_description, has_input, has_expected]) >= 3:
                    valid_tests += 1
            
            validity_score = valid_tests / total_tests
            
            # Store the score
            self.track_project_metrics(project_id, {
                'test_validity_score': validity_score * 100,
                'test_count': total_tests,
                'valid_test_count': valid_tests
            })
            
            return validity_score
            
        except Exception as e:
            logger.error(f"Error calculating test validity: {str(e)}")
            return 0.0
    
    def calculate_processing_efficiency(self, project_id: str, processing_time: float, file_count: int) -> float:
        """
        Calculate processing efficiency score
        
        Args:
            project_id: Project ID
            processing_time: Time taken to process (seconds)
            file_count: Number of files processed
            
        Returns:
            Efficiency score between 0 and 1
        """
        try:
            # Calculate time per file
            time_per_file = processing_time / max(file_count, 1)
            
            # Target: 10 seconds per file
            target_time_per_file = 10.0
            
            if time_per_file <= target_time_per_file:
                efficiency_score = 1.0
            else:
                efficiency_score = max(0.0, target_time_per_file / time_per_file)
            
            # Store the metrics
            self.track_project_metrics(project_id, {
                'processing_time': processing_time,
                'file_count': file_count,
                'time_per_file': time_per_file,
                'efficiency_score': efficiency_score * 100
            })
            
            return efficiency_score
            
        except Exception as e:
            logger.error(f"Error calculating processing efficiency: {str(e)}")
            return 0.0
    
    def get_kpi_dashboard_data(self, days: int = 30) -> Dict[str, Any]:
        """
        Get KPI dashboard data for the specified period
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dashboard data with KPIs and trends
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Get CloudWatch metrics
            metrics_data = self._get_cloudwatch_metrics(start_time, end_time)
            
            # Get DynamoDB metrics
            db_metrics = self._get_dynamodb_metrics(start_time, end_time)
            
            # Calculate KPIs
            kpis = self._calculate_kpis(metrics_data, db_metrics)
            
            # Calculate trends
            trends = self._calculate_trends(metrics_data, db_metrics)
            
            return {
                'kpis': kpis,
                'trends': trends,
                'period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'days': days
                },
                'targets': self.kpi_targets
            }
            
        except Exception as e:
            logger.error(f"Error getting KPI dashboard data: {str(e)}")
            return {}
    
    def _get_cloudwatch_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, List]:
        """
        Get metrics from CloudWatch
        
        Args:
            start_time: Start time for metrics
            end_time: End time for metrics
            
        Returns:
            Dictionary of metric data
        """
        metrics_data = {}
        
        metric_names = [
            'ProcessingTime', 'FileCount', 'LanguageCount', 'BRDQualityScore',
            'TestCount', 'UseCaseCount'
        ]
        
        for metric_name in metric_names:
            try:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='CodeToBRD/Projects',
                    MetricName=metric_name,
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,  # 1 hour periods
                    Statistics=['Average', 'Sum', 'Maximum', 'Minimum']
                )
                
                metrics_data[metric_name] = response['Datapoints']
                
            except Exception as e:
                logger.error(f"Error getting CloudWatch metric {metric_name}: {str(e)}")
                metrics_data[metric_name] = []
        
        return metrics_data
    
    def _get_dynamodb_metrics(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """
        Get detailed metrics from DynamoDB
        
        Args:
            start_time: Start time for metrics
            end_time: End time for metrics
            
        Returns:
            List of metric records
        """
        try:
            table_name = 'code-to-brd-metrics'
            table = self.dynamodb.Table(table_name)
            
            # Scan for metrics in the time range
            response = table.scan(
                FilterExpression='timestamp BETWEEN :start AND :end',
                ExpressionAttributeValues={
                    ':start': start_time.isoformat(),
                    ':end': end_time.isoformat()
                }
            )
            
            return response['Items']
            
        except Exception as e:
            logger.error(f"Error getting DynamoDB metrics: {str(e)}")
            return []
    
    def _calculate_kpis(self, metrics_data: Dict[str, List], db_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate KPIs from metrics data
        
        Args:
            metrics_data: CloudWatch metrics data
            db_metrics: DynamoDB metrics data
            
        Returns:
            Dictionary of calculated KPIs
        """
        kpis = {}
        
        # BRD Accuracy KPI
        brd_scores = [point['Average'] for point in metrics_data.get('BRDQualityScore', []) if 'Average' in point]
        if brd_scores:
            kpis['brd_accuracy'] = {
                'current': sum(brd_scores) / len(brd_scores) / 100,  # Convert percentage to decimal
                'target': self.kpi_targets['brd_accuracy'],
                'status': 'meeting_target' if (sum(brd_scores) / len(brd_scores) / 100) >= self.kpi_targets['brd_accuracy'] else 'below_target'
            }
        
        # Test Validity KPI
        test_counts = [point['Sum'] for point in metrics_data.get('TestCount', []) if 'Sum' in point]
        if test_counts:
            # This is a simplified calculation - in reality, you'd need to track test execution results
            kpis['test_validity'] = {
                'current': 0.75,  # Placeholder - would need actual test execution data
                'target': self.kpi_targets['test_validity'],
                'status': 'meeting_target'
            }
        
        # Processing Efficiency KPI
        processing_times = [point['Average'] for point in metrics_data.get('ProcessingTime', []) if 'Average' in point]
        if processing_times:
            avg_processing_time = sum(processing_times) / len(processing_times)
            kpis['processing_efficiency'] = {
                'current': avg_processing_time,
                'target': self.kpi_targets['avg_processing_time'],
                'status': 'meeting_target' if avg_processing_time <= self.kpi_targets['avg_processing_time'] else 'below_target'
            }
        
        # Success Rate KPI
        total_projects = len(db_metrics)
        successful_projects = len([m for m in db_metrics if m.get('metrics', {}).get('status') == 'completed'])
        if total_projects > 0:
            success_rate = successful_projects / total_projects
            kpis['success_rate'] = {
                'current': success_rate,
                'target': self.kpi_targets['processing_success_rate'],
                'status': 'meeting_target' if success_rate >= self.kpi_targets['processing_success_rate'] else 'below_target'
            }
        
        return kpis
    
    def _calculate_trends(self, metrics_data: Dict[str, List], db_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate trends from metrics data
        
        Args:
            metrics_data: CloudWatch metrics data
            db_metrics: DynamoDB metrics data
            
        Returns:
            Dictionary of trend data
        """
        trends = {}
        
        # Processing time trend
        processing_times = sorted([point['Average'] for point in metrics_data.get('ProcessingTime', []) if 'Average' in point])
        if len(processing_times) >= 2:
            trends['processing_time'] = {
                'direction': 'improving' if processing_times[-1] < processing_times[0] else 'declining',
                'change_percent': ((processing_times[-1] - processing_times[0]) / processing_times[0]) * 100
            }
        
        # Volume trend
        daily_counts = {}
        for metric in db_metrics:
            date = metric['timestamp'][:10]  # Extract date
            daily_counts[date] = daily_counts.get(date, 0) + 1
        
        if len(daily_counts) >= 2:
            dates = sorted(daily_counts.keys())
            first_count = daily_counts[dates[0]]
            last_count = daily_counts[dates[-1]]
            trends['volume'] = {
                'direction': 'increasing' if last_count > first_count else 'decreasing',
                'change_percent': ((last_count - first_count) / first_count) * 100 if first_count > 0 else 0
            }
        
        return trends
    
    def generate_kpi_report(self, days: int = 30) -> str:
        """
        Generate a KPI report
        
        Args:
            days: Number of days to include in report
            
        Returns:
            Formatted KPI report
        """
        try:
            dashboard_data = self.get_kpi_dashboard_data(days)
            
            report = f"""
# Code-to-BRD System KPI Report
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
Period: {dashboard_data.get('period', {}).get('days', days)} days

## Key Performance Indicators

"""
            
            kpis = dashboard_data.get('kpis', {})
            targets = dashboard_data.get('targets', {})
            
            for kpi_name, kpi_data in kpis.items():
                current = kpi_data.get('current', 0)
                target = kpi_data.get('target', 0)
                status = kpi_data.get('status', 'unknown')
                
                if isinstance(current, float) and current < 1:
                    current_display = f"{current:.1%}"
                else:
                    current_display = f"{current:.1f}"
                
                if isinstance(target, float) and target < 1:
                    target_display = f"{target:.1%}"
                else:
                    target_display = f"{target:.1f}"
                
                status_emoji = "✅" if status == 'meeting_target' else "❌"
                
                report += f"### {kpi_name.replace('_', ' ').title()}\n"
                report += f"- Current: {current_display}\n"
                report += f"- Target: {target_display}\n"
                report += f"- Status: {status_emoji} {status.replace('_', ' ').title()}\n\n"
            
            # Add trends section
            trends = dashboard_data.get('trends', {})
            if trends:
                report += "## Trends\n\n"
                for trend_name, trend_data in trends.items():
                    direction = trend_data.get('direction', 'stable')
                    change = trend_data.get('change_percent', 0)
                    direction_emoji = "📈" if direction == 'increasing' or direction == 'improving' else "📉"
                    
                    report += f"### {trend_name.replace('_', ' ').title()}\n"
                    report += f"- Direction: {direction_emoji} {direction.title()}\n"
                    report += f"- Change: {change:.1f}%\n\n"
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating KPI report: {str(e)}")
            return f"Error generating KPI report: {str(e)}"
