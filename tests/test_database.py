def test_database_connection(db):
    with db.engine.connect() as connection:
        result = connection.execute("SELECT 1")
        assert result.scalar() == 1
