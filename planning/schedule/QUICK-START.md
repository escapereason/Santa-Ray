# Santa Ray Property - Quick Start Guide

## 🎯 Your Simple Task Management System

This is your daily task management system. No complexity, just simple tools that work.

---

## ⚡ First Time Setup (5 minutes)

```bash
cd /Users/paulorozco/Documents/Github/property-santaray/planning/schedule

# 1. Assign dates to all tasks
python3 tools/assign_dates.py
```

You'll be asked three questions:
1. **When does PS need to move in?** (YYYY-MM-DD, e.g., 2026-02-01)
2. **When does Chris need to move in?** (YYYY-MM-DD, e.g., 2026-06-01)
3. **When can work start?** (Press Enter for today)

The tool then assigns realistic dates to ALL 74 tasks automatically. Done!

```bash
# 2. Open your dashboard
open dashboard.html
```

Bookmark this page - it's your daily task manager!

```bash
# 3. (Optional) Export to Google Calendar
python3 tools/export_calendar.py
```

Then import `data/santa_ray_tasks.ics` to Google Calendar to see tasks on your phone.

---

## 📅 Daily Use

**What you do every day:**

```bash
open dashboard.html
```

That's it! The dashboard shows:
- ✅ What's coming up (next 7/14/30 days)
- ✅ Tasks sorted by date
- ✅ Color-coded by priority (red=critical, orange=high, yellow=medium, green=low)
- ✅ Click tasks to mark them complete

**Filters:**
- "Next 7 Days" - See just this week
- "Next 14 Days" - See the next two weeks
- "Next 30 Days" - See the month ahead
- "All Tasks" - See everything

---

## 🔄 When You Need to Reschedule

Deadlines changed? No problem:

```bash
python3 tools/assign_dates.py
```

Enter your new deadlines. All tasks will be rescheduled automatically.

Then refresh your dashboard - done!

---

## 📱 Google Calendar Integration

**Why use it:** See tasks on your phone, get notifications

**How to set up:**

1. Export tasks:
```bash
python3 tools/export_calendar.py
```

2. In Google Calendar:
   - Click "+" next to "Other calendars"
   - Select "Create new calendar"
   - Name it "Santa Ray Repairs"
   - Click "+" again → "Import"
   - Choose `data/santa_ray_tasks.ics`
   - Select "Santa Ray Repairs" calendar
   - Click Import

3. Done! Tasks are now on your phone.

**To update calendar when dates change:**
- Re-run `python3 tools/export_calendar.py`
- Import the new .ics file (it will update the tasks)

**Pro tip:** Export only upcoming tasks to avoid calendar clutter:
```bash
python3 tools/export_calendar.py 30  # Next 30 days only
```

---

## 🛠️ Other Useful Tools

### See detailed task info
```bash
python3 tools/query_tasks.py
```

Interactive menu shows:
- Tasks by priority
- Tasks by assignee
- Project summary (costs, hours)
- Task dependencies

### See full project timeline
```bash
python3 tools/export_gantt.py
```

Then open `data/gantt_chart.html` - interactive Gantt chart with full timeline.

---

## 💡 Common Scenarios

### "What do I need to do this week?"
```bash
open dashboard.html
```
Click "Next 7 Days" filter.

### "What's the critical stuff?"
Dashboard shows it with red borders. Or use query tool:
```bash
python3 tools/query_tasks.py
# Select option 2: View critical path tasks
```

### "I finished a task!"
Open dashboard, click "Mark Done" on the task.

### "Contractor asks for their task list"
```bash
python3 tools/query_tasks.py
# Select option 3: View tasks by assignee
```

### "I need to see the big picture"
```bash
python3 tools/export_gantt.py
open data/gantt_chart.html
```

### "Deadlines changed!"
```bash
python3 tools/assign_dates.py
# Enter new deadlines
# All tasks automatically rescheduled
```

---

## 📂 Where Are My Files?

| File | What It Is | What You Do |
|------|-----------|-------------|
| `dashboard.html` | Daily task dashboard | Open it, bookmark it, use it daily |
| `data/property_tasks.db` | The database | This is where everything is stored |
| `data/tasks.json` | Dashboard data | Auto-created, don't edit |
| `data/gantt_chart.html` | Full timeline | Open for big picture view |
| `data/santa_ray_tasks.ics` | Calendar file | Import to Google Calendar |

---

## 🆘 Troubleshooting

### Dashboard shows "No tasks found"
Run this first:
```bash
python3 tools/assign_dates.py
```

### Tasks don't have dates
Run this:
```bash
python3 tools/assign_dates.py
```

### Want to see tasks on phone
Export to Google Calendar:
```bash
python3 tools/export_calendar.py
# Then import .ics file to Google Calendar
```

### Made a mistake, want to start over
```bash
python3 tools/assign_dates.py
# Enter correct deadlines, it will reschedule everything
```

---

## ✅ That's It!

**Your daily workflow:**
1. Open `dashboard.html`
2. Check what's coming up
3. Mark tasks done as you complete them
4. Repeat tomorrow

**When deadlines change:**
1. Run `python3 tools/assign_dates.py`
2. Enter new dates
3. Refresh dashboard

Simple. Effective. Done.

---

**Questions?** Check `README.md` for full documentation.

**Last Updated:** November 8, 2025
