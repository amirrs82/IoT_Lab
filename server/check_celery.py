#!/usr/bin/env python
"""
Script to check Celery configuration and scheduled tasks
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.celery import app
from celery import current_app

def check_celery_config():
    """Check Celery configuration"""
    print("=== CELERY CONFIGURATION ===")
    print(f"Broker URL: {app.conf.broker_url}")
    print(f"Result Backend: {app.conf.result_backend}")
    print(f"Timezone: {app.conf.timezone}")
    print(f"Task Serializer: {app.conf.task_serializer}")
    print(f"Accept Content: {app.conf.accept_content}")
    print()

def check_registered_tasks():
    """Check registered tasks"""
    print("=== REGISTERED TASKS ===")
    tasks = list(app.tasks.keys())
    for task in sorted(tasks):
        if not task.startswith('celery.'):  # Skip built-in Celery tasks
            print(f"- {task}")
    print()

def check_periodic_tasks():
    """Check periodic tasks configuration"""
    print("=== PERIODIC TASKS ===")
    # Import tasks to ensure they are registered
    import cryptocurrency.tasks
    
    if hasattr(app.conf, 'beat_schedule'):
        for name, task_info in app.conf.beat_schedule.items():
            print(f"Task: {name}")
            print(f"  Task function: {task_info.get('task', 'N/A')}")
            print(f"  Schedule: {task_info.get('schedule', 'N/A')}")
            print()
    else:
        print("No beat_schedule found in configuration")
    print()

def test_task_manually():
    """Test running the task manually"""
    print("=== MANUAL TASK TEST ===")
    try:
        from cryptocurrency.tasks import update_currency_prices
        print("Testing update_currency_prices task...")
        result = update_currency_prices.delay()
        print(f"Task ID: {result.task_id}")
        print("Task submitted successfully!")
        
        # Try to get result (with timeout)
        try:
            task_result = result.get(timeout=10)
            print(f"Task result: {task_result}")
        except Exception as e:
            print(f"Could not get task result: {e}")
    except Exception as e:
        print(f"Error testing task: {e}")
    print()

if __name__ == "__main__":
    # Set Redis URL for local development
    os.environ['REDIS_URL'] = 'redis://localhost:10002/0'
    
    check_celery_config()
    check_registered_tasks()
    check_periodic_tasks()
    test_task_manually()
