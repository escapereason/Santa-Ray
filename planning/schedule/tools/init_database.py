#!/usr/bin/env python3
"""
Property Santa Ray - Task Database Initialization
Creates SQLite database schema for project task management and scheduling.

Database Design:
- Main tasks table with comprehensive fields for scheduling and tracking
- Reference tables for assignees, tools, and materials
- Many-to-many relationships for tools and materials
- Self-referencing dependencies for task ordering
"""

import sqlite3
import os
from pathlib import Path

# Database location
DB_PATH = Path(__file__).parent.parent / "data" / "property_tasks.db"


def init_database():
    """Initialize the SQLite database with all tables and relationships."""

    # Remove existing database if it exists (for clean init)
    if DB_PATH.exists():
        print(f"⚠️  Removing existing database at {DB_PATH}")
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    print("🔧 Creating database schema...")

    # ========================================
    # REFERENCE TABLES
    # ========================================

    # Assignees table
    cursor.execute("""
        CREATE TABLE assignees (
            assignee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT CHECK(type IN ('DIY', 'Contractor', 'Specialist')) NOT NULL,
            contact_info TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Tools table
    cursor.execute("""
        CREATE TABLE tools (
            tool_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT,
            owned BOOLEAN DEFAULT FALSE,
            purchase_cost REAL,
            rental_cost_per_day REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Materials table
    cursor.execute("""
        CREATE TABLE materials (
            material_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            unit TEXT,
            unit_cost REAL,
            supplier TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ========================================
    # MAIN TASKS TABLE
    # ========================================

    cursor.execute("""
        CREATE TABLE tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Basic Information
            name TEXT NOT NULL,
            description TEXT,
            location TEXT,

            -- Planning & Scheduling
            required_before_ps_movein BOOLEAN DEFAULT FALSE,
            required_before_chris_movein BOOLEAN DEFAULT FALSE,
            priority TEXT CHECK(priority IN ('Critical', 'High', 'Medium', 'Low')) DEFAULT 'Medium',
            status TEXT CHECK(status IN ('Not Started', 'In Progress', 'Completed', 'Blocked', 'Deferred')) DEFAULT 'Not Started',

            -- Assignment
            assignee_id INTEGER,

            -- Timeline
            start_date DATE,
            end_date DATE,
            labor_hours_min INTEGER,
            labor_hours_max INTEGER,

            -- Costs
            cost_estimate_min REAL,
            cost_estimate_max REAL,

            -- Technical Details
            technical_description TEXT,
            source_file TEXT,
            source_section TEXT,

            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completion_date DATE,

            -- Foreign Keys
            FOREIGN KEY (assignee_id) REFERENCES assignees(assignee_id)
        );
    """)

    # ========================================
    # TASK DEPENDENCIES (Self-referencing)
    # ========================================

    cursor.execute("""
        CREATE TABLE task_dependencies (
            dependency_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            depends_on_task_id INTEGER NOT NULL,
            dependency_type TEXT CHECK(dependency_type IN ('blocks', 'suggests', 'sequence')) DEFAULT 'blocks',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
            FOREIGN KEY (depends_on_task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
            CHECK (task_id != depends_on_task_id)
        );
    """)

    # ========================================
    # MANY-TO-MANY RELATIONSHIPS
    # ========================================

    # Task-Tools relationship
    cursor.execute("""
        CREATE TABLE task_tools (
            task_tool_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            tool_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            notes TEXT,

            FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
            FOREIGN KEY (tool_id) REFERENCES tools(tool_id) ON DELETE CASCADE,
            UNIQUE(task_id, tool_id)
        );
    """)

    # Task-Materials relationship
    cursor.execute("""
        CREATE TABLE task_materials (
            task_material_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            quantity REAL,
            notes TEXT,

            FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES materials(material_id) ON DELETE CASCADE,
            UNIQUE(task_id, material_id)
        );
    """)

    # ========================================
    # INDEXES for Performance
    # ========================================

    cursor.execute("CREATE INDEX idx_tasks_status ON tasks(status);")
    cursor.execute("CREATE INDEX idx_tasks_priority ON tasks(priority);")
    cursor.execute("CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);")
    cursor.execute("CREATE INDEX idx_tasks_ps_movein ON tasks(required_before_ps_movein);")
    cursor.execute("CREATE INDEX idx_tasks_chris_movein ON tasks(required_before_chris_movein);")
    cursor.execute("CREATE INDEX idx_task_dependencies_task ON task_dependencies(task_id);")
    cursor.execute("CREATE INDEX idx_task_dependencies_depends ON task_dependencies(depends_on_task_id);")

    # ========================================
    # VIEWS for Common Queries
    # ========================================

    # View: Tasks with assignee information
    cursor.execute("""
        CREATE VIEW tasks_with_assignees AS
        SELECT
            t.*,
            a.name as assignee_name,
            a.type as assignee_type
        FROM tasks t
        LEFT JOIN assignees a ON t.assignee_id = a.assignee_id;
    """)

    # View: Critical path tasks (required before PS move-in)
    cursor.execute("""
        CREATE VIEW critical_path_tasks AS
        SELECT *
        FROM tasks
        WHERE required_before_ps_movein = TRUE
           OR priority = 'Critical'
        ORDER BY
            CASE priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
            END,
            start_date;
    """)

    # View: Task summary with costs and hours
    cursor.execute("""
        CREATE VIEW task_summary AS
        SELECT
            task_id,
            name,
            priority,
            status,
            assignee_id,
            COALESCE(labor_hours_min, 0) || '-' || COALESCE(labor_hours_max, 0) as labor_hours_range,
            '$' || COALESCE(cost_estimate_min, 0) || '-$' || COALESCE(cost_estimate_max, 0) as cost_range,
            start_date,
            end_date
        FROM tasks;
    """)

    # ========================================
    # SEED REFERENCE DATA
    # ========================================

    # Default assignees
    default_assignees = [
        ('Paul (DIY)', 'DIY', 'Self', 'Primary DIY work'),
        ('Sarah (DIY)', 'DIY', 'Self', 'Assisting with DIY tasks'),
        ('Challenge Rooter', 'Contractor', 'From estimates #6296 & #6297', 'Sewer lateral and sidewalk'),
        ('Licensed Electrician', 'Specialist', 'TBD', 'All electrical work requiring permits'),
        ('Licensed Plumber', 'Specialist', 'TBD', 'All plumbing work'),
        ('Licensed Pest Control', 'Specialist', 'TBD', 'Fungus remediation and TIM-BOR application'),
        ('Licensed HVAC', 'Specialist', 'TBD', 'HVAC repairs and modifications'),
        ('General Contractor', 'Contractor', 'TBD', 'Structural and general construction'),
        ('Window Contractor', 'Specialist', 'TBD', 'Window sash replacement'),
        ('Flooring Specialist', 'Specialist', 'TBD', 'Floor refinishing and repairs'),
        ('Painter', 'Contractor', 'TBD', 'Interior/exterior painting'),
        ('Appliance Specialist', 'Specialist', 'TBD', 'Appliance repairs'),
        ('Chimney Sweep', 'Specialist', 'TBD', 'Chimney cleaning (CSIA certified preferred)'),
        ('Drainage Contractor', 'Specialist', 'TBD', 'Grading and drainage work'),
        ('Waterproofing Contractor', 'Specialist', 'TBD', 'Moisture prevention'),
    ]

    cursor.executemany("""
        INSERT INTO assignees (name, type, contact_info, notes)
        VALUES (?, ?, ?, ?);
    """, default_assignees)

    # Commit and close
    conn.commit()

    # Print summary
    print("✅ Database schema created successfully!")
    print(f"📍 Database location: {DB_PATH}")
    print("\n📊 Tables created:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    for table in cursor.fetchall():
        print(f"   - {table[0]}")

    print("\n👁️  Views created:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;")
    for view in cursor.fetchall():
        print(f"   - {view[0]}")

    print(f"\n👥 Seeded {len(default_assignees)} default assignees")

    conn.close()

    return DB_PATH


if __name__ == "__main__":
    print("=" * 60)
    print("Property Santa Ray - Database Initialization")
    print("=" * 60)
    print()

    db_path = init_database()

    print()
    print("=" * 60)
    print("✅ Initialization complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Run populate_tasks.py to load all 157 tasks")
    print("  2. Use query_tasks.py to explore the data")
    print("  3. Generate schedules with export_gantt.py and export_calendar.py")
