from flask_testing import TestCase
from app import create_app, db
from app.models import User, Stipend, Tag, Organization
from app.constants import FlashMessages
from datetime import datetime, timedelta
from wtforms.validators import ValidationError

class BaseTestCase(TestCase):
    def create_app(self):
        app = create_app('testing')
        return app

    def setUp(self):
        db.create_all()
        self.create_test_data()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_test_data(self):
        # Create test admin user
        admin = User(
            username='admin',
            email='admin@test.com',
            is_admin=True
        )
        admin.set_password('password')
        db.session.add(admin)

        # Create test organization
        org = Organization(name='Test Org', description='Test Description')
        db.session.add(org)

        # Create test tags
        tags = [
            Tag(name='Research'),
            Tag(name='Internship'),
            Tag(name='Scholarship')
        ]
        db.session.add_all(tags)

        # Create test stipends
        stipends = [
            Stipend(
                name='Test Stipend 1',
                summary='Test Summary 1',
                description='Test Description 1',
                application_deadline=datetime.utcnow() + timedelta(days=30),
                organization=org,
                tags=[tags[0]]
            ),
            Stipend(
                name='Test Stipend 2',
                summary='Test Summary 2',
                description='Test Description 2',
                application_deadline=datetime.utcnow() + timedelta(days=60),
                organization=org,
                tags=[tags[1]]
            )
        ]
        db.session.add_all(stipends)
        db.session.commit()

    def login(self, username='admin', password='password'):
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def assertModelEqual(self, model, data, exclude=[]):
        """Helper to compare model attributes with dictionary data"""
        for key, value in data.items():
            if key not in exclude:
                model_value = getattr(model, key)
                if isinstance(model_value, datetime):
                    model_value = model_value.isoformat()
                self.assertEqual(model_value, value)

    def assertServiceCreates(self, service, valid_data, invalid_data=None):
        """Test service create operation"""
        # Test valid creation
        entity = service.create(valid_data)
        self.assertIsNotNone(entity.id)
        self.assertModelEqual(entity, valid_data)
        
        # Test invalid data
        if invalid_data:
            with self.assertRaises(ValidationError):
                service.create(invalid_data)

    def assertServiceUpdates(self, service, entity, valid_data, invalid_data=None):
        """Test service update operation"""
        # Test valid update
        updated = service.update(entity, valid_data)
        self.assertModelEqual(updated, valid_data)
        
        # Test invalid data
        if invalid_data:
            with self.assertRaises(ValidationError):
                service.update(entity, invalid_data)

    def assertServiceDeletes(self, service, entity):
        """Test service delete operation"""
        service.delete(entity)
        self.assertIsNone(self.model.query.get(entity.id))

    def assertFormValid(self, form, data):
        """Helper to test form validation with valid data"""
        form.process(data=data)
        self.assertTrue(form.validate(), 
                       f"Form should be valid but got errors: {form.errors}")

    def assertFormInvalid(self, form, data, expected_errors):
        """Helper to test form validation with invalid data"""
        form.process(data=data)
        self.assertFalse(form.validate(), 
                        "Form should be invalid but validated successfully")
        for field, errors in expected_errors.items():
            self.assertIn(field, form.errors, 
                         f"Expected errors for field {field} not found")
            for error in errors:
                self.assertIn(error, form.errors[field], 
                             f"Expected error '{error}' not found in {field} errors")

    def assertServiceOperation(self, service, operation, valid_data, invalid_data=None):
        """Generic helper to test service operations"""
        # Test valid operation
        result = getattr(service, operation)(valid_data)
        self.assertIsNotNone(result)
        
        # Test invalid data
        if invalid_data:
            with self.assertRaises(ValidationError):
                getattr(service, operation)(invalid_data)