-- Initialize the To-Do database for Docker deployment
-- This matches your existing working database structure

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS task_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE task_db;

-- Drop existing tables if they exist (to ensure clean schema)
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS task;

-- Create the main "task" table matching your models_task.py
CREATE TABLE task (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    
    -- Indexes for better performance
    INDEX idx_completed (completed),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create additional user for the application
CREATE USER IF NOT EXISTS 'todouser'@'%' IDENTIFIED BY 'todopass';
GRANT ALL PRIVILEGES ON task_db.* TO 'todouser'@'%';
GRANT ALL PRIVILEGES ON task_db.* TO 'root'@'%';
FLUSH PRIVILEGES;

-- Insert sample data matching the assessment mockup
INSERT INTO task (title, description, completed) VALUES
('Buy books', 'Buy books for the next school year', FALSE),
('Clean home', 'Need to clean the bed room', FALSE),
('Takehome assignment', 'Finish the mid-term assignment', FALSE),
('Play Cricket', 'Plan the soft ball cricket match on next Sunday', FALSE),
('Help Saman', 'Saman need help with his software project', FALSE);

-- Verify table structure
DESCRIBE task;
SELECT COUNT(*) as total_tasks FROM task;