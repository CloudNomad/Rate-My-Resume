from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from models import Base
from database import engine
from sqlalchemy import text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/ratemyresume")

def init_db():
    # Create database engine
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create additional indexes
    with engine.connect() as conn:
        # Create GIN index for array columns in resume_versions
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_resume_versions_skills 
            ON resume_versions USING GIN (skills);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_resume_versions_languages 
            ON resume_versions USING GIN (languages);
        """))
        
        # Create full text search index for resume content
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_resume_versions_content_fts 
            ON resume_versions USING GIN (to_tsvector('english', content));
        """))
        
        conn.commit()

if __name__ == "__main__":
    print("Creating database tables and indexes...")
    init_db()
    print("Database initialization complete!") 