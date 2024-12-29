import pytest
from app.models.tag import Tag
from app.services.tag_service import tag_service
from sqlalchemy.exc import SQLAlchemyError
from wtforms.validators import ValidationError
from app.extensions import db
from flask import Flask
import logging
from unittest.mock import patch

    def test_create_tag_with_empty_name(self, db_session):
        invalid_tag_data = {
            'name': '',
            'category': 'TestCategory'
        }
        with pytest.raises(ValidationError) as excinfo:
            self.service.create(invalid_tag_data)
        assert "Name cannot be empty." in str(excinfo.value)

    def test_create_tag_with_empty_category(self, db_session):
        invalid_tag_data = {
            'name': 'Test Tag',
            'category': ''
        }
        with pytest.raises(ValidationError) as excinfo:
            self.service.create(invalid_tag_data)
        assert "Category cannot be empty." in str(excinfo.value)

    def test_update_tag_with_empty_name(self, db_session, test_entity):
        updated_data = {
            'name': '',
            'category': 'UpdatedCategory'
        }
        with pytest.raises(ValidationError) as excinfo:
            self.service.update(test_entity, updated_data)
        assert "Name cannot be empty." in str(excinfo.value)

    def test_update_tag_with_empty_category(self, db_session, test_entity):
        updated_data = {
            'name': 'Updated Tag Name',
            'category': ''
        }
        with pytest.raises(ValidationError) as excinfo:
            self.service.update(test_entity, updated_data)
        assert "Category cannot be empty." in str(excinfo.value)
