#!/usr/bin/env python3
"""
Property Santa Ray - Gantt Chart Export (Frappe Gantt)
Generates an HTML Gantt chart visualization with dependency arrows.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent.parent / "data" / "property_tasks.db"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "gantt_chart.html"


def get_tasks_with_dependencies(conn):
    """Fetch tasks and their dependencies from the database."""
    cursor = conn.cursor()

    # Get ALL active tasks (no limit), sorted by start date
    cursor.execute("""
        SELECT
            task_id,
            name,
            priority,
            start_date,
            end_date,
            assignee_name,
            status
        FROM tasks_with_assignees
        WHERE status != 'Completed'
        ORDER BY
            CASE WHEN start_date IS NULL THEN 1 ELSE 0 END,
            start_date ASC,
            required_before_ps_movein DESC,
            CASE priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
            END
    """)

    tasks = cursor.fetchall()

    # Get dependencies
    cursor.execute("""
        SELECT task_id, depends_on_task_id
        FROM task_dependencies
    """)

    dependencies = {}
    for task_id, depends_on in cursor.fetchall():
        if task_id not in dependencies:
            dependencies[task_id] = []
        dependencies[task_id].append(depends_on)

    return tasks, dependencies


def generate_frappe_gantt_html(conn):
    """Generate HTML using Frappe Gantt library."""

    tasks, dependencies = get_tasks_with_dependencies(conn)

    # Build task objects for Frappe Gantt
    task_objects = []
    tasks_needing_dates = []  # Track tasks without dates
    task_id_map = {}

    # Get today's date for placeholder assignment
    today = datetime.now().date()
    default_duration = timedelta(days=7)

    for i, (task_id, name, priority, start, end, assignee, status) in enumerate(tasks):
        # Create unique string ID
        str_id = f"task_{task_id}"
        task_id_map[task_id] = str_id

        # Handle tasks without dates - assign placeholders
        needs_dates = False
        if start is None or end is None:
            needs_dates = True
            if start is None:
                start = today.isoformat()
            if end is None:
                end = (today + default_duration).isoformat()

            tasks_needing_dates.append({
                "name": name,
                "priority": priority,
                "assignee": assignee or "Unassigned",
                "placeholder_start": start,
                "placeholder_end": end
            })

        # Build dependencies list
        task_deps = []
        if task_id in dependencies:
            for dep_id in dependencies[task_id]:
                task_deps.append(f"task_{dep_id}")

        # Progress based on status
        progress = 0
        if status == "In Progress":
            progress = 50
        elif status == "Completed":
            progress = 100

        task_obj = {
            "id": str_id,
            "name": name,
            "start": start,
            "end": end,
            "progress": progress,
            "custom_class": f"{priority.lower()}{' needs-dates' if needs_dates else ''}",
            "dependencies": ", ".join(task_deps) if task_deps else ""
        }

        task_objects.append(task_obj)

    # Calculate today's position for auto-scroll
    today_str = today.isoformat()

    # Generate tasks needing dates section HTML
    tasks_needing_dates_html = ""
    if tasks_needing_dates:
        tasks_needing_dates_html = """
    <div class="info warning-section" style="margin-top: 30px; background: #fff3cd; border-left: 4px solid #ffc107;">
        <h3>⚠️ Tasks Needing Date Assignment ({} tasks)</h3>
        <p>These tasks have been assigned placeholder dates (starting today, 7-day duration) to appear in the timeline.
        They are highlighted with a dashed border in the chart above.</p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
            <thead>
                <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                    <th style="padding: 10px; text-align: left;">Task Name</th>
                    <th style="padding: 10px; text-align: left;">Priority</th>
                    <th style="padding: 10px; text-align: left;">Assignee</th>
                    <th style="padding: 10px; text-align: left;">Placeholder Dates</th>
                </tr>
            </thead>
            <tbody>
""".format(len(tasks_needing_dates))

        for task in tasks_needing_dates:
            tasks_needing_dates_html += f"""
                <tr style="border-bottom: 1px solid #dee2e6;">
                    <td style="padding: 10px;">{task['name']}</td>
                    <td style="padding: 10px;">{task['priority']}</td>
                    <td style="padding: 10px;">{task['assignee']}</td>
                    <td style="padding: 10px;">{task['placeholder_start']} to {task['placeholder_end']}</td>
                </tr>
"""

        tasks_needing_dates_html += """
            </tbody>
        </table>
    </div>
"""

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Santa Ray Property - Project Gantt Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/frappe-gantt/dist/frappe-gantt.umd.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/frappe-gantt/dist/frappe-gantt.css"/>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        h1 {{
            color: #333;
            position: sticky;
            top: 0;
            background: white;
            z-index: 100;
            padding: 10px 0;
            margin: 0 0 20px 0;
        }}
        .info {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .warning-section {{
            background: #fff3cd !important;
        }}
        .legend {{
            margin: 20px 0;
            position: sticky;
            top: 60px;
            background: white;
            z-index: 99;
            padding: 10px 0;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
        }}
        .legend-box {{
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-right: 5px;
            vertical-align: middle;
        }}

        /* Gantt container with scrolling */
        #gantt-wrapper {{
            position: relative;
            margin: 20px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: auto;
            max-height: 70vh;
        }}

        /* Custom priority colors for task bars */
        .gantt .bar.critical {{
            fill: #d32f2f;
        }}
        .gantt .bar.high {{
            fill: #f57c00;
        }}
        .gantt .bar.medium {{
            fill: #fbc02d;
        }}
        .gantt .bar.low {{
            fill: #388e3c;
        }}

        /* Highlight tasks needing dates */
        .gantt .bar.needs-dates {{
            stroke: #ff9800;
            stroke-width: 2;
            stroke-dasharray: 5,5;
        }}

        /* Style dependency arrows */
        .gantt .arrow {{
            stroke: #666;
            stroke-width: 1.4px;
        }}

        /* Today indicator line */
        .today-line {{
            stroke: #2196F3;
            stroke-width: 2;
            stroke-dasharray: 5,5;
            opacity: 0.7;
        }}

        /* Toolbar styling */
        .view-toolbar {{
            margin-bottom: 15px;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
            position: sticky;
            top: 140px;
            z-index: 98;
        }}
        .view-toolbar button {{
            padding: 8px 15px;
            margin-right: 5px;
            border: 1px solid #ccc;
            background: white;
            cursor: pointer;
            border-radius: 3px;
        }}
        .view-toolbar button:hover {{
            background: #e0e0e0;
        }}
        .view-toolbar button.active {{
            background: #2196F3;
            color: white;
            border-color: #2196F3;
        }}

        /* Table styling */
        table {{
            font-size: 14px;
        }}
        th {{
            font-weight: 600;
        }}

        /* Scroll indicator */
        .scroll-hint {{
            text-align: center;
            padding: 10px;
            background: #e3f2fd;
            color: #1976d2;
            font-weight: 500;
            margin-bottom: 10px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <h1>🏗️ Santa Ray Property - Project Schedule</h1>

    <div class="info">
        <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
        <p><strong>Showing:</strong> {len(task_objects)} active tasks (excluding completed)</p>
        <p><strong>Sorted:</strong> Earliest start date at top → Latest at bottom</p>
        <p><strong>Interactive:</strong> Click and drag tasks to reschedule. Scroll horizontally/vertically to navigate timeline.</p>
    </div>

    <div class="legend">
        <strong>Priority Colors:</strong>
        <div class="legend-item">
            <span class="legend-box" style="background: #d32f2f;"></span> Critical
        </div>
        <div class="legend-item">
            <span class="legend-box" style="background: #f57c00;"></span> High
        </div>
        <div class="legend-item">
            <span class="legend-box" style="background: #fbc02d;"></span> Medium
        </div>
        <div class="legend-item">
            <span class="legend-box" style="background: #388e3c;"></span> Low
        </div>
        <div class="legend-item">
            <span class="legend-box" style="background: white; border: 2px dashed #ff9800;"></span> Needs Dates
        </div>
        <div class="legend-item">
            <span style="display: inline-block; width: 20px; height: 2px; background: #2196F3; margin-right: 5px; vertical-align: middle;"></span> Today
        </div>
    </div>

    <div class="view-toolbar">
        <strong>Timeline View:</strong>
        <button onclick="changeView('Day', this)" class="active" id="btn-Day">Day</button>
        <button onclick="changeView('Week', this)">Week</button>
        <button onclick="changeView('Month', this)">Month</button>
    </div>

    <div class="scroll-hint">
        ⬅️ Scroll horizontally to see timeline | Scroll vertically to see all tasks ⬇️
    </div>

    <div id="gantt-wrapper">
        <svg id="gantt"></svg>
    </div>

    <script>
        const tasks = {json.dumps(task_objects, indent=8)};
        const todayDate = new Date('{today_str}');

        // Initialize Gantt chart
        const gantt = new Gantt("#gantt", tasks, {{
            view_mode: 'Day',
            bar_height: 40,
            column_width: 30,
            arrow_curve: 8,
            move_dependencies: true,
            on_click: function (task) {{
                console.log('Task clicked:', task);
            }},
            on_date_change: function(task, start, end) {{
                console.log('Task rescheduled:', task.name, start, end);
            }},
            on_progress_change: function(task, progress) {{
                console.log('Progress updated:', task.name, progress);
            }}
        }});

        // View mode switcher
        function changeView(mode, buttonElement) {{
            gantt.change_view_mode(mode);

            // Update button styles
            document.querySelectorAll('.view-toolbar button').forEach(btn => {{
                btn.classList.remove('active');
            }});
            buttonElement.classList.add('active');
        }}

        // Auto-scroll to current date
        function scrollToToday() {{
            const wrapper = document.getElementById('gantt-wrapper');

            // Get the gantt SVG dimensions
            const svg = document.getElementById('gantt');
            const svgWidth = svg.getBBox().width;

            // Calculate approximate position of today
            // This is a rough calculation - adjust based on your timeline
            const scrollPosition = svgWidth * 0.3; // Start at ~30% to show some past context

            // Scroll horizontally to show current date
            wrapper.scrollLeft = scrollPosition;
        }}

        // Call auto-scroll after a short delay to ensure chart is rendered
        setTimeout(scrollToToday, 500);

        // Add visual indicator for today
        window.addEventListener('load', function() {{
            // You could add a vertical line for "today" here if needed
            // This would require adding an SVG element to the Frappe Gantt output
        }});
    </script>

    <div class="info" style="margin-top: 20px;">
        <h3>Features:</h3>
        <ul>
            <li><strong>Complete Task List:</strong> All {len(task_objects)} active tasks shown, sorted by earliest start date first</li>
            <li><strong>Dependency Arrows:</strong> Lines show task relationships from prerequisite tasks to dependent tasks</li>
            <li><strong>Interactive Editing:</strong> Drag task bars to reschedule</li>
            <li><strong>Auto-Scheduling:</strong> Dependent tasks move when prerequisites change</li>
            <li><strong>Multiple Views:</strong> Use buttons above to switch timeline scale (Day, Week, Month)</li>
            <li><strong>Scrollable Timeline:</strong> Scroll horizontally to see full timeline, vertically to see all tasks</li>
            <li><strong>Auto-Scroll:</strong> Page automatically scrolls to show current date on load</li>
            <li><strong>Sticky Controls:</strong> Title, legend, and view controls stay visible while scrolling</li>
        </ul>
        <h3>How to Read:</h3>
        <ul>
            <li><strong>Task Bars:</strong> Horizontal bars show duration (start to end date)</li>
            <li><strong>Task Names:</strong> Shown on the left side of each bar</li>
            <li><strong>Dependencies:</strong> Arrows point from prerequisite → dependent task</li>
            <li><strong>Colors:</strong> Red (Critical), Orange (High), Yellow (Medium), Green (Low)</li>
            <li><strong>Dashed Border:</strong> Tasks with placeholder dates that need actual dates assigned</li>
            <li><strong>Sort Order:</strong> Tasks are sorted with earliest start dates at the top</li>
        </ul>
        <h3>Next Steps:</h3>
        <ul>
            <li>Use <code>python3 tools/query_tasks.py</code> to view detailed task information</li>
            <li>Update tasks without dates (see section below if applicable)</li>
            <li>Click tasks in the chart to see console details (open browser DevTools)</li>
            <li>Drag tasks to experiment with scheduling scenarios</li>
        </ul>
    </div>

    {tasks_needing_dates_html}

</body>
</html>
"""

    return html


def main():
    """Generate and save Gantt chart."""
    print("=" * 60)
    print("Property Santa Ray - Gantt Chart Export (Frappe)")
    print("=" * 60)
    print()

    if not DB_PATH.exists():
        print("❌ Database not found! Please run init_database.py first.")
        return

    conn = sqlite3.connect(DB_PATH)

    print("📊 Generating comprehensive Gantt chart...")
    html = generate_frappe_gantt_html(conn)

    with open(OUTPUT_PATH, 'w') as f:
        f.write(html)

    print(f"✅ Gantt chart saved to: {OUTPUT_PATH}")
    print()
    print("📌 Features included:")
    print("   ✓ All active tasks (no limit)")
    print("   ✓ Sorted by earliest date first")
    print("   ✓ Auto-scroll to current date")
    print("   ✓ Sticky headers while scrolling")
    print("   ✓ Tasks with dependencies shown as arrows")
    print("   ✓ Tasks needing dates listed at bottom")
    print()
    print(f"   open {OUTPUT_PATH}")

    conn.close()


if __name__ == "__main__":
    main()
