from flask import request, jsonify, current_app
from database import db
from models_task import Task
import logging
import traceback

logger = logging.getLogger(__name__)

def register_routes(app):
    """Register all routes with the Flask app"""
    
    @app.route('/api/tasks', methods=['GET'])
    def get_tasks():
        """Get the most recent 5 incomplete tasks with detailed logging"""
        try:
            logger.info("GET /api/tasks - Fetching incomplete tasks")
            
            # Use the model method for getting tasks
            tasks = Task.get_incomplete_tasks(limit=5)
            
            # Convert to dictionaries for JSON response
            task_list = [task.to_dict() for task in tasks]
            
            response_data = {
                'success': True,
                'tasks': task_list,
                'count': len(task_list)
            }
            
            logger.info(f"Successfully fetched {len(task_list)} tasks")
            return jsonify(response_data), 200
            
        except Exception as e:
            logger.error(f"Error in get_tasks: {str(e)}")
            logger.error(traceback.format_exc())
            
            return jsonify({
                'success': False,
                'error': f'Failed to fetch tasks: {str(e)}'
            }), 500

    @app.route('/api/tasks', methods=['POST'])
    def create_task():
        """Create a new task with comprehensive error handling"""
        try:
            logger.info("POST /api/tasks - Creating new task")
            
            # Get JSON data
            data = request.get_json()
            logger.info(f"Received data: {data}")
            
            if not data:
                logger.warning("No data provided in request")
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # Extract and validate data
            title = data.get('title', '').strip()
            description = data.get('description', '').strip()
            
            logger.info(f"Parsed data - Title: '{title}', Description: '{description}'")
            
            # Validate title
            if not title:
                logger.warning("Title is empty or missing")
                return jsonify({
                    'success': False,
                    'error': 'Title is required'
                }), 400
            
            if len(title) > 255:
                logger.warning(f"Title too long: {len(title)} characters")
                return jsonify({
                    'success': False,
                    'error': 'Title must be 255 characters or less'
                }), 400
            
            # Create task using model method
            new_task = Task.create_task(title, description)
            
            # Prepare response
            response_data = {
                'success': True,
                'task': new_task.to_dict(),
                'message': 'Task created successfully'
            }
            
            logger.info(f"Task created successfully with ID: {new_task.id}")
            return jsonify(response_data), 201
            
        except ValueError as ve:
            logger.error(f"Validation error in create_task: {str(ve)}")
            return jsonify({
                'success': False,
                'error': str(ve)
            }), 400
            
        except Exception as e:
            logger.error(f"Error in create_task: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Ensure rollback on error
            try:
                db.session.rollback()
            except:
                pass
            
            return jsonify({
                'success': False,
                'error': f'Failed to create task: {str(e)}'
            }), 500

    @app.route('/api/tasks/<int:task_id>/complete', methods=['PUT'])
    def complete_task(task_id):
        """Mark a task as completed with detailed logging"""
        try:
            logger.info(f"PUT /api/tasks/{task_id}/complete - Completing task")
            
            # Find the task
            task = Task.query.get(task_id)
            
            if not task:
                logger.warning(f"Task not found: {task_id}")
                return jsonify({
                    'success': False,
                    'error': 'Task not found'
                }), 404
            
            if task.completed:
                logger.warning(f"Task {task_id} is already completed")
                return jsonify({
                    'success': False,
                    'error': 'Task is already completed'
                }), 400
            
            # Mark as completed using model method
            task.mark_completed()
            
            response_data = {
                'success': True,
                'task': task.to_dict(),
                'message': 'Task marked as completed'
            }
            
            logger.info(f"Task {task_id} completed successfully")
            return jsonify(response_data), 200
            
        except Exception as e:
            logger.error(f"Error in complete_task: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Ensure rollback on error
            try:
                db.session.rollback()
            except:
                pass
            
            return jsonify({
                'success': False,
                'error': f'Failed to complete task: {str(e)}'
            }), 500

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint with database verification"""
        try:
            # Test database connection
            task_count = Task.query.count()
            
            return jsonify({
                'success': True,
                'message': 'API is healthy',
                'database_status': 'connected',
                'total_tasks': task_count
            }), 200
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'API health check failed',
                'database_status': 'error',
                'error': str(e)
            }), 500

    @app.route('/debug/tasks', methods=['GET'])
    def debug_tasks():
        """Debug endpoint to check all tasks in database"""
        try:
            all_tasks = Task.query.all()
            
            return jsonify({
                'success': True,
                'total_tasks': len(all_tasks),
                'tasks': [task.to_dict() for task in all_tasks],
                'incomplete_tasks': len([t for t in all_tasks if not t.completed]),
                'completed_tasks': len([t for t in all_tasks if t.completed])
            }), 200
            
        except Exception as e:
            logger.error(f"Debug endpoint error: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/debug/test-insert', methods=['POST'])
    def debug_test_insert():
        """Debug endpoint to test direct database insertion"""
        try:
            import uuid
            test_title = f"Test Task {uuid.uuid4().hex[:8]}"
            
            logger.info(f"Creating test task: {test_title}")
            
            # Create test task
            test_task = Task.create_task(test_title, "This is a test task for debugging")
            
            # Verify it was saved
            saved_task = Task.query.get(test_task.id)
            
            return jsonify({
                'success': True,
                'message': 'Test task created successfully',
                'task': test_task.to_dict(),
                'verified': saved_task is not None
            }), 201
            
        except Exception as e:
            logger.error(f"Test insert failed: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/debug/clear-tasks', methods=['DELETE'])
    def debug_clear_tasks():
        """Debug endpoint to clear all tasks"""
        try:
            logger.info("Clearing all tasks from database")
            
            # Delete all tasks
            deleted_count = Task.query.delete()
            db.session.commit()
            
            logger.info(f"Deleted {deleted_count} tasks")
            
            return jsonify({
                'success': True,
                'message': f'Cleared {deleted_count} tasks from database',
                'deleted_count': deleted_count
            }), 200
            
        except Exception as e:
            logger.error(f"Clear tasks failed: {str(e)}")
            logger.error(traceback.format_exc())
            
            try:
                db.session.rollback()
            except:
                pass
            
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/debug/database-info', methods=['GET'])
    def debug_database_info():
        """Debug endpoint to get database information"""
        try:
            from sqlalchemy import text
            
            # Get database info
            with db.engine.connect() as connection:
                # Current database
                current_db_result = connection.execute(text("SELECT DATABASE() as current_db"))
                current_db = current_db_result.fetchone()
                
                # Tables
                tables_result = connection.execute(text("SHOW TABLES"))
                tables = [row[0] for row in tables_result.fetchall()]
                
                # Task table info
                table_info = None
                if 'task' in tables:
                    table_info_result = connection.execute(text("DESCRIBE task"))
                    table_info = [dict(row._mapping) for row in table_info_result.fetchall()]
            
            return jsonify({
                'success': True,
                'database': current_db[0] if current_db else None,
                'tables': tables,
                'task_table_structure': table_info,
                'connection_string': app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
            }), 200
            
        except Exception as e:
            logger.error(f"Database info failed: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    logger.info("All routes registered successfully")
    
    # Log all registered routes for debugging
    routes_info = []
    for rule in app.url_map.iter_rules():
        routes_info.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule.rule)
        })
    
    logger.info(f"Registered routes: {routes_info}")