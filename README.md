# To-Do Task Manager - Senior Full Stack Engineer Assessment

A complete full-stack web application for managing to-do tasks, built according to the Senior Full Stack Engineer Take Home Assessment requirements. This application demonstrates modern software architecture with containerized microservices, comprehensive testing, and production-ready deployment.

## 🏗️ Architecture Overview

The application follows a 3-container microservices architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Nginx)       │◄──►│   (Flask API)   │◄──►│   (MySQL)       │
│   Port 80       │    │   Port 5000     │    │   Port 3306     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Components:
- **Frontend**: Nginx reverse proxy serving a Single Page Application (SPA)
- **Backend**: Flask REST API with SQLAlchemy ORM
- **Database**: MySQL 8.0 with the "task" table as specified

## ✅ Assessment Requirements Fulfilled

### User Requirements:
- ✅ Create to-do tasks with title and description through web UI
- ✅ Display only the 5 most recent incomplete tasks
- ✅ Mark tasks as completed via "Done" button
- ✅ Completed tasks disappear from UI
- ✅ UI matches the provided mockup exactly

### Technical Requirements:
- ✅ 3 separate Docker containers
- ✅ MySQL database with "task" table
- ✅ Flask REST API backend
- ✅ HTML/CSS/JavaScript SPA frontend
- ✅ Docker Compose orchestration
- ✅ Unit tests and integration tests with coverage reporting
- ✅ Clean code principles and SOLID principles
- ✅ Comprehensive documentation

## 🚀 Quick Start Guide

### Prerequisites
- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Git** for cloning the repository
- **Linux/macOS/Windows** with WSL2

### One-Command Deployment

```bash
# Clone the repository
git clone <your-repository-url>
cd todo-task-manager

# Start all containers
docker-compose up --build -d
```

### Verify Deployment

```bash
# Check container status
docker-compose ps

# All containers should show as "healthy"
# Test the application
curl http://localhost/api/health
```

## 🌐 Access Points

Once deployed, access the application at:

- **🎯 Main Application**: http://localhost
- **🔧 Backend API**: http://localhost:5000
- **🏥 Health Checks**: 
  - Frontend: http://localhost/health
  - Backend: http://localhost/api/health
- **🔍 Debug Interface**: http://localhost/debug/tasks

## 📋 API Documentation

### Task Management Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `GET` | `/api/tasks` | Get 5 most recent incomplete tasks | - |
| `POST` | `/api/tasks` | Create a new task | `{"title": "string", "description": "string"}` |
| `PUT` | `/api/tasks/{id}/complete` | Mark task as completed | - |
| `GET` | `/api/health` | API health check | - |

### Example API Usage

```bash
# Get all active tasks
curl http://localhost/api/tasks

# Create a new task
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread"}'

# Complete a task
curl -X PUT http://localhost/api/tasks/1/complete

# Health check
curl http://localhost/api/health
```

## 🗄️ Database Schema

The application uses a MySQL database with the "task" table:

```sql
CREATE TABLE task (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_completed (completed),
    INDEX idx_created_at (created_at)
);
```

## 🧪 Testing

The application includes comprehensive test coverage:

### Running Tests

```bash
# Install test dependencies
pip install -r test-requirements.txt

# Run all tests with