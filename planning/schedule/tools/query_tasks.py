#!/usr/bin/env python3
"""
Property Santa Ray - Task Database Query Tool
Interactive tool for exploring and querying the task database.
"""

import sqlite3
from pathlib import Path
from tabulate import tabulate

DB_PATH = Path(__file__).parent.parent / "data" / "property_tasks.db"


def connect_db():
    """Connect to the database."""
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("   Run init_database.py first.")
        exit(1)
    return sqlite3.connect(DB_PATH)


def query_tasks_by_priority(conn):
    """Query tasks grouped by priority."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT priority, name, status, assignee_name, cost_estimate_min, cost_estimate_max
        FROM tasks_with_assignees
        ORDER BY
            CASE priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
            END,
            name
    """)

    tasks_by_priority = {}
    for priority, name, status, assignee, cost_min, cost_max in cursor.fetchall():
        if priority not in tasks_by_priority:
            tasks_by_priority[priority] = []
        cost_range = f"${cost_min or 0}-${cost_max or 0}" if cost_min or cost_max else "N/A"
        tasks_by_priority[priority].append([name[:50], status, assignee or "Unassigned", cost_range])

    for priority, tasks in tasks_by_priority.items():
        print(f"\n{priority} Priority Tasks ({len(tasks)} tasks)")
        print("=" * 100)
        print(tabulate(tasks, headers=["Task Name", "Status", "Assignee", "Cost Range"], tablefmt="grid"))


def query_critical_path(conn):
    """Query critical path tasks (required before PS move-in)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, priority, status, assignee_name,
               labor_hours_min || '-' || labor_hours_max as hours,
               cost_estimate_min || '-' || cost_estimate_max as cost
        FROM tasks_with_assignees
        WHERE required_before_ps_movein = TRUE
        ORDER BY
            CASE priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
            END,
            name
    """)

    tasks = []
    for name, priority, status, assignee, hours, cost in cursor.fetchall():
        tasks.append([name[:60], priority, status, assignee or "Unassigned", hours, f"${cost}"])

    print(f"\n🚨 Critical Path Tasks (Required before PS Move-In)")
    print("=" * 120)
    print(tabulate(tasks, headers=["Task Name", "Priority", "Status", "Assignee", "Hours", "Cost"], tablefmt="grid"))


def query_by_assignee(conn):
    """Query tasks grouped by assignee."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT assignee_name, COUNT(*) as task_count,
               SUM(COALESCE(cost_estimate_min, 0) + COALESCE(cost_estimate_max, 0)) / 2 as avg_total_cost
        FROM tasks_with_assignees
        WHERE assignee_name IS NOT NULL
        GROUP BY assignee_name
        ORDER BY task_count DESC
    """)

    assignees = []
    for assignee, count, total_cost in cursor.fetchall():
        assignees.append([assignee, count, f"${total_cost:.2f}"])

    print(f"\n👥 Tasks by Assignee")
    print("=" * 80)
    print(tabulate(assignees, headers=["Assignee", "Task Count", "Est. Total Cost"], tablefmt="grid"))


def query_project_summary(conn):
    """Query overall project summary."""
    cursor = conn.cursor()

    # Total tasks and status breakdown
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]

    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM tasks
        GROUP BY status
        ORDER BY count DESC
    """)
    status_breakdown = cursor.fetchall()

    # Cost estimates
    cursor.execute("""
        SELECT
            SUM(COALESCE(cost_estimate_min, 0)) as total_min,
            SUM(COALESCE(cost_estimate_max, 0)) as total_max
        FROM tasks
    """)
    total_min, total_max = cursor.fetchone()

    # Labor hours
    cursor.execute("""
        SELECT
            SUM(COALESCE(labor_hours_min, 0)) as hours_min,
            SUM(COALESCE(labor_hours_max, 0)) as hours_max
        FROM tasks
    """)
    hours_min, hours_max = cursor.fetchone()

    print("\n📊 Project Summary")
    print("=" * 80)
    print(f"Total Tasks: {total_tasks}")
    print(f"Total Cost Estimate: ${total_min:,.2f} - ${total_max:,.2f}")
    print(f"Total Labor Hours: {hours_min:,.0f} - {hours_max:,.0f} hours")
    print()
    print("Status Breakdown:")
    for status, count in status_breakdown:
        print(f"  {status}: {count} tasks")


def query_dependencies(conn):
    """Query task dependencies."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t1.name as task, t2.name as depends_on, td.dependency_type, td.notes
        FROM task_dependencies td
        JOIN tasks t1 ON td.task_id = t1.task_id
        JOIN tasks t2 ON td.depends_on_task_id = t2.task_id
        ORDER BY t1.name
    """)

    deps = []
    for task, depends_on, dep_type, notes in cursor.fetchall():
        deps.append([task[:40], depends_on[:40], dep_type, notes[:40] if notes else ""])

    if deps:
        print(f"\n🔗 Task Dependencies ({len(deps)} dependencies)")
        print("=" * 120)
        print(tabulate(deps, headers=["Task", "Depends On", "Type", "Notes"], tablefmt="grid"))
    else:
        print("\nNo task dependencies found.")


def interactive_menu():
    """Interactive query menu."""
    conn = connect_db()

    while True:
        print("\n" + "=" * 60)
        print("Property Santa Ray - Task Database Query Tool")
        print("=" * 60)
        print("\nSelect a query:")
        print("  1. View tasks by priority")
        print("  2. View critical path tasks (required before PS move-in)")
        print("  3. View tasks by assignee")
        print("  4. View project summary")
        print("  5. View task dependencies")
        print("  6. Exit")
        print()

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            query_tasks_by_priority(conn)
        elif choice == "2":
            query_critical_path(conn)
        elif choice == "3":
            query_by_assignee(conn)
        elif choice == "4":
            query_project_summary(conn)
        elif choice == "5":
            query_dependencies(conn)
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-6.")

        input("\nPress Enter to continue...")

    conn.close()


if __name__ == "__main__":
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
