import sys
from pathlib import Path
from flask import Flask, template_rendered
from jinja2 import TemplateNotFound
import logging

def configure_logging():
    """Configure logging for template verification"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/template_verification.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def verify_template_params(template_name, *required_params):
    """Verify that a template has all required parameters"""
    logger = configure_logging()
    
    try:
        # Create a test Flask app
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Track rendered template parameters
        rendered_params = {}
        
        def capture_params(sender, template, context, **extra):
            nonlocal rendered_params
            rendered_params = context
            
        # Connect signal to capture template rendering
        template_rendered.connect(capture_params, app)
        
        # Try to render the template
        with app.test_request_context():
            try:
                app.jinja_env.get_template(template_name)
                logger.info(f"Template {template_name} exists")
            except TemplateNotFound:
                logger.error(f"Template {template_name} not found")
                return False
                
        # Verify required parameters
        missing_params = []
        for param in required_params:
            if param not in rendered_params:
                missing_params.append(param)
                
        if missing_params:
            logger.error(f"Missing required parameters in {template_name}: {', '.join(missing_params)}")
            return False
            
        logger.info(f"Template {template_name} has all required parameters")
        return True
        
    except Exception as e:
        logger.error(f"Error verifying template parameters: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python verify_template_params.py <template_name> <param1> [param2 ...]")
        sys.exit(1)
        
    template_name = sys.argv[1]
    required_params = sys.argv[2:]
    
    if verify_template_params(template_name, *required_params):
        sys.exit(0)
    else:
        sys.exit(1)
