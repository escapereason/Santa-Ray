# Santa Ray Property - Database-Driven Scheduling System

## 📋 Overview

This scheduling system provides comprehensive task management for the Santa Ray property renovation project. It replaces the previous priority-based organization with a robust SQLite database that enables proper dependency tracking, timeline analysis, and schedule visualization.

**System Status:** ✅ Fully Operational

---

## 🗂️ What Was Accomplished

### Phase 1: Document Reorganization ✅

Extracted large sections from `master-repair-plan.md` to improve maintainability:

1. **docs/project-phasing.md** - Stakeholder-based phasing strategy (Pre-PS, Post-PS, Pre-CG, Post-CG)
2. **docs/priority-breakdown.md** - Original 4-tier priority organization (Critical/High/Medium/Low)
3. **docs/labor-hours-analysis.md** - Comprehensive 1,000-1,350 hour analysis with detailed breakdowns

The master repair plan now references these documents, making it more concise and navigable.

### Phase 2: Database System ✅

Created a complete SQLite database system with:

**Database Schema:**
- **tasks** - Main tasks table (72+ tasks populated, framework for all 157)
- **assignees** - Contractors and DIY assignees (15 seeded)
- **tools** - Tool tracking (ready for population)
- **materials** - Material tracking (ready for population)
- **task_dependencies** - Self-referencing task relationships (11 dependencies created)
- **task_tools** - Many-to-many task-tool relationships
- **task_materials** - Many-to-many task-material relationships

**Views for Common Queries:**
- `tasks_with_assignees` - Tasks joined with assignee information
- `critical_path_tasks` - Tasks required before PS move-in
- `task_summary` - Quick overview with costs and hours

### Phase 3: Management Tools ✅

Complete suite of tools for project management:

**Daily Use:**
1. **dashboard.html** - Interactive task dashboard (your daily go-to!)
2. **tools/assign_dates.py** - Smart date scheduler (setup and rescheduling)

**Integration & Analysis:**
3. **tools/export_calendar.py** - Export to Google Calendar (iCal format)
4. **tools/query_tasks.py** - Interactive database query tool
5. **tools/export_gantt.py** - Generate full HTML Gantt chart

**Database Management:**
6. **tools/init_database.py** - Initialize database schema
7. **tools/populate_tasks.py** - Populate with project tasks

All data files are stored in the `data/` folder for clean organization.

---

## 🚀 Quick Start

### Initial Setup (One Time)

```bash
cd /Users/paulorozco/Documents/Github/property-santaray/planning/schedule

# 1. Assign dates to all tasks (CRITICAL FIRST STEP)
python3 tools/assign_dates.py

# This will ask you for:
#   - PS move-in deadline
#   - Chris move-in deadline
#   - Project start date
# Then it will automatically assign realistic dates to all 74 tasks!

# 2. Open your dashboard
open dashboard.html
# This is now your daily task manager - bookmark it!

# 3. Export to Google Calendar (optional - for mobile access)
python3 tools/export_calendar.py
# Then import the .ics file to Google Calendar
```

### Daily Workflow

**Your go-to command:**
```bash
open dashboard.html
```

That's it! The dashboard shows you:
- ✅ What's coming up in the next 7/14/30 days
- ✅ Tasks sorted by date
- ✅ Color-coded by priority
- ✅ Click to mark tasks complete
- ✅ Export to Google Calendar

**When you need to reschedule:**
1. Run `python3 tools/assign_dates.py` again with new dates
2. Refresh your dashboard
3. Re-export to Google Calendar if needed

### Files Generated

- `data/property_tasks.db` - SQLite database (the single source of truth)
- `data/tasks.json` - Task data for dashboard (auto-generated)
- `dashboard.html` - Your daily task dashboard (just open it!)
- `data/gantt_chart.html` - Full Gantt chart timeline (for planning)
- `data/santa_ray_tasks.ics` - Calendar import file for Google Calendar

---

## 📊 Current Database Status

### Tasks Populated: 72 of 157

**By Category:**
- Property Transfer Compliance: 25 tasks
- Electrical (Critical + Upgrades): 13 tasks
- Fungus Remediation: 21 tasks
- HVAC/Plumbing/Safety: 13 tasks

**By Priority:**
- Critical: 61 tasks (85%)
- High: 6 tasks (8%)
- Medium: 2 tasks (3%)
- Low: 3 tasks (4%)

**By Status:**
- Completed: 4 tasks (fungus debris removal, front porch, handrail, rear porch)
- Not Started: 68 tasks

### Task Dependencies Created: 11

Critical dependencies established:
- Sewer work must complete before sidewalk
- Form installation before concrete pour
- Cure times before form removal
- Smaller studio sequential phases (7 dependencies)

---

## 🎯 Sample Schedule & Recommendations

### Critical Path (Before PS Move-In)

**Priority 1: Property Transfer Compliance (5 days)**
- Sewer lateral replacement (2 days) - **BLOCKS PROPERTY TRANSFER**
- Sidewalk ADA compliance (3 days) - **BLOCKS PROPERTY TRANSFER**
- Estimated cost: $12,700
- Must complete before close of escrow

**Priority 2: DIY Safety Tasks (2-3 days)**
- Electrical safety (cover plates, GFCI, exposed wiring)
- CO detector installation
- Dryer vent repair
- Can run parallel with property transfer work
- Estimated cost: $60-165 (materials only)

**Priority 3: Contractor Safety Tasks (1 day)**
- Electrical panel repairs
- Kitchen sink leak
- Loose toilet
- Estimated cost: $450-850
- Schedule immediately after property transfer

### High Priority (Weeks 2-12)

**Fungus Remediation (10-14 weeks)**
- Largest single category - **700 hours recommended**
- Includes permits (10-15 days before work can begin)
- Weather-dependent exterior work
- Must include TIM-BOR treatment between demo and rebuild
- Estimated cost: $52,367 (incl. permits)

**Strategy:**
- Submit permits DAY 1 of project
- Start with interior work during rainy weather
- Schedule exterior work for dry periods
- 2-person crew recommended for efficiency

### Medium Priority (Months 2-3)

**Interior Functionality**
- Appliance repairs (oven, cooktop, exhaust fan)
- Chimney cleaning
- Door and window repairs
- Can overlap with later stages of fungus work

**Drainage & Exterior**
- Negative grading correction (critical for preventing future fungus)
- DIY exterior repairs
- Should complete before rainy season

### Low Priority (Months 4+)

**Cosmetic Improvements**
- Floor refinishing (requires 7-10 calendar days due to cure times)
- Interior painting
- Window screens
- Can be deferred if budget/timeline requires

**Electrical Upgrades**
- Ungrounded receptacle upgrades
- AFCI protection
- Additional circuits
- Requires separate permits (10-15 day lead time)

---

## 📈 Recommended Project Timeline

### Month 1: Critical Safety & Compliance
- **Days 1-5:** Property transfer (sewer + sidewalk)
- **Days 1-3:** DIY safety tasks (parallel)
- **Day 6:** Submit fungus remediation permits
- **Days 6-15:** Contractor safety repairs + permit processing
- **Days 16-30:** Begin fungus work (interior first)

### Months 2-4: Major Fungus Remediation
- Continue fungus work across 13+ locations
- Schedule weather-dependent exterior work strategically
- Begin overlap with HVAC/plumbing infrastructure work in month 3

### Months 4-5: Functionality & Infrastructure
- Complete remaining HVAC/plumbing work
- Interior functionality improvements
- Drainage corrections

### Month 6+: Cosmetic & Upgrades (As Budget Allows)
- Floor refinishing
- Painting
- Electrical upgrades
- Window screens

**Total Realistic Timeline: 14-20 weeks (3.5-5 months)**

---

## 🔧 Using the Management Tools

### 1. Task Dashboard (`dashboard.html`) ⭐ PRIMARY TOOL

**Your daily go-to for task management.**

Open it: `open dashboard.html`

Features:
- 📅 Calendar-style timeline view of all tasks
- 🔍 Filter by time range (Next 7/14/30 days, or All)
- ✅ Click to mark tasks complete
- 📊 Live statistics (upcoming, this week, critical, completed)
- 🎨 Color-coded by priority
- 📥 One-click export to Google Calendar

**Perfect for:**
- Checking what's next each day
- Marking tasks done
- Seeing your progress
- Planning your week

### 2. Smart Date Scheduler (`assign_dates.py`) ⭐ SETUP TOOL

**Assigns realistic dates to all tasks based on deadlines and dependencies.**

Run it: `python3 tools/assign_dates.py`

You'll be asked for:
1. PS move-in deadline
2. Chris move-in deadline
3. Project start date (defaults to today)

The tool then:
- ✅ Respects task dependencies (e.g., sewer before sidewalk)
- ✅ Schedules based on priority (Critical first)
- ✅ Balances assignee workload
- ✅ Accounts for labor hours and weekends
- ✅ Works backward from deadlines
- ✅ Warns if deadlines can't be met

**Run this whenever:**
- First time setting up
- Deadlines change
- You want to reschedule the entire project

### 3. Calendar Export (`export_calendar.py`)

**Exports tasks to Google Calendar for mobile access.**

Basic usage: `python3 tools/export_calendar.py`

Filter to upcoming tasks only: `python3 tools/export_calendar.py 30`

Features:
- Exports to `.ics` format (universal calendar format)
- All non-completed tasks included
- Priority, assignee, costs in description
- Can filter to next N days for cleaner calendar

**How to import to Google Calendar:**
1. Create a new calendar called "Santa Ray Repairs"
2. Settings → Import & Export → Import
3. Choose `data/santa_ray_tasks.ics`
4. Select "Santa Ray Repairs" calendar
5. Done! Tasks now on your phone

### 4. Query Tool (`query_tasks.py`)

**Interactive database query tool for detailed analysis.**

Run it: `python3 tools/query_tasks.py`

Menu options:
1. View tasks by priority
2. View critical path tasks (required before PS move-in)
3. View tasks by assignee
4. View project summary (costs, hours, status breakdown)
5. View task dependencies

**Perfect for:**
- Analyzing contractor workload
- Checking critical path tasks
- Reviewing project costs
- Understanding dependencies

### 5. Gantt Chart Generator (`export_gantt.py`)

**Creates interactive Gantt chart with full timeline.**

Run it: `python3 tools/export_gantt.py`

Opens: `data/gantt_chart.html`

Features:
- Full project timeline visualization
- Drag-and-drop task rescheduling
- Dependency arrows
- Multiple view modes (Day/Week/Month)
- Shows all active tasks

**Perfect for:**
- High-level project planning
- Presenting to contractors
- Understanding the full timeline
- Spotting scheduling conflicts

---

## 📝 Next Steps

### Immediate Actions (Do These Now!)

1. **Assign dates to all tasks**: `python3 tools/assign_dates.py`
2. **Open your dashboard**: `open dashboard.html` and bookmark it
3. **Export to Google Calendar** (optional): `python3 tools/export_calendar.py`

That's it! You're now ready to manage your project daily.

### As You Work

1. **Daily**: Open `dashboard.html` to see what's next
2. **Weekly**: Review upcoming tasks for the next 7-14 days
3. **When completing tasks**: Click "Mark Done" in dashboard
4. **When dates change**: Re-run `assign_dates.py` with new deadlines
5. **When sharing with contractors**: Export Gantt chart or calendar

### Optional Enhancements

1. **Complete task population** - Add remaining tasks from contractor/DIY folders
2. **Add more dependencies** - Establish additional task relationships
3. **Populate tools/materials** - Track specific tools and materials
4. **Track actuals** - Record actual hours and costs as work completes

---

## 🎓 Database Schema Reference

### Main Fields in `tasks` Table

- **Planning**: name, description, location, priority, status
- **Scheduling**: required_before_ps_movein, required_before_chris_movein, start_date, end_date
- **Resources**: assignee_id, labor_hours_min/max, cost_estimate_min/max
- **Technical**: technical_description, source_file, source_section
- **Tracking**: created_at, updated_at, completion_date

### Key Relationships

- **Tasks → Assignees**: One assignee per task
- **Tasks → Tools**: Many-to-many (a task can use multiple tools)
- **Tasks → Materials**: Many-to-many (a task can use multiple materials)
- **Tasks → Tasks**: Self-referencing dependencies (task A depends on task B)

---

## 💡 Design Philosophy

This system follows the **beautiful simplicity** principle:

1. **SQLite** - Simple, single-file database (no server required)
2. **Python scripts** - Clean, readable code with clear purposes
3. **Standard formats** - HTML for Gantt, iCal for calendar (widely compatible)
4. **Extensible** - Easy to add more tasks, tools, materials
5. **Version controlled** - Everything is files that can be tracked in git

---

## 🔍 Technical Notes

### Database Location
`/Users/paulorozco/Documents/Github/property-santaray/planning/schedule/data/property_tasks.db`

### Python Requirements
- Python 3.x (system python works)
- sqlite3 (built into Python)
- tabulate (for query_tasks.py - install with `pip3 install tabulate` if needed)

### Modifying the Database

To add/update tasks programmatically:
```python
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "data" / "property_tasks.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert new task
cursor.execute("""
    INSERT INTO tasks (name, description, priority)
    VALUES (?, ?, ?)
""", ("New Task", "Description", "Medium"))

conn.commit()
conn.close()
```

To query directly:
```bash
cd /Users/paulorozco/Documents/Github/property-santaray/planning/schedule
sqlite3 data/property_tasks.db
.tables
SELECT * FROM tasks WHERE priority = 'Critical' LIMIT 5;
.quit
```

---

## 📧 Support & Documentation

- **Master Repair Plan**: `../master-repair-plan.md`
- **Detailed Cost Breakdown**: `../detailed-cost-breakdown.md`
- **Contractor Plans**: `../contractor/*.md`
- **DIY Guides**: `../diy/*.md`

All scheduling documents are now centralized in this `schedule/` folder for better organization.

---

## ⚡ Quick Reference

### Most Common Commands

```bash
# Daily task check
open dashboard.html

# Reschedule everything
python3 tools/assign_dates.py

# Export to Google Calendar
python3 tools/export_calendar.py

# Detailed analysis
python3 tools/query_tasks.py

# Full project timeline
python3 tools/export_gantt.py
```

### File Locations

| File | Purpose | How to Use |
|------|---------|------------|
| `dashboard.html` | Daily task manager | Open in browser, bookmark it |
| `data/property_tasks.db` | Master database | Single source of truth |
| `data/tasks.json` | Dashboard data | Auto-generated |
| `data/gantt_chart.html` | Full timeline | For planning |
| `data/santa_ray_tasks.ics` | Calendar export | Import to Google Calendar |

### Workflow Summary

1. **Setup (one time)**: Run `assign_dates.py` → Enter deadlines
2. **Daily**: Open `dashboard.html` → Check what's next → Mark tasks done
3. **Mobile**: Export to Google Calendar for phone access
4. **Reschedule**: Re-run `assign_dates.py` when dates change

---

**Last Updated:** November 8, 2025
**System Version:** 2.0 (Dashboard Release)
**Status:** Production Ready

**Created by:** Claude Code
**For:** Paul & Sarah Orozco - 757 Santa Ray Avenue Property Renovation
