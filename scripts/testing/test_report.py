import json
import logging
from pathlib import Path
from datetime import datetime

def generate_test_report():
    """Generate comprehensive test report"""
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'test_suites': [],
        'coverage': {},
        'environment': {},
        'summary': {}
    }
    
    # Collect test results
    for result_file in Path('test_results').glob('*.json'):
        with open(result_file) as f:
            report['test_suites'].append(json.load(f))
    
    # Collect coverage data
    coverage_file = Path('.coverage')
    if coverage_file.exists():
        with open(coverage_file) as f:
            report['coverage'] = json.load(f)
    
    # Generate summary
    report['summary'] = {
        'total_tests': sum(s['total'] for s in report['test_suites']),
        'passed_tests': sum(s['passed'] for s in report['test_suites']),
        'failed_tests': sum(s['failed'] for s in report['test_suites']),
        'coverage_percentage': report['coverage'].get('percent_covered', 0)
    }
    
    # Save final report
    report_file = Path('reports/test_report.json')
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if generate_test_report():
        print("Test report generated successfully")
        exit(0)
    else:
        print("Test report generation failed")
        exit(1)
