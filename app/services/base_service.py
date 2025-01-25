from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from wtforms import ValidationError
from werkzeug.exceptions import Unauthorized

class Result:
    """Simple result container for service operations"""
    
    def __init__(self, success: bool, message: str = None, data: dict = None):
        self.success = success
        self.message = message
        self.data = data
        
    def __bool__(self):
        return self.success
        
    def __repr__(self):
        return f"Result(success={self.success}, message={self.message})"
from app.extensions import db
from flask import current_app
import logging
from datetime import datetime
from app.constants import FlashMessages, FlashCategory
from flask_limiter.util import get_remote_address

class AuthenticationError(Unauthorized):
    """Custom authentication error class"""
    pass

logger = logging.getLogger(__name__)

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            args[0].operation_metrics['total_operations'] += 1  # self is args[0]
            args[0].operation_metrics['pending_operations'] += 1
            result = func(*args, **kwargs)
            args[0].operation_metrics['success_count'] += 1
            args[0].operation_metrics['pending_operations'] -= 1
            return result
        except ValidationError as e:
            db.session.rollback()
            logger.error(f"Validation error in {func.__name__}: {str(e)}", extra={
                'user_id': kwargs.get('user_id'),
                'data': kwargs.get('data'),
                'errors': e.messages
            })
            raise ValueError(FlashMessages.CRUD_VALIDATION_ERROR.format(errors=e.messages))
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error in {func.__name__}: {str(e)}", extra={
                'user_id': kwargs.get('user_id'),
                'data': kwargs.get('data')
            })
            raise ValueError(FlashMessages.DATABASE_ERROR)
        except ValueError as e:
            db.session.rollback()
            logger.error(f"Value error in {func.__name__}: {str(e)}", extra={
                'user_id': kwargs.get('user_id'),
                'data': kwargs.get('data')
            })
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in {func.__name__}: {str(e)}", extra={
                'user_id': kwargs.get('user_id'),
                'data': kwargs.get('data')
            })
            args[0].operation_metrics['error_count'] += 1
            args[0].operation_metrics['last_error'] = str(e)
            args[0].operation_metrics['pending_operations'] -= 1
            raise ValueError(FlashMessages.CRUD_OPERATION_ERROR.format(error=str(e)))
    return wrapper

    def _init_metrics(self):
        """Initialize metrics tracking structures"""
        self.operation_metrics = {
            'total_operations': 0,
            'success_count': 0,
            'error_count': 0,
            'pending_operations': 0,
            'last_error': None
        }

    @handle_errors
    def get_operation_metrics(self):
        """Get calculated performance metrics"""
        return {
            'success_rate': (self.operation_metrics['success_count'] / 
                           self.operation_metrics['total_operations']) * 100 
                           if self.operation_metrics['total_operations'] > 0 else 0,
            'error_rate': (self.operation_metrics['error_count'] / 
                          self.operation_metrics['total_operations']) * 100 
                          if self.operation_metrics['total_operations'] > 0 else 0,
            'pending_ops': self.operation_metrics['pending_operations'],
            'last_error': self.operation_metrics['last_error']
        }

class BaseService:
    def __init__(self, model, audit_logger=None):
        self.model = model
        self.audit_logger = audit_logger
        self._init_metrics()  # Initialize metrics tracking
        # Initialize rate limits without limiter
        self.rate_limits = {
            'create': "10/minute",
            'update': "10/minute", 
            'delete': "5/minute"
        }
        self._create_limit = self.rate_limits['create']
        self.soft_delete_enabled = hasattr(model, 'is_deleted')
        self.validation_rules = {}
        self.pre_create_hooks = []
        self.post_create_hooks = []
        self.pre_update_hooks = [] 
        self.post_update_hooks = []
        self.pre_delete_hooks = []
        self.post_delete_hooks = []
        self.pre_validation_hooks = []
        self.post_validation_hooks = []
        self.validation_cache = {}
        self.cache_validation = False

    def _get_limiter(self):
        """Get limiter from current app"""
        if not current_app or not hasattr(current_app, 'extensions'):
            return None
        return current_app.extensions.get('limiter')

    def _rate_limit_decorator(self, operation):
        """Create a rate limit decorator if limiter is available"""
        limiter = self._get_limiter()
        if limiter is None:
            # If no limiter, return a no-op decorator
            def noop_decorator(f):
                @wraps(f)
                def wrapper(*args, **kwargs):
                    return f(*args, **kwargs)
                return wrapper
            return noop_decorator
        
        # Create actual rate limit decorator
        return limiter.limit(
            lambda self: self.rate_limits[operation],
            key_func=get_remote_address
        )

    def add_pre_validation_hook(self, hook):
        """Add a hook to run before validation"""
        self.pre_validation_hooks.append(hook)
        
    def add_post_validation_hook(self, hook):
        """Add a hook to run after validation"""
        self.post_validation_hooks.append(hook)

    def add_pre_create_hook(self, hook):
        self.pre_create_hooks.append(hook)
        
    def add_post_create_hook(self, hook):
        self.post_create_hooks.append(hook)
        
    def add_pre_update_hook(self, hook):
        self.pre_update_hooks.append(hook)
        
    def add_post_update_hook(self, hook):
        self.post_update_hooks.append(hook)
        
    def add_pre_delete_hook(self, hook):
        self.pre_delete_hooks.append(hook)
        
    def add_post_delete_hook(self, hook):
        self.post_delete_hooks.append(hook)

    @handle_errors
    def get_by_id(self, id):
        """Get entity by ID or raise 404"""
        entity = self.model.query.get(id)
        if not entity:
            raise ValueError(FlashMessages.NOT_FOUND.format(entity_name=self.model.__name__))
        return entity

    @handle_errors
    def get_all(self):
        """Get all entities with pagination support"""
        return self.model.query

    @property
    def create_limit(self):
        return self.rate_limits['create']

    @create_limit.setter
    @handle_errors
    def create_limit(self, value):
        if not isinstance(value, str):
            raise ValueError("Create limit must be a string (e.g., '10 per minute')")
        if not any(x in value for x in ['per second', 'per minute', 'per hour', 'per day']):
            raise ValueError("Rate limit must include time unit (e.g., 'per minute')")
        self.rate_limits['create'] = value
        
    @handle_errors
    def create(self, data, user_id=None):
        """Create a new entity with validation and audit logging"""
        # Apply rate limiting decorator dynamically
        create_func = self._rate_limit_decorator('create')(self._create)
        return create_func(data, user_id)

    def _create(self, data, user_id=None):
        """Actual create implementation without rate limiting"""
        try:
            # Run pre-create hooks
            for hook in self.pre_create_hooks:
                data = hook(data)
                
            self.validate_create(data)
            entity = self.model(**data)
            db.session.add(entity)
            db.session.commit()
            
            # Run post-create hooks
            for hook in self.post_create_hooks:
                hook(entity)
            
            self._log_audit('create', entity, user_id=user_id, after=entity.to_dict())
            return entity
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise ValueError(f"Failed to create {self.model.__name__}: {str(e)}")

    def validate(self, data):
        """Enhanced validation with date/time handling"""
        errors = {}
        
        # Run pre-validation hooks
        for hook in self.pre_validation_hooks:
            data = hook(data)
        
        # Validate date/time fields
        for field, rules in self.validation_rules.items():
            if rules.get('type') == 'datetime':
                try:
                    value = data.get(field)
                    if value:
                        # Convert to datetime object if string
                        if isinstance(value, str):
                            try:
                                datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                errors[field] = str(FlashMessages.INVALID_DATETIME_FORMAT)
                except Exception as e:
                    errors[field] = str(e)
        
        # Run post-validation hooks
        for hook in self.post_validation_hooks:
            hook(data, errors)
        
        if errors:
            raise ValidationError(FlashMessages.CRUD_VALIDATION_ERROR.format(errors=errors))

    def benchmark_validation(self, iterations=1000):
        """Benchmark validation performance with various test cases"""
        import time
        from datetime import datetime
        
        test_cases = [
            {'valid': True, 'data': {'date_field': '2024-12-31 23:59:59'}},
            {'valid': True, 'data': {'date_field': '2024-02-29 00:00:00'}},  # Leap year
            {'valid': False, 'data': {'date_field': '2023-02-29 00:00:00'}}, # Invalid leap year
            {'valid': False, 'data': {'date_field': '2024-13-01 00:00:00'}}, # Invalid month
            {'valid': False, 'data': {'date_field': '2024-12-32 00:00:00'}}, # Invalid day
            {'valid': False, 'data': {'date_field': '2024-12-31 24:00:00'}}, # Invalid hour
            {'valid': False, 'data': {'date_field': '2024-12-31 23:60:00'}}, # Invalid minute
            {'valid': False, 'data': {'date_field': '2024-12-31 23:59:60'}}, # Invalid second
        ]
        
        results = {}
        
        for case in test_cases:
            data = case['data']
            expected = case['valid']
            
            start = time.perf_counter()
            for _ in range(iterations):
                try:
                    self.validate(data)
                    actual = True
                except ValidationError:
                    actual = False
            elapsed = time.perf_counter() - start
            
            results[str(data)] = {
                'iterations': iterations,
                'time': elapsed,
                'expected': expected,
                'actual': actual,
                'avg_time': elapsed / iterations
            }
        
        return results

    def validate_create(self, data):
        """Validate data before creation"""
        if not data:
            raise ValidationError(FlashMessages.CRUD_VALIDATION_ERROR.format(errors="No data provided"))
            
        # Only validate required fields
        required_fields = self.model.REQUIRED_FIELDS if hasattr(self.model, 'REQUIRED_FIELDS') else []
        errors = {}
        
        for field in required_fields:
            if field not in data or not data[field]:
                errors[field] = f"{field} is required"
                
        if errors:
            raise ValidationError(FlashMessages.CRUD_VALIDATION_ERROR.format(errors=errors))
        
    def validate_update(self, data):
        """Validate data before update"""
        if not data:
            raise ValidationError(FlashMessages.CRUD_VALIDATION_ERROR.format(errors="No data provided"))
        self.validate(data)

    @property
    def update_limit(self):
        return self.rate_limits['update']

    @update_limit.setter
    @handle_errors
    def update_limit(self, value):
        if not isinstance(value, str):
            raise ValueError("Update limit must be a string (e.g., '10 per minute')")
        if not any(x in value for x in ['per second', 'per minute', 'per hour', 'per day']):
            raise ValueError("Rate limit must include time unit (e.g., 'per minute')")
        self.rate_limits['update'] = value
        
    @handle_errors
    def update(self, id, data, user_id=None):
        """Update an existing entity with validation and audit logging"""
        # Apply rate limiting decorator dynamically
        update_func = self._rate_limit_decorator('update')(self._update)
        return update_func(id, data, user_id)

    def _update(self, id, data, user_id=None):
        """Actual update implementation without rate limiting"""
        entity = self.get_by_id(id)
        
        if hasattr(self, '_validate_update_data'):
            self._validate_update_data(data)
            
        before = entity.to_dict()
        for key, value in data.items():
            setattr(entity, key, value)
        db.session.commit()
        
        self._log_audit('update', entity, user_id=user_id, before=before, after=entity.to_dict())
        return entity

    @property
    def delete_limit(self):
        return self.rate_limits['delete']

    @delete_limit.setter
    @handle_errors
    def delete_limit(self, value):
        if not isinstance(value, str):
            raise ValueError("Delete limit must be a string (e.g., '5 per minute')")
        if not any(x in value for x in ['per second', 'per minute', 'per hour', 'per day']):
            raise ValueError("Rate limit must include time unit (e.g., 'per minute')")
        self.rate_limits['delete'] = value
        
    @handle_errors
    def delete(self, id, user_id=None):
        """Enhanced delete with soft delete support"""
        # Apply rate limiting decorator dynamically
        delete_func = self._rate_limit_decorator('delete')(self._delete)
        return delete_func(id, user_id)

    def _delete(self, id, user_id=None):
        """Actual delete implementation without rate limiting"""
        entity = self.get_by_id(id)
        
        if self.soft_delete_enabled:
            return self.soft_delete(id, user_id)
            
        db.session.delete(entity)
        db.session.commit()
        
        self._log_audit('delete', entity, user_id=user_id, before=entity.to_dict())
        return entity

    def get_active(self):
        """Get only active (non-deleted) entities"""
        if self.soft_delete_enabled:
            return self.model.query.filter_by(is_deleted=False)
        return self.model.query
        
    def get_deleted(self):
        """Get only deleted entities"""
        if self.soft_delete_enabled:
            return self.model.query.filter_by(is_deleted=True)
        raise ValueError("Model does not support soft delete")
        
    def bulk_restore(self, ids, user_id=None):
        """Restore multiple soft deleted entities"""
        if not self.soft_delete_enabled:
            raise ValueError("Model does not support soft delete")
            
        entities = self.model.query.filter(self.model.id.in_(ids)).all()
        for entity in entities:
            entity.is_deleted = False
            self._log_audit('restore', entity, user_id=user_id)
        db.session.commit()
        return entities

    def soft_delete(self, id, user_id=None):
        """Soft delete implementation"""
        entity = self.get_by_id(id)
        if hasattr(entity, 'is_deleted'):
            setattr(entity, 'is_deleted', True)
            db.session.commit()
            self._log_audit('soft_delete', entity, user_id=user_id)
            return entity
        raise ValueError("Model does not support soft delete")

    def restore(self, id, user_id=None):
        """Restore soft deleted entity"""
        entity = self.get_by_id(id)
        if hasattr(entity, 'is_deleted'):
            setattr(entity, 'is_deleted', False)
            db.session.commit()
            self._log_audit('restore', entity, user_id=user_id)
            return entity
        raise ValueError("Model does not support restore")

    def _log_audit(self, action, entity, user_id=None, before=None, after=None):
        """Enhanced audit logging with IP and endpoint tracking"""
        from flask import request
        if self.audit_logger:
            self.audit_logger.log(
                action=action,
                object_type=self.model.__name__,
                object_id=entity.id if entity else None,
                user_id=user_id,
                before=before,
                after=after or (entity.to_dict() if entity else None),
                ip_address=request.remote_addr if request else '127.0.0.1',
                endpoint=request.endpoint if request else 'unknown',
                http_method=request.method if request else 'UNKNOWN',
                user_agent=request.headers.get('User-Agent') if request else None,
                error_details=getattr(self, '_last_error', None)
            )

    def handle_authentication_error(self, error):
        """Specialized handler for authentication errors"""
        error_message = str(error) if str(error) else "Authentication failed"
        self._last_error = {
            'type': 'AuthenticationError',
            'message': error_message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log the error
        logger.error(f"Authentication error: {error_message}")
        
        # Add to audit log
        self._log_audit(
            action='auth_error',
            entity=None,
            user_id=getattr(error, 'user_id', None),
            before=None,
            after=None
        )
        
        raise AuthenticationError(error_message)
