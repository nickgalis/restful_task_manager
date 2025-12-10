# Task Management RESTful API

A comprehensive RESTful API for managing tasks, categories, and users built with Flask and SQLite. This API provides full CRUD operations with proper validation, error handling, filtering, and sorting capabilities.

## Features

- Complete REST API with proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Three-tier data model: Users → Categories → Tasks
- SQLite database with SQLAlchemy ORM
- Input validation and comprehensive error handling
- Advanced filtering and sorting for tasks
- Cascade delete operations
- Auto-populated timestamps
- Well-documented endpoints
- Sample data seeding script
- Postman collection for testing

## Technology Stack

- **Python 3.x** - Programming language
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Database engine

## Project Structure

```
task-api/
├── app.py                      # Main Flask application
├── models.py                   # Database models
├── database.py                 # Database initialization and connection
├── requirements.txt            # Python dependencies
├── seed_data.py               # Sample data seeding script
├── postman_collection.json    # Postman API collection
└── README.md                  # This file
```

## Database Schema

### Users Table
| Column     | Type     | Constraints           |
|------------|----------|-----------------------|
| id         | INTEGER  | PRIMARY KEY           |
| username   | STRING   | UNIQUE, NOT NULL      |
| email      | STRING   | NOT NULL              |
| created_at | DATETIME | NOT NULL, AUTO        |

### Categories Table
| Column      | Type     | Constraints                    |
|-------------|----------|--------------------------------|
| id          | INTEGER  | PRIMARY KEY                    |
| name        | STRING   | NOT NULL                       |
| description | TEXT     |                                |
| user_id     | INTEGER  | FOREIGN KEY, NOT NULL          |

### Tasks Table
| Column      | Type     | Constraints                    |
|-------------|----------|--------------------------------|
| id          | INTEGER  | PRIMARY KEY                    |
| title       | STRING   | NOT NULL                       |
| description | TEXT     |                                |
| status      | ENUM     | pending/in_progress/completed  |
| priority    | ENUM     | low/medium/high                |
| due_date    | DATETIME |                                |
| category_id | INTEGER  | FOREIGN KEY, NOT NULL          |
| user_id     | INTEGER  | FOREIGN KEY, NOT NULL          |
| created_at  | DATETIME | NOT NULL, AUTO                 |
| updated_at  | DATETIME | NOT NULL, AUTO                 |

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project**
   ```bash
   cd restful_task_manager
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python database.py
   ```

5. **Seed sample data (optional)**
   ```bash
   python seed_data.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## API Endpoints

### Users

#### Create User
```bash
POST /api/users
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2025-11-19T10:30:00"
}
```

#### Get User by ID
```bash
GET /api/users/{id}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2025-11-19T10:30:00"
}
```

#### Get All Users
```bash
GET /api/users
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2025-11-19T10:30:00"
  },
  ...
]
```

---

### Categories

#### Create Category
```bash
POST /api/categories
Content-Type: application/json

{
  "name": "Work",
  "description": "Work-related tasks",
  "user_id": 1
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Work",
  "description": "Work-related tasks",
  "user_id": 1
}
```

#### Get All Categories
```bash
GET /api/categories?user_id=1
```

**Query Parameters:**
- `user_id` (optional) - Filter categories by user

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Work",
    "description": "Work-related tasks",
    "user_id": 1
  },
  ...
]
```

#### Get Category by ID
```bash
GET /api/categories/{id}
```

#### Update Category
```bash
PUT /api/categories/{id}
Content-Type: application/json

{
  "name": "Work Projects",
  "description": "All work-related projects",
  "user_id": 1
}
```

#### Delete Category
```bash
DELETE /api/categories/{id}
```

**Response (200 OK):**
```json
{
  "message": "Category deleted successfully"
}
```

---

### Tasks

#### Create Task
```bash
POST /api/tasks
Content-Type: application/json

{
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "status": "pending",
  "priority": "high",
  "due_date": "2025-11-25T17:00:00",
  "category_id": 1,
  "user_id": 1
}
```

**Required fields:** `title`, `category_id`, `user_id`

**Optional fields:** `description`, `status`, `priority`, `due_date`

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "status": "pending",
  "priority": "high",
  "due_date": "2025-11-25T17:00:00",
  "category_id": 1,
  "user_id": 1,
  "created_at": "2025-11-19T10:30:00",
  "updated_at": "2025-11-19T10:30:00"
}
```

#### Get All Tasks (with Filtering & Sorting)
```bash
GET /api/tasks?status=pending&priority=high&sort_by=due_date&order=asc
```

**Query Parameters (all optional):**
- `status` - Filter by status (`pending`, `in_progress`, `completed`)
- `priority` - Filter by priority (`low`, `medium`, `high`)
- `category_id` - Filter by category ID
- `user_id` - Filter by user ID
- `sort_by` - Sort field (`due_date`, `created_at`, `priority`, `status`, `updated_at`)
- `order` - Sort order (`asc`, `desc`)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Complete project documentation",
    "status": "pending",
    "priority": "high",
    ...
  },
  ...
]
```

#### Get Task by ID
```bash
GET /api/tasks/{id}
```

#### Update Task (Full Update)
```bash
PUT /api/tasks/{id}
Content-Type: application/json

{
  "title": "Complete project documentation (Updated)",
  "description": "Updated description",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2025-11-26T17:00:00",
  "category_id": 1,
  "user_id": 1
}
```

**Note:** PUT requires all fields to be provided.

#### Update Task (Partial Update)
```bash
PATCH /api/tasks/{id}
Content-Type: application/json

{
  "status": "completed"
}
```

**Note:** PATCH allows updating only specific fields. Useful for updating just the status, priority, or other individual fields.

#### Delete Task
```bash
DELETE /api/tasks/{id}
```

## Example cURL Commands

### Create a User
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"john_doe\",\"email\":\"john@example.com\"}"
```

### Create a Category
```bash
curl -X POST http://localhost:5000/api/categories \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Work\",\"description\":\"Work tasks\",\"user_id\":1}"
```

### Create a Task
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Test task\",\"description\":\"A test task\",\"status\":\"pending\",\"priority\":\"high\",\"category_id\":1,\"user_id\":1}"
```

### Get All Tasks with Filters
```bash
curl "http://localhost:5000/api/tasks?status=pending&priority=high&sort_by=due_date&order=asc"
```

### Update Task Status (Partial Update)
```bash
curl -X PATCH http://localhost:5000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d "{\"status\":\"completed\"}"
```

### Delete a Task
```bash
curl -X DELETE http://localhost:5000/api/tasks/1
```

## Error Handling

The API returns appropriate HTTP status codes and JSON error messages:

### Status Codes
- `200 OK` - Successful GET, PUT, PATCH, DELETE
- `201 Created` - Successful POST (resource created)
- `400 Bad Request` - Invalid input or validation error
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Error Response Format
```json
{
  "error": "Detailed error message"
}
```

### Examples

**Missing required field:**
```json
{
  "error": "Missing required fields: title, user_id"
}
```

**Invalid enum value:**
```json
{
  "error": "Invalid status. Must be one of: pending, in_progress, completed"
}
```

**Resource not found:**
```json
{
  "error": "Task not found"
}
```

## Testing with Postman

1. Open Postman
2. Import the `postman_collection.json` file
3. The collection includes all endpoints with:
   - Pre-configured request bodies
   - Example responses
   - Parameter descriptions
   - Test scenarios

## Database Management

### Reset Database
To reset the database and clear all data:

```python
from database import reset_db
reset_db()
```

### Reinitialize with Sample Data
```bash
python seed_data.py
```

This creates:
- 3 sample users
- 7 categories across users
- 15 tasks with various statuses and priorities

## Development

### Code Style
The code follows PEP 8 style guidelines with:
- Descriptive variable names
- Comprehensive docstrings
- Proper error handling
- Separation of concerns

### Project Architecture
- **models.py** - Database models and schema definitions
- **database.py** - Database connection and initialization
- **app.py** - Flask routes and business logic

## Features Implemented

✅ **Complete CRUD Operations**
- Users: Create, Read
- Categories: Create, Read, Update, Delete
- Tasks: Create, Read, Update (PUT & PATCH), Delete

✅ **Advanced Filtering**
- Filter tasks by status, priority, category, and user
- Sort by multiple fields with ascending/descending order

✅ **Data Validation**
- Required field validation
- Enum value validation
- Foreign key validation
- Descriptive error messages

✅ **Database Features**
- Auto-populated timestamps
- Cascade delete for related records
- Proper foreign key constraints

✅ **API Best Practices**
- Proper HTTP status codes
- JSON request/response format
- RESTful URL structure
- Comprehensive error handling

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify the last line in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Database Locked Error
If you get a database locked error:
1. Close all connections to the database
2. Delete `task_manager.db`
3. Run `python database.py` to reinitialize

### Import Errors
Make sure you've activated the virtual environment and installed all dependencies:
```bash
pip install -r requirements.txt
```

## License

This project is provided as-is for educational and development purposes.

## Support

For issues or questions, please refer to the code comments and docstrings which provide detailed explanations of all functions and endpoints.
