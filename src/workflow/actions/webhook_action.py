import logging
import json
from typing import Dict, Any
from . import BaseAction, StepResult

logger = logging.getLogger(__name__)


class WebhookAction(BaseAction):
    """
    Action to send HTTP requests to external APIs.
    
    Inputs (Config):
        url (str): Target URL for the webhook
        method (str): HTTP method - 'POST' | 'GET' | 'PUT' | 'DELETE' (default: POST)
        headers (dict): Optional HTTP headers
        body_type (str): 'json' | 'form' | 'text' (default: json)
        body (dict|str): Request body content
        timeout (float): Request timeout in seconds (default: 30.0)
        
    Outputs (StepResult.data):
        status_code (int): HTTP response status code
        response (dict|str): Response body
        success (bool): Whether request was successful (2xx)
        
    Effect:
        Sends HTTP request to specified URL.
    """
    
    @property
    def action_type(self) -> str:
        return "webhook"
    
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """Execute webhook request"""
        import requests
        
        url = config.get('url')
        if not url:
            return StepResult(self.action_type, False, error="URL is required")
        
        method = config.get('method', 'POST').upper()
        headers = config.get('headers', {})
        body_type = config.get('body_type', 'json')
        body = config.get('body', {})
        timeout = float(config.get('timeout', 30.0))
        
        # Resolve body references from context
        body = self._resolve_body(body, context)
        
        try:
            logger.info(f"Webhook {method} to {url}")
            
            # Prepare request kwargs
            kwargs = {
                'headers': headers,
                'timeout': timeout
            }
            
            # Add body based on type
            if method in ['POST', 'PUT', 'PATCH']:
                if body_type == 'json':
                    kwargs['json'] = body
                elif body_type == 'form':
                    kwargs['data'] = body
                elif body_type == 'text':
                    kwargs['data'] = body if isinstance(body, str) else json.dumps(body)
                    if 'Content-Type' not in headers:
                        kwargs['headers']['Content-Type'] = 'text/plain'
            
            # Make request
            response = requests.request(method, url, **kwargs)
            
            # Parse response
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            output_data = {
                'status_code': response.status_code,
                'response': response_data,
                'success': 200 <= response.status_code < 300
            }
            
            if output_data['success']:
                logger.info(f"Webhook successful: {response.status_code}")
                return StepResult(self.action_type, True, data=output_data)
            else:
                logger.warning(f"Webhook returned {response.status_code}: {response_data}")
                return StepResult(self.action_type, True, data=output_data)  # Still success, but check data
                
        except requests.exceptions.Timeout:
            logger.error(f"Webhook timeout after {timeout}s")
            return StepResult(self.action_type, False, error=f"Request timed out after {timeout}s")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Webhook connection error: {e}")
            return StepResult(self.action_type, False, error=f"Connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Webhook failed: {e}")
            return StepResult(self.action_type, False, error=str(e))
    
    def _resolve_body(self, body: Any, context: Dict[str, Any]) -> Any:
        """Resolve context references in request body"""
        if isinstance(body, str):
            # Check if it's a reference
            if '.' in body and not body.startswith(('http://', 'https://')):
                # Check if the full reference exists in context (e.g., "step_10c.content")
                if body in context:
                    logger.debug(f"Resolved body reference: {body} -> {context[body][:100] if isinstance(context[body], str) else context[body]}...")
                    return context[body]
                
                # Check for input reference
                parts = body.split('.', 1)
                if parts[0] == 'inputs':
                    return context.get('inputs', {}).get(parts[1], body)
                
                # If not found, log warning and return original
                logger.warning(f"Could not resolve body reference: {body}")
            return body
        elif isinstance(body, dict):
            return {k: self._resolve_body(v, context) for k, v in body.items()}
        elif isinstance(body, list):
            return [self._resolve_body(item, context) for item in body]
        return body
