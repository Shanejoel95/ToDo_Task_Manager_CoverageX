import os
import logging
import time
from flask import Flask, render_template, jsonify
from flask_cors import CORS

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the Flask app FIRST
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Enable CORS for frontend-backend communication
CORS(app)

# Database configuration - Docker environment aware
DATABASE_CONFIG = {
    'host': os.environ.get('DATABASE_HOST', 'localhost'),
    'port': int(os.environ.get('DATABASE_PORT', 3306)),
    'user': os.environ.get('DATABASE_USER', 'root'),
    'password': os.environ.get('DATABASE_PASSWORD', '507507'),
    'database': os.environ.get('DATABASE_NAME', 'task_db'),
    'charset': 'utf8mb4'
}

# Build MySQL connection string
DATABASE_URL = f"mysql+mysqlconnector://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}?charset={DATABASE_CONFIG['charset']}"

logger.info(f"Database URL: {DATABASE_URL}")

# Configure Flask app for database
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Health check route (must work without database)
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Backend is running',
        'database_host': DATABASE_CONFIG['host']
    })

@app.route('/')
def index():
    """Serve the main HTML page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving index page: {e}")
        return f"To-Do App Backend is Running! (Templates not found: {e})", 200

def wait_for_database_with_context(max_retries=60, delay=3):
    """Wait for database to be ready in Docker environment with proper context"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Database connection attempt {attempt + 1}/{max_retries}")
            
            # Import database modules
            from database import db, test_database_connection
            
            # Use application context for database operations
            with app.app_context():
                if test_database_connection():
                    logger.info("Database connection successful")
                    return True
                    
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
            
        if attempt < max_retries - 1:
            logger.info(f"Waiting {delay} seconds before next attempt...")
            time.sleep(delay)
    
    logger.error("Failed to connect to database after all retries")
    return False

def setup_database():
    """Setup database with comprehensive error handling and proper context"""
    try:
        logger.info("Setting up database...")
        
        # Import database modules
        from database import db, init_database, create_tables_safely
        
        # Initialize database with app context
        with app.app_context():
            # Initialize database
            if not init_database(app):
                logger.error("Failed to initialize database")
                return False
            
            # Test database connection
            if not wait_for_database_with_context():
                logger.error("Database connection test failed")
                return False
            
            # Create tables
            if not create_tables_safely():
                logger.error("Table creation failed")
                return False
            
            # Import models
            from models_task import Task
            logger.info("Models imported successfully")
            
            # Test basic database operations
            try:
                logger.info("Testing basic database operations...")
                
                # Test creating a task
                test_task = Task(
                    title="Database Setup Test",
                    description="Testing database functionality"
                )
                
                # Save the task
                db.session.add(test_task)
                db.session.commit()
                logger.info(f"Test task created with ID: {test_task.id}")
                
                # Test querying the task
                retrieved_task = Task.query.get(test_task.id)
                if retrieved_task:
                    logger.info(f"Test task retrieved: {retrieved_task.title}")
                else:
                    raise Exception("Failed to retrieve test task")
                
                # Clean up the test task
                db.session.delete(retrieved_task)
                db.session.commit()
                logger.info("Test task cleaned up successfully")
                
            except Exception as e:
                logger.error(f"Database operation test failed: {e}")
                try:
                    db.session.rollback()
                except:
                    pass
                return False
            
            logger.info("Database setup completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False

def register_app_routes():
    """Register API routes with error handling"""
    try:
        from routes import register_routes
        register_routes(app)
        logger.info("API routes registered successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to register routes: {e}")
        return False

def main():
    """Main application startup"""
    logger.info("Starting To-Do Application...")
    
    # Setup database (only if we're in Docker environment)
    if os.environ.get('DATABASE_HOST'):  # Running in Docker
        logger.info("Docker environment detected, waiting for database...")
        if not setup_database():
            logger.error("Database setup failed. Starting without database...")
            # Don't exit - start the app anyway for health checks
    else:
        logger.info("Local environment detected")
        # For local development, try to setup database but don't fail if it doesn't work
        try:
            setup_database()
        except Exception as e:
            logger.warning(f"Local database setup failed: {e}")
    
    # Register routes
    if not register_app_routes():
        logger.warning("Route registration failed. Starting with basic routes only...")
    
    logger.info("Application startup completed")
    return True

if __name__ == "__main__":
    # Initialize the app
    main()
    
    logger.info("Starting Flask development server...")
    try:
        # For Docker, bind to all interfaces
        port = int(os.environ.get('PORT', 5000))
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start Flask server: {e}")
        exit(1)