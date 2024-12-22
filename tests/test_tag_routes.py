import pytest
from flask import url_for
from app.models.tag import Tag
from app.utils import flash_message

@pytest.fixture
def tag(client, db_session):
    tag = Tag(name="TestTag")
    db_session.add(tag)
    db_session.commit()
    return tag

def test_create_tag_success(client, admin_user, mock_flash_message):
    client.post(url_for('tag.create'), data={'name': 'NewTag'}, follow_redirects=True)
    assert mock_flash_message.call_args[0][0] == "Tag created successfully"
    assert mock_flash_message.call_args[0][1] == "success"

def test_create_tag_failure(client, admin_user, mock_flash_message):
    client.post(url_for('tag.create'), data={'name': ''}, follow_redirects=True)
    assert mock_flash_message.call_args[0][0] == "Name: This field is required."
    assert mock_flash_message.call_args[0][1] == "error"

def test_delete_tag_success(client, admin_user, tag, mock_flash_message):
    client.post(url_for('tag.delete', id=tag.id), follow_redirects=True)
    assert mock_flash_message.call_args[0][0] == "Tag deleted successfully"
    assert mock_flash_message.call_args[0][1] == "success"

def test_delete_tag_failure(client, admin_user, mock_flash_message):
    client.post(url_for('tag.delete', id=999), follow_redirects=True)
    assert mock_flash_message.call_args[0][0] == "Tag not found"
    assert mock_flash_message.call_args[0][1] == "error"

def test_edit_tag_success(client, admin_user, tag, mock_flash_message):
    client.post(url_for('tag.edit', id=tag.id), data={'name': 'UpdatedTag'}, follow_redirects=True)
    assert mock_flash_message.call_args[0][0] == "Tag updated successfully"
    assert mock_flash_message.call_args[0][1] == "success"

def test_edit_tag_failure(client, admin_user, tag, mock_flash_message):
    client.post(url_for('tag.edit', id=tag.id), data={'name': ''}, follow_redirects=True)
    assert mock_flash_message.call_args[0][0] == "Name: This field is required."
    assert mock_flash_message.call_args[0][1] == "error"

@pytest.fixture
def mock_flash_message(mocker):
    return mocker.patch('app.utils.flash_message')
