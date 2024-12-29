import pytest
from app.extensions import db

class BaseCRUDTest:
    @pytest.fixture(autouse=True)
    def setup(self, app, client):
        self.app = app
        self.client = client
        self.setup_test_data()

    def setup_test_data(self):
        """Setup test data for each test case"""
        raise NotImplementedError

    def test_create_success(self):
        """Test successful creation"""
        response = self.client.post(self.create_url, data=self.valid_data)
        assert response.status_code == 302
        assert self.model.query.filter_by(**self.valid_data).first() is not None

    def test_create_validation_error(self):
        """Test creation with invalid data"""
        response = self.client.post(self.create_url, data=self.invalid_data)
        assert response.status_code == 400
        assert b"ValidationError" in response.data

    def test_delete_success(self):
        """Test successful deletion"""
        instance = self.model(**self.valid_data)
        db.session.add(instance)
        db.session.commit()
        
        response = self.client.post(f"{self.delete_url}/{instance.id}")
        assert response.status_code == 302
        assert self.model.query.get(instance.id) is None

    def test_delete_not_found(self):
        """Test deletion of non-existent entity"""
        response = self.client.post(f"{self.delete_url}/999")
        assert response.status_code == 404

    def test_create_audit_log(self):
        """Test audit logging on create"""
        response = self.client.post(self.create_url, data=self.valid_data)
        assert response.status_code == 302
        entity = self.model.query.filter_by(**self.valid_data).first()
        assert entity is not None
        
        # Verify audit log was created
        log = AuditLog.query.filter_by(object_type=self.model.__name__, object_id=entity.id).first()
        assert log is not None
        assert log.action == 'create'

    def test_update_audit_log(self):
        """Test audit logging on update"""
        instance = self.model(**self.valid_data)
        db.session.add(instance)
        db.session.commit()
        
        response = self.client.post(f"{self.edit_url}/{instance.id}", data=self.update_data)
        assert response.status_code == 302
        
        # Verify audit log was created
        log = AuditLog.query.filter_by(object_type=self.model.__name__, object_id=instance.id, action='update').first()
        assert log is not None
