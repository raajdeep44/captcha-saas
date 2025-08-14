# create_tables.py
from app.config import engine
from app.models import Base

if __name__ == "__main__":
    try:
        # This creates all tables that don't exist yet
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
