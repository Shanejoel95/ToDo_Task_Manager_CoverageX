from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Create database instance with explicit configuration
db = SQLAlchemy(model_class=Base)

def init_database(app):
    """Initialize database with proper configuration"""
    try:
        # Configure database settings
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
            "pool_timeout": 20,
            "max_overflow": 0,
            "echo": True,  # Enable SQL logging for debugging
        }
        
        # Initialize with app
        db.init_app(app)
        logger.info("Database initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def test_database_connection():
    """Test database connection and operations"""
    try:
        from sqlalchemy import text
        
        # Test basic connection
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            test_result = result.fetchone()
            logger.info(f"Database connection test successful: {test_result}")
        
        # Test current database
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT DATABASE() as current_db"))
            current_db = result.fetchone()
            logger.info(f"Connected to database: {current_db}")
        
        return True
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

def create_tables_safely():
    """Create tables with error handling"""
    try:
        # Create all tables
        db.create_all()
        logger.info("All database tables created successfully")
        
        # Verify table creation
        from sqlalchemy import text
        with db.engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"Created tables: {tables}")
        
        return True
        
    except Exception as e:
        logger.error(f"Table creation failed: {e}")
        return False