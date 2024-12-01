def test_database_connection(db):
    result = db.engine.execute("SELECT 1")
    assert result.scalar() == 1
