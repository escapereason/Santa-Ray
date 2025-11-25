**high level desire**

I want to start a schedule system to track what is going on. I want to use a database to track this including every line item that we are working on. Use every item in the contractor and diy folders. Double check that it includes everything from the master-repair-plan.md. 

**main database**

I want the main task database to include items such as
- item name
- further description of what is wrong and the work that will need to be done. 
- location
- task dependency (self-referencing - itemizing what task needs to be done before this one)
- required before PS move-in (binary)
- required before Chris move-in (binary)
- assignee (reference key to assignee)
- start date (date)
- end date (date)
- labor hour estimate (integer)
- tools used (set of reference keys)
- materials used (set of reference keys)
- cost estimate (integer)
- technical description of how to perform the work (string)
- link to the file and section for hte specific action within the @planning/ folder 

**reference tables**

Here are some other basic tables to make for the above one to reference.
- Make another table for the assignees. 
- make another table for tools
- make another table for materials

**additional schedule features**
Make or suggest a way to visualize the schedule like a gantt chart and another that can use it like a calendar event system. I think that'd be cool. Ideally it can integrate with google calendar. 

**now the main task**

Do a deep analysis of all the tasks and organize a sample schedule for me to identify what should done when. Use the master repair document to track what has already been completed.  