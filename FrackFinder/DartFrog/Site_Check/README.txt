This analysis was performed to determine which tasks should be moved to the
internal app.  The input task.json for the public app was taken and filtered to remove tasks that the public had completed.  The resulting candidate tasks 
were filtered against all the tasks that were completed in the public app to
leave a total of 2925 tasks that were never completd.  Running processor.py
from the current directory will grab all the necessary files and perform
all necessary filters.  It takes about 5 minutes to run.  The resulting
Final_Tasks.json contains all the tasks needed to load into a new app.

2/2/14
-Kevin Wurster
