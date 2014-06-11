Task Completion Notes
=====================

Author: Kevin Wurster - <kevin@skytruth.org>
[GitHub Repository](https://github.com/SkyTruth/CrowdProjects)

An explanation of why there are 5 different groups of tasks.


##### Applications #####
[Public]()
[First Internal](http://crowd.dev.skytruth.org/app/categorizer-pond-internal-tasks/)
[Final Internal](http://crowd.dev.skytruth.org/app/final-dartfrog-internal/)
[Sweeper Internal](http://crowd.dev.skytruth.org/app/sweeper_dartfrog/)
[Missing]()



Summary
-------
Each task has been completed at least once but may have been completed in multiple applications.  There is
known overlap between the public and first internal application.  In general it is best to interact with
the data through the utilities provided.  The `derivative-data/Compiled_Output.csv` file is the most reliable
dataset and has the complete record of each task's history including a final set of attributes.



Public Application
------------------
The files in `public` are directly exported from the application presented to the public.  This
application was never fully completed by the crowd, so when working with the tasks, understand that
only tasks from task.json were ONLY fully completed if there are >= 10 task runs in the task_run.json
file.



First Internal Application
--------------------------
The files in `first-internal` were from the very first DartFrog internal application.  The crowd
stalled on the public application around the 50% mark so almost 4000 tasks were pulled out of the
public app and and moved to an internal application with a lower redundancy.  The redundancy for
these tasks were set to 0 in the database behind the public app so they would never be shown to
the public, and to force the public progress bar to display the appropriate new number.



Final Internal Application
--------------------------
The files in `final-internal` are a combination of tasks from public and first-internal.  Through
examining the public and first internal tasks it became apparent that the set of tasks moved to the
first internal application was incorrect, so any task that was never fully completed in the public
or first internal application was extracted and placed into a new final internal application.



Sweeper Internal Application
----------------------------
The `dartfrog-task2shp.py` utility was used to convert each task.json and its matching task_run.json
file into a spatial format with a set of attributes explaining the crowd's selection and confidence
level.  If the crowd classified a pond as 'fracking' 8 times and 'other' 2 times, 80% of the crowd agreed.
These attributes and agreement levels were used to identify which ponds needed to be re-examined one
final time by SkyTruth employees.  A total of 1280 ponds were placed into a sweeper application to 
resolve any ambiguity based on the following criteria:  

For the public application, any pond with an agreement level < 80% and any pond that was confidently
classified as 'unknown'

For the internal applications, any pond with an agreement level < 66%.

For all applications, any pond where the crowd's response was evenly split across two or more choices.



Missing Internal Application
----------------------------
After the four applications detailed above were completed, the `dartfrog-taskCompiler.py` utility
was developed to stitch together a complete history for any given pond and to identify a final
pond classification.  Through developing this utility it was discovered that 221 tasks had never been
completed in any application.  These tasks were identified and completed in a final application.
