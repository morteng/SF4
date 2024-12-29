from tests.base_test_case import BaseTestCase
from app.services.base_service import BaseService
from app.models.tag import Tag
from wtforms.validators import ValidationError
from app.extensions import db

class TestBaseService(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.service = BaseService(Tag)

    def test_create(self):
        data = {'name': 'New Tag', 'category': 'Test'}
        tag = self.service.create(data)
        self.assertIsNotNone(tag.id)
        self.assertEqual(tag.name, 'New Tag')

    def test_create_invalid_data(self):
        with self.assertRaises(ValidationError):
            self.service.create({})

    def test_update(self):
        tag = Tag(name='Test Tag', category='Test')
        db.session.add(tag)
        db.session.commit()
        
        updated = self.service.update(tag, {'name': 'Updated Tag'})
        self.assertEqual(updated.name, 'Updated Tag')

    def test_update_invalid_data(self):
        tag = Tag(name='Test Tag', category='Test')
        db.session.add(tag)
        db.session.commit()
        
        with self.assertRaises(ValidationError):
            self.service.update(tag, {'invalid_field': 'value'})

    def test_delete(self):
        tag = Tag(name='Test Tag', category='Test')
        db.session.add(tag)
        db.session.commit()
        
        self.service.delete(tag)
        self.assertIsNone(Tag.query.get(tag.id))

    def test_get_by_id(self):
        tag = Tag(name='Test Tag', category='Test')
        db.session.add(tag)
        db.session.commit()
        
        result = self.service.get_by_id(tag.id)
        self.assertEqual(result.id, tag.id)

    def test_get_all(self):
        tags = [
            Tag(name='Tag 1', category='Test'),
            Tag(name='Tag 2', category='Test')
        ]
        db.session.add_all(tags)
        db.session.commit()
        
        results = self.service.get_all().all()
        self.assertEqual(len(results), 2)
