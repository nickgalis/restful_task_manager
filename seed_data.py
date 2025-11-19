"""
Seed data script for the Task Management API.

This script populates the database with sample users, categories, and tasks
for testing and demonstration purposes.
"""

from database import SessionLocal, init_db
from models import User, Category, Task, TaskStatus, TaskPriority
from datetime import datetime, timedelta

def seed_data():
    """Populate the database with sample data."""
    
    # Initialize database
    init_db()
    
    # Create a new session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("Database already contains data. Skipping seed...")
            return
        
        print("Seeding database with sample data...")
        
        # Create sample users
        users = [
            User(username='john_doe', email='john@example.com'),
            User(username='jane_smith', email='jane@example.com'),
            User(username='bob_wilson', email='bob@example.com')
        ]
        
        for user in users:
            db.add(user)
        
        db.commit()
        print(f"✓ Created {len(users)} users")
        
        # Create categories for each user
        categories = [
            # John's categories
            Category(name='Work', description='Work-related tasks', user_id=1),
            Category(name='Personal', description='Personal tasks and errands', user_id=1),
            Category(name='Shopping', description='Shopping lists and purchases', user_id=1),
            
            # Jane's categories
            Category(name='Project Alpha', description='Tasks for Project Alpha', user_id=2),
            Category(name='Home', description='Home improvement tasks', user_id=2),
            
            # Bob's categories
            Category(name='Development', description='Software development tasks', user_id=3),
            Category(name='Learning', description='Learning and training tasks', user_id=3),
        ]
        
        for category in categories:
            db.add(category)
        
        db.commit()
        print(f"✓ Created {len(categories)} categories")
        
        # Create sample tasks
        today = datetime.utcnow()
        
        tasks = [
            # John's tasks
            Task(
                title='Complete quarterly report',
                description='Finish Q4 financial report for management review',
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                due_date=today + timedelta(days=2),
                category_id=1,
                user_id=1
            ),
            Task(
                title='Team meeting preparation',
                description='Prepare slides for Monday team meeting',
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
                due_date=today + timedelta(days=3),
                category_id=1,
                user_id=1
            ),
            Task(
                title='Buy groceries',
                description='Get milk, eggs, bread, and vegetables',
                status=TaskStatus.PENDING,
                priority=TaskPriority.LOW,
                due_date=today + timedelta(days=1),
                category_id=3,
                user_id=1
            ),
            Task(
                title='Schedule dentist appointment',
                description='Call dentist office for annual checkup',
                status=TaskStatus.COMPLETED,
                priority=TaskPriority.MEDIUM,
                due_date=today - timedelta(days=1),
                category_id=2,
                user_id=1
            ),
            Task(
                title='Pay utility bills',
                description='Pay electricity and water bills online',
                status=TaskStatus.PENDING,
                priority=TaskPriority.HIGH,
                due_date=today + timedelta(days=5),
                category_id=2,
                user_id=1
            ),
            
            # Jane's tasks
            Task(
                title='Design database schema',
                description='Create ERD for new database structure',
                status=TaskStatus.COMPLETED,
                priority=TaskPriority.HIGH,
                due_date=today - timedelta(days=2),
                category_id=4,
                user_id=2
            ),
            Task(
                title='Implement user authentication',
                description='Add JWT-based authentication to the API',
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                due_date=today + timedelta(days=4),
                category_id=4,
                user_id=2
            ),
            Task(
                title='Write API documentation',
                description='Document all API endpoints with examples',
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
                due_date=today + timedelta(days=7),
                category_id=4,
                user_id=2
            ),
            Task(
                title='Fix kitchen sink',
                description='Replace leaky faucet in kitchen',
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                due_date=today + timedelta(days=1),
                category_id=5,
                user_id=2
            ),
            Task(
                title='Paint living room',
                description='Buy paint and repaint living room walls',
                status=TaskStatus.PENDING,
                priority=TaskPriority.LOW,
                due_date=today + timedelta(days=14),
                category_id=5,
                user_id=2
            ),
            
            # Bob's tasks
            Task(
                title='Refactor authentication module',
                description='Clean up authentication code and improve security',
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                due_date=today + timedelta(days=3),
                category_id=6,
                user_id=3
            ),
            Task(
                title='Fix bug #234',
                description='Resolve issue with user profile update',
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
                due_date=today + timedelta(days=2),
                category_id=6,
                user_id=3
            ),
            Task(
                title='Complete Python course',
                description='Finish remaining modules on advanced Python topics',
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.MEDIUM,
                due_date=today + timedelta(days=10),
                category_id=7,
                user_id=3
            ),
            Task(
                title='Read Docker documentation',
                description='Study Docker best practices and deployment strategies',
                status=TaskStatus.PENDING,
                priority=TaskPriority.LOW,
                due_date=today + timedelta(days=15),
                category_id=7,
                user_id=3
            ),
            Task(
                title='Setup CI/CD pipeline',
                description='Configure GitHub Actions for automated testing',
                status=TaskStatus.COMPLETED,
                priority=TaskPriority.HIGH,
                due_date=today - timedelta(days=3),
                category_id=6,
                user_id=3
            ),
        ]
        
        for task in tasks:
            db.add(task)
        
        db.commit()
        print(f"✓ Created {len(tasks)} tasks")
        
        print("\n" + "="*50)
        print("Database seeded successfully!")
        print("="*50)
        print("\nSample data summary:")
        print(f"  • Users: {len(users)}")
        print(f"  • Categories: {len(categories)}")
        print(f"  • Tasks: {len(tasks)}")
        print("\nYou can now test the API with this sample data.")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {str(e)}")
    finally:
        db.close()


if __name__ == '__main__':
    seed_data()
