"""
Script to create all database tables in Railway PostgreSQL
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Load environment variables
load_dotenv()

def create_tables():
    """Create all required tables"""
    database_url = os.getenv("DATABASE_URL")

    print("=" * 60)
    print("CREATING DATABASE TABLES")
    print("=" * 60)
    print()

    engine = create_engine(database_url)

    # SQL script to create all tables
    sql_script = """
    -- Tabla de Centros
    CREATE TABLE IF NOT EXISTS centers (
        id SERIAL PRIMARY KEY,
        center_code VARCHAR(50) UNIQUE NOT NULL,
        center_name VARCHAR(200) NOT NULL,
        city VARCHAR(100),
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );

    -- Tabla de Métricas Diarias
    CREATE TABLE IF NOT EXISTS daily_metrics (
        id SERIAL PRIMARY KEY,
        center_id INTEGER REFERENCES centers(id) ON DELETE CASCADE,
        date DATE NOT NULL,
        total_orders INTEGER DEFAULT 0,
        total_results INTEGER DEFAULT 0,
        total_pets INTEGER DEFAULT 0,
        total_owners INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(center_id, date)
    );

    -- Tabla de Resumen de Pruebas
    CREATE TABLE IF NOT EXISTS test_summary (
        id SERIAL PRIMARY KEY,
        center_id INTEGER REFERENCES centers(id) ON DELETE CASCADE,
        date DATE NOT NULL,
        test_code VARCHAR(50) NOT NULL,
        test_name VARCHAR(200),
        count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(center_id, date, test_code)
    );

    -- Tabla de Resumen de Especies
    CREATE TABLE IF NOT EXISTS species_summary (
        id SERIAL PRIMARY KEY,
        center_id INTEGER REFERENCES centers(id) ON DELETE CASCADE,
        date DATE NOT NULL,
        species_name VARCHAR(100) NOT NULL,
        count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(center_id, date, species_name)
    );

    -- Tabla de Resumen de Razas
    CREATE TABLE IF NOT EXISTS breed_summary (
        id SERIAL PRIMARY KEY,
        center_id INTEGER REFERENCES centers(id) ON DELETE CASCADE,
        date DATE NOT NULL,
        breed VARCHAR(100) NOT NULL,
        species VARCHAR(100),
        count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(center_id, date, breed, species)
    );

    -- Crear índices para mejor rendimiento
    CREATE INDEX IF NOT EXISTS idx_daily_metrics_center_date ON daily_metrics(center_id, date);
    CREATE INDEX IF NOT EXISTS idx_test_summary_center_date ON test_summary(center_id, date);
    CREATE INDEX IF NOT EXISTS idx_species_summary_center_date ON species_summary(center_id, date);
    CREATE INDEX IF NOT EXISTS idx_breed_summary_center_date ON breed_summary(center_id, date);
    """

    try:
        with engine.connect() as conn:
            # Execute each statement
            for statement in sql_script.split(';'):
                statement = statement.strip()
                if statement:
                    print(f"Executing: {statement[:80]}...")
                    conn.execute(text(statement))
                    conn.commit()

            print()
            print("✅ All tables created successfully!")
            print()

            # Verify tables
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('centers', 'daily_metrics', 'test_summary', 'species_summary', 'breed_summary')
                ORDER BY table_name;
            """))

            tables = [row[0] for row in result]

            print("Tables created:")
            for table in tables:
                print(f"  ✓ {table}")

            print()
            print("=" * 60)
            print("SETUP COMPLETED SUCCESSFULLY")
            print("=" * 60)

            return True

    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)
