import sys
import os
from sqlalchemy import inspect

# Add the backend/app directory to the python path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import engine

def check_schema():
    inspector = inspect(engine)
    columns = inspector.get_columns('users')
    print("Columns in 'users' table:")
    for column in columns:
        print(f"  {column['name']}: {column['type']} (Nullable: {column['nullable']}, Default: {column['default']})")
    
    indexes = inspector.get_indexes('users')
    print("\nIndexes in 'users' table:")
    for index in indexes:
        print(f"  {index['name']}: {index['column_names']} (Unique: {index['unique']})")

if __name__ == "__main__":
    check_schema()
