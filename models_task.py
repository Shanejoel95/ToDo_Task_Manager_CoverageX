from database import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
import logging

logger = logging.getLogger(__name__)

class Task(db.Model):
    __tablename__ = 'task'  # Use exact table name from requirements
    
    # Define columns with explicit configuration
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, title, description=None, completed=False):
        """Initialize task with proper logging"""
        self.title = title
        self.description = description
        self.completed = completed
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        logger.info(f"Task object created: title='{title}', description='{description}', completed={completed}")
    
    def __repr__(self):
        return f'<Task {self.id}: {self.title}>'
    
    def to_dict(self):
        """Convert task to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def save(self):
        """Save task with error handling and verification"""
        try:
            logger.info(f"Attempting to save task: {self.title}")
            
            # Add to session
            db.session.add(self)
            logger.info("Task added to database session")
            
            # Commit to database
            db.session.commit()
            logger.info(f"Task committed to database with ID: {self.id}")
            
            # Verify the save
            saved_task = Task.query.get(self.id)
            if saved_task:
                logger.info(f"Task save verified: {saved_task}")
                return True
            else:
                logger.error("Task save verification failed")
                return False
                
        except Exception as e:
            logger.error(f"Error saving task: {e}")
            db.session.rollback()
            raise e
    
    def mark_completed(self):
        """Mark task as completed with proper logging"""
        try:
            logger.info(f"Marking task {self.id} as completed")
            
            self.completed = True
            self.updated_at = datetime.utcnow()
            self.completed_at = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"Task {self.id} marked as completed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Error marking task as completed: {e}")
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_incomplete_tasks(limit=5):
        """Get incomplete tasks with logging"""
        try:
            logger.info(f"Fetching {limit} incomplete tasks")
            
            tasks = Task.query.filter_by(completed=False)\
                             .order_by(Task.created_at.desc())\
                             .limit(limit)\
                             .all()
            
            logger.info(f"Found {len(tasks)} incomplete tasks")
            return tasks
            
        except Exception as e:
            logger.error(f"Error fetching incomplete tasks: {e}")
            raise e
    
    @staticmethod
    def create_task(title, description=None):
        """Create and save a new task with comprehensive error handling"""
        try:
            logger.info(f"Creating new task: title='{title}', description='{description}'")
            
            # Validate input
            if not title or not title.strip():
                raise ValueError("Title is required and cannot be empty")
            
            if len(title.strip()) > 255:
                raise ValueError("Title must be 255 characters or less")
            
            # Create new task
            new_task = Task(
                title=title.strip(),
                description=description.strip() if description else None,
                completed=False
            )
            
            # Save task
            if new_task.save():
                logger.info(f"Task created successfully with ID: {new_task.id}")
                return new_task
            else:
                raise Exception("Failed to save task to database")
                
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise e