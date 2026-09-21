"""Database connection and initialization for RFAW."""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from ..config import DATABASE_URL, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, SQL_DIR


def get_engine() -> Engine:
    """Create SQLAlchemy engine from DATABASE_URL or individual params."""
    if DATABASE_URL:
        return create_engine(DATABASE_URL)
    url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)


def init_database():
    """Run all SQL schema files in order."""
    engine = get_engine()
    schema_files = sorted(SQL_DIR.glob("*.sql"))
    with engine.connect() as conn:
        for sql_file in schema_files:
            print(f"  Executing {sql_file.name}...")
            sql_text = sql_file.read_text()
            for statement in sql_text.split(";"):
                stmt = statement.strip()
                if stmt:
                    conn.execute(text(stmt))
            conn.commit()
    print("Database initialized successfully.")


def table_exists(table_name: str, schema: str = "mart") -> bool:
    """Check if a table exists in the database."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = :schema AND table_name = :table)"
        ), {"schema": schema, "table": table_name})
        return result.scalar()
