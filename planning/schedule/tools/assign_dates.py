#!/usr/bin/env python3
"""
Property Santa Ray - Smart Date Assignment Tool
Intelligently assigns start and end dates to all tasks based on:
- Move-in deadlines
- Task dependencies
- Priorities
- Assignee capacity
- Labor hour estimates
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

DB_PATH = Path(__file__).parent.parent / "data" / "property_tasks.db"


def connect_db():
    """Connect to the database."""
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("   Run init_database.py first.")
        exit(1)
    return sqlite3.connect(DB_PATH)


def get_user_deadlines():
    """Get move-in deadlines from user."""
    print("\n" + "=" * 70)
    print("Smart Date Scheduler - Set Project Deadlines")
    print("=" * 70)
    print("\nThis tool will assign realistic dates to all tasks based on your deadlines.")
    print()

    # Get PS move-in deadline
    while True:
        ps_deadline = input("When does PS need to move in? (YYYY-MM-DD): ").strip()
        try:
            ps_date = datetime.strptime(ps_deadline, "%Y-%m-%d").date()
            break
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD (e.g., 2025-12-01)")

    # Get Chris move-in deadline
    while True:
        chris_deadline = input("When does Chris need to move in? (YYYY-MM-DD): ").strip()
        try:
            chris_date = datetime.strptime(chris_deadline, "%Y-%m-%d").date()
            if chris_date < ps_date:
                print("⚠️  Warning: Chris move-in is before PS move-in. Is this correct?")
                confirm = input("Continue? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            break
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD (e.g., 2026-01-01)")

    # Get start date
    today = datetime.now().date()
    while True:
        start_input = input(f"When can work start? (YYYY-MM-DD, press Enter for today: {today}): ").strip()
        if not start_input:
            start_date = today
            break
        try:
            start_date = datetime.strptime(start_input, "%Y-%m-%d").date()
            if start_date > ps_date:
                print("❌ Start date must be before PS move-in deadline")
                continue
            break
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD")

    print(f"\n✅ Deadlines set:")
    print(f"   Start Date: {start_date}")
    print(f"   PS Move-In: {ps_date}")
    print(f"   Chris Move-In: {chris_date}")

    return {
        'start_date': start_date,
        'ps_movein': ps_date,
        'chris_movein': chris_date
    }


def load_tasks(conn):
    """Load all tasks with their details."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            t.task_id, t.name, t.priority, t.status,
            t.required_before_ps_movein, t.required_before_chris_movein,
            t.labor_hours_min, t.labor_hours_max,
            t.start_date, t.end_date,
            a.name as assignee_name, a.type as assignee_type
        FROM tasks t
        LEFT JOIN assignees a ON t.assignee_id = a.assignee_id
        WHERE t.status != 'Completed'
        ORDER BY
            CASE t.priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
            END,
            t.name
    """)

    tasks = {}
    for row in cursor.fetchall():
        task_id, name, priority, status, ps_req, chris_req, hours_min, hours_max, start, end, assignee, assignee_type = row
        tasks[task_id] = {
            'id': task_id,
            'name': name,
            'priority': priority,
            'status': status,
            'ps_required': bool(ps_req),
            'chris_required': bool(chris_req),
            'hours_min': hours_min or 4,  # Default to 4 hours min
            'hours_max': hours_max or 8,  # Default to 8 hours max
            'start_date': start,
            'end_date': end,
            'assignee': assignee or 'Unassigned',
            'assignee_type': assignee_type,
            'dependencies': [],
            'dependents': []
        }

    return tasks


def load_dependencies(conn, tasks):
    """Load task dependencies and add to task dict."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT task_id, depends_on_task_id, dependency_type
        FROM task_dependencies
    """)

    for task_id, depends_on_id, dep_type in cursor.fetchall():
        if task_id in tasks and depends_on_id in tasks:
            tasks[task_id]['dependencies'].append(depends_on_id)
            tasks[depends_on_id]['dependents'].append(task_id)

    return tasks


def estimate_task_duration(task):
    """Estimate task duration in days based on labor hours."""
    # Use average hours
    avg_hours = (task['hours_min'] + task['hours_max']) / 2

    # Assume 8-hour work days
    work_days = avg_hours / 8

    # Round up to at least 1 day, max 14 days for a single task
    duration_days = max(1, min(14, int(work_days + 0.5)))

    # Add buffer for contractor work (scheduling, inspections, etc.)
    if task['assignee_type'] in ['Contractor', 'Licensed Professional']:
        duration_days += 1

    return duration_days


def topological_sort(tasks):
    """
    Perform topological sort on tasks to determine scheduling order.
    Returns list of task_ids in dependency order.
    """
    # Calculate in-degree for each task
    in_degree = {task_id: len(task['dependencies']) for task_id, task in tasks.items()}

    # Queue of tasks with no dependencies
    queue = deque([task_id for task_id, degree in in_degree.items() if degree == 0])
    sorted_tasks = []

    while queue:
        # Process tasks in priority order
        queue = deque(sorted(queue, key=lambda tid: (
            0 if tasks[tid]['priority'] == 'Critical' else
            1 if tasks[tid]['priority'] == 'High' else
            2 if tasks[tid]['priority'] == 'Medium' else 3,
            tasks[tid]['name']
        )))

        task_id = queue.popleft()
        sorted_tasks.append(task_id)

        # Reduce in-degree for dependent tasks
        for dependent_id in tasks[task_id]['dependents']:
            in_degree[dependent_id] -= 1
            if in_degree[dependent_id] == 0:
                queue.append(dependent_id)

    # Check for cycles
    if len(sorted_tasks) != len(tasks):
        print("⚠️  Warning: Circular dependencies detected. Some tasks may not be scheduled correctly.")

    return sorted_tasks


def schedule_tasks(tasks, deadlines):
    """
    Assign dates to tasks using forward scheduling with deadline constraints.
    """
    # Get topological order
    task_order = topological_sort(tasks)

    # Track when each assignee is available
    assignee_availability = defaultdict(lambda: deadlines['start_date'])

    # Track latest required completion for dependent tasks
    latest_end = {}

    # First pass: identify tasks that MUST complete before deadlines
    for task_id in task_order:
        task = tasks[task_id]
        if task['ps_required']:
            latest_end[task_id] = deadlines['ps_movein']
        elif task['chris_required']:
            latest_end[task_id] = deadlines['chris_movein']

    # Propagate constraints backward through dependencies
    for task_id in reversed(task_order):
        if task_id in latest_end:
            for dep_id in tasks[task_id]['dependencies']:
                duration = estimate_task_duration(tasks[task_id])
                required_start = latest_end[task_id] - timedelta(days=duration)
                if dep_id not in latest_end or required_start < latest_end[dep_id]:
                    latest_end[dep_id] = required_start

    # Second pass: assign actual dates forward from start date
    for task_id in task_order:
        task = tasks[task_id]

        # Start date is the latest of:
        # 1. When assignee is available
        # 2. After all dependencies complete
        # 3. Project start date
        earliest_start = deadlines['start_date']

        # Check assignee availability
        if task['assignee'] in assignee_availability:
            earliest_start = max(earliest_start, assignee_availability[task['assignee']])

        # Check dependencies
        for dep_id in task['dependencies']:
            if tasks[dep_id]['end_date']:
                dep_end = datetime.strptime(tasks[dep_id]['end_date'], "%Y-%m-%d").date()
                # Add 1 day buffer after dependency
                earliest_start = max(earliest_start, dep_end + timedelta(days=1))

        # Calculate duration
        duration = estimate_task_duration(task)

        # Set start date
        start_date = earliest_start

        # Check if we need to rush to meet deadline
        if task_id in latest_end:
            # Must start early enough to finish by deadline
            required_start = latest_end[task_id] - timedelta(days=duration)
            if required_start < start_date:
                print(f"⚠️  Warning: Task '{task['name']}' may not meet deadline!")
                print(f"   Needs to start by {required_start}, but earliest available is {start_date}")

        # Skip weekends (basic logic - move to next Monday if starting on weekend)
        while start_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            start_date += timedelta(days=1)

        # Calculate end date (accounting for weekends)
        end_date = start_date
        days_added = 0
        while days_added < duration:
            end_date += timedelta(days=1)
            if end_date.weekday() < 5:  # Only count weekdays
                days_added += 1

        # Assign dates to task
        task['start_date'] = start_date.strftime("%Y-%m-%d")
        task['end_date'] = end_date.strftime("%Y-%m-%d")

        # Update assignee availability
        assignee_availability[task['assignee']] = end_date + timedelta(days=1)

    return tasks


def save_dates_to_db(conn, tasks):
    """Save assigned dates back to database."""
    cursor = conn.cursor()

    updates = 0
    for task_id, task in tasks.items():
        if task['start_date'] and task['end_date']:
            cursor.execute("""
                UPDATE tasks
                SET start_date = ?, end_date = ?, updated_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
            """, (task['start_date'], task['end_date'], task_id))
            updates += 1

    conn.commit()
    return updates


def export_schedule_json(tasks, output_path):
    """Export schedule as JSON for dashboard."""
    schedule = []
    for task_id, task in tasks.items():
        schedule.append({
            'id': task_id,
            'name': task['name'],
            'priority': task['priority'],
            'status': task['status'],
            'start_date': task['start_date'],
            'end_date': task['end_date'],
            'assignee': task['assignee'],
            'ps_required': task['ps_required'],
            'chris_required': task['chris_required'],
            'dependencies': task['dependencies']
        })

    with open(output_path, 'w') as f:
        json.dump(schedule, f, indent=2)


def print_summary(tasks, deadlines):
    """Print scheduling summary."""
    print("\n" + "=" * 70)
    print("📅 Scheduling Summary")
    print("=" * 70)

    # Count by priority
    by_priority = defaultdict(int)
    for task in tasks.values():
        by_priority[task['priority']] += 1

    print(f"\nTotal Tasks Scheduled: {len(tasks)}")
    for priority in ['Critical', 'High', 'Medium', 'Low']:
        if priority in by_priority:
            print(f"  {priority}: {by_priority[priority]} tasks")

    # Find last task end date
    last_end = max(
        datetime.strptime(task['end_date'], "%Y-%m-%d").date()
        for task in tasks.values()
        if task['end_date']
    )

    print(f"\nProject Timeline:")
    print(f"  Start: {deadlines['start_date']}")
    print(f"  Last Task Completes: {last_end}")
    print(f"  PS Move-In Deadline: {deadlines['ps_movein']}")
    print(f"  Chris Move-In Deadline: {deadlines['chris_movein']}")

    # Check if we meet deadlines
    ps_required_tasks = [t for t in tasks.values() if t['ps_required']]
    if ps_required_tasks:
        latest_ps = max(
            datetime.strptime(t['end_date'], "%Y-%m-%d").date()
            for t in ps_required_tasks
            if t['end_date']
        )
        if latest_ps <= deadlines['ps_movein']:
            print(f"\n✅ PS critical tasks complete by: {latest_ps} (meets deadline)")
        else:
            print(f"\n❌ PS critical tasks complete by: {latest_ps} (MISSES deadline by {(latest_ps - deadlines['ps_movein']).days} days)")

    # Warn about tight schedules
    total_days = (last_end - deadlines['start_date']).days
    print(f"\nTotal project duration: {total_days} days ({total_days / 7:.1f} weeks)")


def main():
    """Main execution function."""
    print("\n🏗️  Smart Date Scheduler for Santa Ray Property")

    # Get deadlines from user
    deadlines = get_user_deadlines()

    # Load data
    print("\n📊 Loading tasks and dependencies...")
    conn = connect_db()
    tasks = load_tasks(conn)
    tasks = load_dependencies(conn, tasks)
    print(f"   Loaded {len(tasks)} tasks")

    # Schedule tasks
    print("\n🗓️  Calculating optimal schedule...")
    tasks = schedule_tasks(tasks, deadlines)

    # Save to database
    print("\n💾 Saving dates to database...")
    updates = save_dates_to_db(conn, tasks)
    print(f"   Updated {updates} tasks")

    # Export JSON for dashboard
    json_path = Path(__file__).parent.parent / "data" / "tasks.json"
    export_schedule_json(tasks, json_path)
    print(f"   Exported schedule to {json_path}")

    # Print summary
    print_summary(tasks, deadlines)

    # Close connection
    conn.close()

    print("\n✅ Date assignment complete!")
    print("\nNext steps:")
    print("  1. Open dashboard.html to view your schedule")
    print("  2. Run export_calendar.py to sync to Google Calendar")
    print("  3. Adjust dates as needed in the dashboard")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
