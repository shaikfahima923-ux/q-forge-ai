
from app.database import test_db_connection

if __name__ == "__main__":
    try:
        database_name = test_db_connection()
        print(f"Database connection successful! Database: {database_name}")
    except Exception as error:
        print("Database connection failed.")
        print(f"Error type: {type(error).__name__}")
        print(error)
