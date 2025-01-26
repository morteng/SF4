import os
from sqlalchemy import create_engine, text, inspect

db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
engine = create_engine(db_uri)

with engine.connect() as connection:
    try:
        result = connection.execute(text("SELECT 1")) # Simple test query
        print("Text function works:", result.scalar())

        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        if table_names:
            first_table = table_names[0] # Just get the first table if any
            pragma_result = connection.execute(text(f"PRAGMA table_info({first_table})")) # Test PRAGMA
            print("PRAGMA query also works (if tables exist):", pragma_result.fetchall())
        else:
            print("No tables found to test PRAGMA.")


    except Exception as e:
        print(f"Error: {e}")

print("Debug script finished.")
