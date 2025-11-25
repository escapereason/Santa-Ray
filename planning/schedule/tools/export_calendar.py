#!/usr/bin/env python3
"""
Property Santa Ray - Calendar Export
Exports tasks to iCal format for Google Calendar import.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import sys

DB_PATH = Path(__file__).parent.parent / "data" / "property_tasks.db"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "santa_ray_tasks.ics"


def generate_ical(conn, days_ahead=None):
    """Generate iCal format calendar file.

    Args:
        conn: Database connection
        days_ahead: If specified, only include tasks starting within this many days
    """

    cursor = conn.cursor()

    # Build query with optional date filter
    query = """
        SELECT
            name,
            description,
            location,
            priority,
            status,
            COALESCE(start_date, date('now')) as start_date,
            COALESCE(end_date, date('now', '+7 days')) as end_date,
            assignee_name,
            cost_estimate_min,
            cost_estimate_max,
            labor_hours_min,
            labor_hours_max
        FROM tasks_with_assignees
        WHERE status != 'Completed'
    """

    if days_ahead:
        cutoff_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        query += f" AND start_date <= '{cutoff_date}'"

    query += " ORDER BY required_before_ps_movein DESC, priority, start_date"

    cursor.execute(query)

    tasks = cursor.fetchall()

    # iCal header
    ical = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Santa Ray Property//Task Schedule//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Santa Ray Property Repairs
X-WR-TIMEZONE:America/Los_Angeles
X-WR-CALDESC:Property repair and renovation task schedule
"""

    # Add each task as an event
    for i, (name, desc, location, priority, status, start, end, assignee, cost_min, cost_max, hours_min, hours_max) in enumerate(tasks):
        # Generate unique ID
        uid = f"santa-ray-task-{i}@property-repairs.local"

        # Format dates (iCal uses YYYYMMDD format for all-day events)
        start_formatted = start.replace('-', '')
        end_formatted = end.replace('-', '')

        # Create description with task details
        event_desc = []
        if desc:
            event_desc.append(f"Description: {desc}")
        if assignee:
            event_desc.append(f"Assignee: {assignee}")
        if cost_min or cost_max:
            event_desc.append(f"Cost Estimate: ${cost_min or 0} - ${cost_max or 0}")
        if hours_min or hours_max:
            event_desc.append(f"Labor Hours: {hours_min or 0} - {hours_max or 0}")
        event_desc.append(f"Priority: {priority}")
        event_desc.append(f"Status: {status}")

        description = "\\n".join(event_desc)

        # Set priority (iCal uses 1=high, 5=medium, 9=low)
        ical_priority = {
            "Critical": "1",
            "High": "3",
            "Medium": "5",
            "Low": "9"
        }.get(priority, "5")

        # Set categories and color
        categories = f"{priority} Priority"

        ical += f"""
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART;VALUE=DATE:{start_formatted}
DTEND;VALUE=DATE:{end_formatted}
SUMMARY:[{priority}] {name}
DESCRIPTION:{description}
LOCATION:{location or 'Property - 757 Santa Ray Avenue'}
STATUS:{'CONFIRMED' if status == 'In Progress' else 'TENTATIVE'}
PRIORITY:{ical_priority}
CATEGORIES:{categories}
END:VEVENT
"""

    ical += "END:VCALENDAR\n"

    return ical


def main():
    """Generate and save iCal file."""
    print("=" * 60)
    print("Property Santa Ray - Calendar Export")
    print("=" * 60)
    print()

    # Parse command line arguments
    days_ahead = None
    if len(sys.argv) > 1:
        try:
            days_ahead = int(sys.argv[1])
            print(f"ℹ️  Filtering to tasks starting within next {days_ahead} days")
        except ValueError:
            print("❌ Invalid argument. Usage: python3 export_calendar.py [days]")
            print("   Example: python3 export_calendar.py 30  (exports next 30 days only)")
            return

    if not DB_PATH.exists():
        print("❌ Database not found! Please run init_database.py first.")
        return

    conn = sqlite3.connect(DB_PATH)

    print("📅 Generating iCal calendar file...")
    ical = generate_ical(conn, days_ahead)

    # Count tasks
    task_count = ical.count('BEGIN:VEVENT')

    with open(OUTPUT_PATH, 'w') as f:
        f.write(ical)

    print(f"✅ Calendar file saved to: {OUTPUT_PATH}")
    print(f"   {task_count} tasks exported")
    print()
    print("📌 How to import to Google Calendar:")
    print("   1. Open Google Calendar (calendar.google.com)")
    print("   2. Click the '+' next to 'Other calendars'")
    print("   3. Select 'Create new calendar' (recommended)")
    print("      Name it 'Santa Ray Repairs' to keep separate")
    print("   4. Click the '+' again and select 'Import'")
    print(f"   5. Choose the file: {OUTPUT_PATH.name}")
    print("   6. Select your 'Santa Ray Repairs' calendar")
    print("   7. Click 'Import'")
    print()
    print("ℹ️  Tasks are imported as all-day events")
    print("ℹ️  Priority levels are color-coded and categorized")
    print()
    print("💡 Tips:")
    print("   - Create a separate calendar so tasks don't clutter your main calendar")
    print("   - Re-export and re-import when dates change")
    print("   - Use different colors for the Santa Ray calendar in Google Calendar")
    if not days_ahead:
        print("   - To export only upcoming tasks: python3 export_calendar.py 30")

    conn.close()


if __name__ == "__main__":
    main()
