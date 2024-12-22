def test_delete_user_route(logged_in_admin, test_user, db_session):
    with logged_in_admin.application.app_context():
        # Ensure the user is attached to the session
        user = db_session.query(User).get(test_user.id)
        
        delete_response = logged_in_admin.post(
            url_for('admin.user.delete', id=user.id),
            follow_redirects=True
        )

        assert delete_response.status_code == 200
        # Add assertions to check for the expected behavior after deletion
        # For example, you can check if the user is no longer in the database
        deleted_user = db_session.query(User).get(user.id)
        assert deleted_user is None
