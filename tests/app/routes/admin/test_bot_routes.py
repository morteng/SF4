import pytest
from bs4 import BeautifulSoup
from app.models.bot import Bot
from app.services.bot_service import run_bot
from sqlalchemy import inspect

@pytest.mark.usefixtures("db")
class TestBotRoutes:

    def test_list_bots(self, logged_in_client):
        # Test listing bots
        response = logged_in_client.get('/admin/bots/')
        assert response.status_code == 200
        soup = BeautifulSoup(response.data.decode(), 'html.parser')
        assert soup.find('h1', string='List of Bots')

    def test_create_bot(self, logged_in_client):
        # Test creating a new bot
        response = logged_in_client.post('/admin/bots/create', data={
            'name': 'Test Bot',
            'description': 'A test bot for coverage'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert Bot.query.filter_by(name='Test Bot').first() is not None

    def test_update_bot(self, logged_in_client, db):
        # Create a bot first
        bot = Bot(name='Old Name', description='Old Description')
        db.session.add(bot)
        db.session.commit()

        # Update the bot
        response = logged_in_client.post(f'/admin/bots/update/{bot.id}', data={
            'name': 'Updated Name',
            'description': 'Updated Description'
        }, follow_redirects=True)
        assert response.status_code == 200
        updated_bot = Bot.query.get(bot.id)
        assert updated_bot.name == 'Updated Name'

    def test_delete_bot(self, logged_in_client, db):
        # Create a bot first
        bot = Bot(name='ToDelete', description='For deletion')
        db.session.add(bot)
        db.session.commit()

        # Delete the bot
        response = logged_in_client.post(f'/admin/bots/delete/{bot.id}', follow_redirects=True)
        assert response.status_code == 200
        assert Bot.query.get(bot.id) is None

    def test_run_bot(self, mocker, logged_in_client, db):
        # Mock the run_bot function
        mock_run_bot = mocker.patch('app.services.bot_service.run_bot')

        # Create a bot first
        bot = Bot(name='Runner', description='To run')
        db.session.add(bot)
        db.session.commit()

        # Run the bot
        response = logged_in_client.post(f'/admin/bots/run/{bot.id}', follow_redirects=True)
        assert response.status_code == 200
        mock_run_bot.assert_called_once_with(bot)

    def test_user_table_exists(self, app, db):
        with app.app_context():
            inspector = inspect(db.engine)
            table_names = inspector.get_table_names()
            assert 'user' in table_names
