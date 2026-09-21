"""Initialize the RFAW PostgreSQL database with all schemas and tables."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from rfaw.warehouse.db import init_database

if __name__ == "__main__":
    print("Initializing RFAW database...")
    init_database()
