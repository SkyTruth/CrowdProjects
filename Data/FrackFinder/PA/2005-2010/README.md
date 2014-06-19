SkyTruth FrackFinder PA 2005-2010 Methodology
=============================================

Author: Kevin Wurster - <kevin@skytruth.org>

An explanation of how data flowed from application to application



Source Data Procurement
=======================

##### General Description #####

1. Locate source data
2. Scrape and process source data
3. Load tasks
4. Classify


1. Locate Source Data
---------------------

**TODO: Explain**


2. Scrape and Process Source Data
---------------------------------

**TODO: Explain**



Tadpole Workflow
================

##### General Description #####

1. Generate tasks and load tasks
2. Classify
3. Export data
4. Transform data
5. Sample Data


1. Generate and Load Tasks
--------------------------

**TODO: Explain**


2. Classify
-----------

**TODO: Explain**


3. Export Data
--------------

All tasks were completed by the public in a single applications.  The tasks and task runs
were downloaded and stored in the following locations:

>       Transformations_and_QAQC/Tadpole/tasks/task.json
>       Transformations_and_QAQC/Tadpole/tasks/task_run.json


4. Transform Data
-----------------

The data needs to be converted to a spatial format in order to perform analyses and better
understand how one feature relates to another.  The `task2shp.py` utility performs all
necessary conversions and task/task run aggregation.  In general, the output is a an ESRI
Shapefile with one feature per task and a set of attributes collected from the associated
task runs.  Transformations were performed with the following command:

>       ./Transformations_and_QAQC/Tadpole/bin/task2shp.py Transformations_and_QAQC/Tadpole/tasks/task.json Transformations_and_QAQC/Tadpole/tasks/task_run.json Transformations_and_QAQC/Tadpole/transform/stats/tadpole-stats.shp

The resulting file contains the following fields:

>       id         ->  Task's ID as assigned by PyBossa
>       site_id    ->  SkyTruth assigned unique site ID
>       wms_url    ->  Link to image scene
>       county     ->  County name
>       year       ->  Imagery year
>       location   ->  Generated unique ID (lat + long + year)
>       n_unk_res  ->  Number of task runs where task was classified as 'unknown'
>       n_nop_res  ->  Number of task runs where task was classified as 'nopad'
>       n_eqp_res  ->  Number of task runs where task was classified as 'unknown'
>       n_emp_res  ->  Number of task runs where task was classified as 'empty'
>       n_tot_res  ->  Number of times this task was completed
>       crowd_sel  ->  Classification with the highest number of selections or class1|class2|etc. for ties
>       qaqc       ->  Used in the manual QAQC process
>       p_crd_a    ->  Percent of the crowd's responses that matched the crowd_sel field
>       p_s_crd_a  ->  Percentages for crowd_sel ties percent1|percent2|etc. or NULL if there was no tie


5. Sample Data
--------------

A random sample of 100 sites was taken from each year (2005, 2008, 2010) and manually classified
by an operator using `QGIS 2.2` and the same imagery displayed in the PyBossa application.  There
is a bug in QGIS's random sampling tool that ignores any filters applied to the input datasource
so the filters must be applied and then the data must be exported to a new file, from which a
random sample can be selected.  Queries and exports were performed in QGIS.  All queries were
performed on Tadpole stats layer:

>       Transformations_and_QAQC/Tadpole/transform/stats/tadpole-stats.shp
>           "year" = 2005  ->  Transformations_and_QAQC/Tadpole/sampling/queries/tadpole-query-2005.shp
>           "year" = 2008  ->  Transformations_and_QAQC/Tadpole/sampling/queries/tadpole-query-2008.shp 
>           "year" = 2010  ->  Transformations_and_QAQC/Tadpole/sampling/queries/tadpole-query-2010.shp

The random samples were exported to the sampling directory and examined in place:

>       Transformations_and_QAQC/Tadpole/sampling/2005/tadpole-2005-sample-100.shp
>       Transformations_and_QAQC/Tadpole/sampling/2008/tadpole-2008-sample-100.shp
>       Transformations_and_QAQC/Tadpole/sampling/2010/tadpole-2010-sample-100.shp

### 2005 Results ###

2 disagreements were found, one of which was caused by the crowd preferring two
classifications an equal number of times, and the other was caused by ambiguity in the imagery.

### 2008 Results ###

4 disagreements were found, which were all caused by ambiguity in the imagery.

### 2010 Results ###

6 disagreements were found, about half of which were caused by the crowd preferring two
classifications an equal number of times.  The other half were related to empty vs. equipment vs.
nopad ambiguity caused by compressed NAIP used in the application.



MoorFrog Workflow
=================

##### General Description #####

1. Identify input tasks
2. Generate and load tasks
3. Classify
4. Export data
5. Transform data
6. Sample Data


1. Identify Input Tasks
-----------------------

**TODO: Explain**


2. Generate and Load Tasks
--------------------------

**TODO: Explain**


3. Classify
-----------

**TODO: Explain**


4. Export Data
--------------

All tasks were completed by the public in a single applications.  The tasks and task runs
were downloaded and stored in the following locations:

>       Transformations_and_QAQC/MoorFrog/tasks/task.json
>       Transformations_and_QAQC/MoorFrog/tasks/task_run.json


5. Transform Data
-----------------

MoorFrog's `task2shp.py` utility produces all necessary derivative datasets and aggregations
with a single command.  The MoorFrog tasks have a well pad point, bounding box, and task runs
containing the user's clicks.  The output files include the following layers: bounding boxes,
pond clicks, and well pad points.  The following command produces all data:

>       ./Transformations_and_QAQC/MoorFrog/bin/task2shp.py Transformations_and_QAQC/MoorFrog/tasks/task.json Transformations_and_QAQC/MoorFrog/tasks/task_run.json Transformations_and_QAQC/MoorFrog/transform/

Output fields: `Transformations_and_QAQC/MoorFrog/transform/MoorFrog-bbox.shp`

>       id        ->  Task's ID as assigned by PyBossa  
>       site_id   ->  SkyTruth assigned unique site ID
>       location  ->  Generated primary key (lat + long + year)
>       wms_url   ->  Link to imagery required for this task
>       county    ->  County name
>       year      ->  Imagery year
>       qaqc      ->  Used in manual QAQC

Output fields: `Transformations_and_QAQC/MoorFrog/transform/MoorFrog-clicks.shp`

>       id       ->  Task's ID as assigned by PyBossa
>       task_id  ->  PyBossa assigned task_id from task_run.json (matches task.json['id'])
>       year     ->  Imagery year
>       qaqc     ->  Used in manual QAQC

Output fields: `Transformations_and_QAQC/MoorFrog/transform/MoorFrog-wellpads.shp`

>       id        ->  Task's ID as assigned by PyBossa  
>       site_id   ->  SkyTruth assigned unique site ID
>       location  ->  Generated primary key (lat + long + year)
>       wms_url   ->  Link to imagery required for this task
>       county    ->  County name
>       year      ->  Imagery year
>       qaqc      ->  Used in manual QAQC


6. Sample Data
--------------

When examining a MoorFrog task, the user was asked to click on all the ponds located within
the bounding box.  In order to determine how well the crowd performed a random sample of
100 bounding boxes per year (2005, 2008, 2010) were extracted and manually examined by an
operator who was looking for missed ponds.  Some user's clicked outside of the bounding box,
which was not a part of the instructions so these clicks were thrown away. Any pond (fracking
or otherwise) within the bounding box that was not clicked on at least was once considered
omitted.  The operator created a new Shapefile containing one point per missed pond.

The QGIS bug explained and addressed in the `Tadpole Sample Data` section was accounted for
when creating sample tasks:

>       Transformations_and_QAQC/MoorFrog/transform/MoorFrog-bbox.shp
>           "year" = 2005  ->  Transformations_and_QAQC/MoorFrog/sampling/queries/bbox-2005-query.shp
>           "year" = 2008  ->  Transformations_and_QAQC/MoorFrog/sampling/queries/bbox-2008-query.shp
>           "year" = 2010  ->  Transformations_and_QAQC/MoorFrog/sampling/queries/bbox-2010-query.shp

The random samples and missed ponds are located in the sampling directory and were examined
in place:

>       Transformations_and_QAQC/MoorFrog/sampling/2005/moorfrog-2005-sample-100.shp
>       Transformations_and_QAQC/MoorFrog/sampling/2005/moorfrog-2005-missed-ponds.shp
>       Transformations_and_QAQC/MoorFrog/sampling/2008/moorfrog-2008-sample-100.shp
>       Transformations_and_QAQC/MoorFrog/sampling/2008/moorfrog-2008-missed-ponds.shp
>       Transformations_and_QAQC/MoorFrog/sampling/2010/moorfrog-2010-sample-100.shp
>       Transformations_and_QAQC/MoorFrog/sampling/2010/moorfrog-2010-missed-ponds.shp

### 2005 Results ###

2005 - 18 omitted ponds - None appear to be fracking related

### 2008 Results ###

2008 - 19 omitted ponds - None appear to be fracking related

### 2010 Results ###

2010 - 6 omitted ponds - 2 appear to be fracking related



DartFrog Workflow
=================

##### General Description #####

1. Identify input tasks
2. Generate and load tasks
3. Classify
4. Export data
5. Transform data
6. Sample Data


1. Identify Input Tasks
-----------------------

**TODO: Explain**


2. Generate and Load Tasks
--------------------------

**TODO: Explain**


3. Classify
-----------

### Summary ###

Each task has been completed at least once but may have been completed in multiple applications.  There is
known overlap between the public and first internal application.  In general it is best to interact with
the data through the utilities provided.  The `derivative-data/Compiled_Output.csv` file is the most reliable
dataset and has the complete record of each task's history including a final set of attributes.

### Public Application ###

The files in `public` are directly exported from the application presented to the public.  This
application was never fully completed by the crowd, so when working with the tasks, understand that
only tasks from task.json were ONLY fully completed if there are >= 10 task runs in the task_run.json
file.

### First Internal Application ###

The files in `first-internal` were from the very first DartFrog internal application.  The crowd
stalled on the public application around the 50% mark so almost 4000 tasks were pulled out of the
public app and and moved to an internal application with a lower redundancy.  The redundancy for
these tasks were set to 0 in the database behind the public app so they would never be shown to
the public, and to force the public progress bar to display the appropriate new number.

### Final Internal Application ###

The files in `final-internal` are a combination of tasks from public and first-internal.  Through
examining the public and first internal tasks it became apparent that the set of tasks moved to the
first internal application was incorrect, so any task that was never fully completed in the public
or first internal application was extracted and placed into a new final internal application.

### Sweeper Internal Application ###

The `task2shp.py` utility was used to convert each task.json and its matching task_run.json
file into a spatial format with a set of attributes explaining the crowd's selection and confidence
level.  If the crowd classified a pond as 'fracking' 8 times and 'other' 2 times, 80% of the crowd agreed.
These attributes and agreement levels were used to identify which ponds needed to be re-examined one
final time by SkyTruth employees.  A total of 1280 ponds were placed into a sweeper application to 
resolve any ambiguity based on the following criteria:  

For the public application, any pond with an agreement level < 80% and any pond that was confidently
classified as 'unknown'

For the internal applications, any pond with an agreement level < 66%.

For all applications, any pond where the crowd's response was evenly split across two or more choices.

### Missing Internal Application ###

After the four applications detailed above were completed, the `dartfrog-taskCompiler.py` utility
was developed to stitch together a complete history for any given pond and to identify a final
pond classification.  Through developing this utility it was discovered that 221 tasks had never been
completed in any application.  These tasks were identified and completed in a final application.


4. Export Data
--------------

Each DartFrog application's tasks are stored separately in the following locations:

>       Transformations_and_QAQC/DartFrog/tasks/public/task.json
>       Transformations_and_QAQC/DartFrog/tasks/public/task_run.json
>       Transformations_and_QAQC/DartFrog/tasks/first-internal/task.json
>       Transformations_and_QAQC/DartFrog/tasks/first-internal/task_run.json
>       Transformations_and_QAQC/DartFrog/tasks/final-internal/task.json
>       Transformations_and_QAQC/DartFrog/tasks/final-internal/task_run.json
>       Transformations_and_QAQC/DartFrog/tasks/sweeper-internal/task.json
>       Transformations_and_QAQC/DartFrog/tasks/sweeper-internal/task_run.json
>       Transformations_and_QAQC/DartFrog/tasks/missing/task.json
>       Transformations_and_QAQC/DartFrog/tasks/missing/task_run.json


5. Transform Data
-----------------

As with the previous applications, a `task2shp.py` utility exists to aggregate information
into a single spatial file.  The commands used are as follows:

>       ./Transformations_and_QAQC/DartFrog/bin/task2shp.py Transformations_and_QAQC/DartFrog/tasks/public/task.json Transformations_and_QAQC/DartFrog/tasks/public/task_run.json Transformations_and_QAQC/DartFrog/transform/public/stats/dartfrog-public-stats.shp
>       ./Transformations_and_QAQC/DartFrog/bin/task2shp.py Transformations_and_QAQC/DartFrog/tasks/first-internal/task.json Transformations_and_QAQC/DartFrog/tasks/first-internal/task_run.json Transformations_and_QAQC/DartFrog/transform/first-internal/stats/dartfrog-first-internal-stats.shp
>       ./Transformations_and_QAQC/DartFrog/bin/task2shp.py Transformations_and_QAQC/DartFrog/tasks/final-internal/task.json Transformations_and_QAQC/DartFrog/tasks/final-internal/task_run.json Transformations_and_QAQC/DartFrog/transform/final-internal/stats/dartfrog-final-internal-stats.shp
>       ./Transformations_and_QAQC/DartFrog/bin/task2shp.py Transformations_and_QAQC/DartFrog/tasks/sweeper-internal/task.json Transformations_and_QAQC/DartFrog/tasks/sweeper-internal/task_run.json Transformations_and_QAQC/DartFrog/transform/sweeper-internal/stats/dartfrog-sweeper-internal-stats.shp
>       ./Transformations_and_QAQC/DartFrog/bin/task2shp.py Transformations_and_QAQC/DartFrog/tasks/missing/task.json Transformations_and_QAQC/DartFrog/tasks/missing/task_run.json Transformations_and_QAQC/DartFrog/transform/missing/stats/dartfrog-missing-stats.shp

The output file fields are as follows:

>       id         ->  Task's ID as assigned by PyBossa
>       site_id    ->  SkyTruth assigned unique site ID
>       wms_url    ->  Link to image scene
>       county     ->  County name
>       year       ->  Imagery year
>       location   ->  Generated unique ID (lat + long + year)
>       n_unk_res  ->  Number of task runs where task was classified as 'unknown'
>       n_frk_res  ->  Number of task runs where task was classified as 'fracking'
>       n_oth_res  ->  Number of task runs where task was classified as 'other'
>       n_tot_res  ->  Number of times this task was completed
>       crowd_sel  ->  Classification with the highest number of selections or class1|class2|etc. for ties
>       qaqc       ->  Used in the manual QAQC process
>       p_crd_a    ->  Percent of the crowd's responses that matched the crowd_sel field
>       p_s_crd_a  ->  Percentages for crowd_sel ties percent1|percent2|etc. or NULL if there was no tie

Due to the inherent complexity at the task level, an additional `taskCompiler.py` utility
is included to reconstruct a given task's history.  Each row is a single task and each
column contains information about that task for every application.  If a task was never
completed in an application, then the values for that application will be NULL.  This
utility outputs 3 files:

>       Compiled_Output.csv   ->  Complete task history as CSV
>       Compiled_Output.json  ->  Complete task history as JSON
>       Scrubbed_Output.csv   ->  Final set of attributes for each task as CSV

In order to construct these files a priority/hierarchy must be assigned to each
application, meaning that if a task is completed in multiple applications the
the final values come from the most preferred application:

1. Missing
2. Sweeper
3. Final Internal
4. First Internal
5. Public


##### Additional Notes ######

The primary key between any given set of task.json and task_run.json files is the `id` field in the task
file and the `task_id` in the task run file.  This is fine when working with one application's output but
creates problems when working across applications.  Since each task represents a pond in space-time, a
unique location key can be generated from lat + long + year.  This works without issue EXCEPT that the
lat/long precision on the tasks that were moved to the first internal application was altered, so in order
to get a good match, all lat/long values were rounded (via Python's round() function) to the 8th decimal
place when generating location keys.  This worked, but about 50 ponds have a location that doesn't match
anything.  Re-processing data with the `dartfrog-taskCompiler.py` utility will produce errors with task ID's.

##### Fields #####

Note that the fields are the same for each application except for a few characters pre-pended to the field
name to denote which application they represent:

>       -+= Final Attributes =+-
>
>       location      ->  Location key as described above - generated on the fly
>       wms_url       ->  Final selection - WMS URL from task.json
>       lat           ->  Final selection - degree of latitude from task.json
>       lng           ->  Final selection - degree of longitude from task.json
>       year          ->  Final selection - year from task.json
>       county        ->  Final selection - county name from task.json
>       comp_loc      ->  Name of application the final attributes were selected from
>       n_frk_res     ->  Number of times the crowd classified the pond as 'fracking'
>       n_oth_res     ->  Number of times the crowd classified the pond as 'other'
>       n_unk_res     ->  Number of times the crowd classified the pond as 'unknown'
>       n_tot_res     ->  Total number of times a member of the crowd examined the task (AKA the redundancy)
>       crowd_sel     ->  The classification the crowd chose for the pond
>       p_crd_a    ->  Percent of the crowd's responses that matched the crowd_sel field
>       p_s_crd_a  ->  Percentages for crowd_sel ties percent1|percent2|etc. or NULL if there was no tie

Each application's attributes are denoted with a few leading characters:

>       p_   ->  Public (note that p_crd_a and p_s_crd_a will start with p_p_)
>       fi_  ->  First Internal
>       fn_  ->  Final Internal
>       sw_  ->  Sweeper
>       mt_  ->  Missing Tasks


6. Sample Data
--------------

The sampling routine was similar to the previous applications, however
there are 5 applications and 3 years to sample from.  Samples were
split into applications and years with 100 samples for the public
application and 50 for each internal.  The QGIS random sample bug
was also handled similarly to the previous applications.  The sampling
for this phase served a slightly different purpose as the output from
DartFrog would be used as the input for the Digitizer, which is where
we get one polygon representing each pond, but the Digitizer also
serves as the last location where a human can look at a site and
determine whether or not it is actually a fracking related pond.
The goal of this round of sampling was to identify exactly what
should go into the digitizer (without creating too much work for the
digitizer operator) so some initial data exploration was performed
to determine whether or not the crowd agreement levels could be used
as a threshold for determining which ponds are loaded into the
digitizer.  The threshold for the internal applications was determined
to be 66% and 80% for the public application.  The queries and exports
are as follows:

>       Transformations_and_QAQC/DartFrog/transform/public/stats/dartfrog-public-stats.shp
>           "p_crd_a" >= 80 AND "n_tot_res" >= 10 AND "year" = 2008  ->  Transformations_and_QAQC/DartFrog/sampling/query/dartfrog-public-2008.shp
>           "p_crd_a" >= 80 AND "n_tot_res" >= 10 AND "year" = 2010  ->  Transformations_and_QAQC/DartFrog/sampling/query/dartfrog-public-2010.shp
>
>       Transformations_and_QAQC/DartFrog/transform/first-internal/stats/dartfrog-first-internal-stats.shp
>           "p_crd_a" >= 66 AND "year" = 2005  ->  Transformations_and_QAQC/DartFrog/sampling/query/dartfrog-first-internal-2005.shp
>           "p_crd_a" >= 66 AND "year" = 2008  ->  Transformations_and_QAQC/DartFrog/sampling/query/dartfrog-first-internal-2008.shp
>           "p_crd_a" >= 66 AND "year" = 2010  ->  Transformations_and_QAQC/DartFrog/sampling/query/dartfrog-first-internal-2010.shp
>
>       Transformations_and_QAQC/DartFrog/transform/final-internal/stats/dartfrog-final-internal-stats.shp
>           "p_crd_a" >= 66 AND "year" = 2005  ->  Transformations_and_QAQC/DartFrog/sampling/query/dartfrog-final-internal-2005.shp
>           "p_crd_a" >= 66 AND "year" = 2008  ->  Transformations_and_QAQC/DartFrog/sampling/query/dartfrog-final-internal-2008.shp
>           "p_crd_a" >= 66 AND "year" = 2010  ->  Transformations_and_QAQC/DartFrog/sampling/query/dartfrog-final-internal-2010.shp
>
>       Transformations_and_QAQC/DartFrog/transform/sweeper-internal/stats/dartfrog-sweeper-internal-stats.shp
>           "p_crd_a" >= 66 AND "year" = 2005  ->  Transformations_and_QAQC/DartFrog/sampling/query/dartfrog-sweeper-internal-2005.shp
>           "p_crd_a" >= 66 AND "year" = 2008  ->  Transformations_and_QAQC/DartFrog/sampling/query/dartfrog-sweeper-internal-2008.shp
>           "p_crd_a" >= 66 AND "year" = 2010  ->  Transformations_and_QAQC/DartFrog/sampling/query/dartfrog-sweeper-internal-2010.shp

Additional Notes:
* 2005 Public has no random sample because all 2005 tasks were completed in the
  First Internal and Final Internal applications.
* 2010 Final Internal has no random sampling because all of the 2010 tasks were
  completed in the Public or First Internal applications.
* The Missing Tasks were only examined once and did not need to be randomly
  sampled since the one response constitutes the final classification.

The manually examined files are located in the following locations:

>       Transformations_and_QAQC/DartFrog/sampling/2008/dartfrog-public-2008-sample-100.shp
>       Transformations_and_QAQC/DartFrog/sampling/2010/dartfrog-public-2010-sample-100.shp
>       Transformations_and_QAQC/DartFrog/sampling/2005/dartfrog-first-internal-2005-sample-50.shp
>       Transformations_and_QAQC/DartFrog/sampling/2008/dartfrog-first-internal-2008-sample-50.shp
>       Transformations_and_QAQC/DartFrog/sampling/2010/dartfrog-first-internal-2010-sample-50.shp
>       Transformations_and_QAQC/DartFrog/sampling/2005/dartfrog-final-internal-2005-sample-50.shp
>       Transformations_and_QAQC/DartFrog/sampling/2008/dartfrog-final-internal-2008-sample-50.shp
>       Transformations_and_QAQC/DartFrog/sampling/2005/dartfrog-sweeper-internal-2005-sample-50.shp
>       Transformations_and_QAQC/DartFrog/sampling/2008/dartfrog-sweeper-internal-2008-sample-50.shp
>       Transformations_and_QAQC/DartFrog/sampling/2010/dartfrog-sweeper-internal-2010-sample-50.shp


### Public Results ###

Sample size: 100

2005 - NO SAMPLE (see above section)
2008 - Disagreed with 18 pond classifications - due to "fat fingering"
       the sample size was 99 instead of 100.
2010 - Disagreed with 10 pond classifications

### First Internal Results ###

Sample size: 50

2005 - Disagreed with 2 pond classifications
2008 - Disagreed with 5 pond classifications
2010 - Disagreed with 4 pond classifications

### Final Internal Results ###

Sample size: 50

2005 - Disagreed with 0 pond classifications
2008  - Disagreed with 0 pond classifications
2010  - NO SAMPLE (see above section)

### Sweeper Results ###

Sample size: 50

2005 - Sampled all 6 sites - disagreed with 0 pond classifications
2008 - Disagreed with 6 pond classifications
2010 - Disagreed with 6 pond classifications

### Missing Tasks Results ###

NOT SAMPLED (see above section)



Digitizer Workflow
=================

##### General Description #####

1. Identify input tasks
2. Generate and load tasks
3. Digitize
4. Export data
5. Transform data
6. Resolve intersecting ponds
7. Sample Data


1. Identify Input Tasks
-----------------------

**TODO: Explain**


2. Generate and Load Tasks
--------------------------

**TODO: Explain**


3. Digitize
-----------

The final set of 896 ponds were loaded into a single application for digitizing with a redundancy of 1 and
4 actions: draw polygons and submit, skip pond, classify as unknown, and classify as not a fracking pond
The operator was instructed to digitize and classify tasks with an obvious answer, but skip any that
were questionable or required a more in depth review.  The ponds marked as skipped would then be loaded
into a second digitizer and be reviewed by a panel of SkyTruth employees.
 
At around the 1/3 mark a bug was discovered in the digitizer that prevented multiple geometries from
being recorded, which is not a problem for single ponds, but for multiple ponds in close proximity
that are attached to a single clustered pond point, only the first drawn polygon was recorded.  The
solution to this problem involved two things: the operator was instructed to now skip any multi-ponds
while a patch was developed and deployed.  The patch was successful but introduced an inconsistency
in the output data by storing the polygons in a slightly different way than the original application.
The difference is outlined in the code blocks below.

An additional bug was discovered around the 2/3 mark that was preventing any selection from being recorded
if the triangle on the submit button was clicked.  This bug was successfully quickly patched.

After the initial digitizing pass, some ponds required a second pass.  Initially this second pass was only
expected to include ponds the operator skipped, but due to the two discovered bugs, the second pass
contained ponds with the following characteristics: ponds that were skipped and ponds lacking a selection
key.  The 181 ponds marked for re-examination were loaded and examined by a panel without issue.

The PyBossa applications are as follows:  

    * [First Digitizer](http://crowd.dev.skytruth.org/app/frackfinder_pa_digitizer-pond/)  
    * [Final Digitizer](http://crowd.dev.skytruth.org/app/digitizer_pond_2005-2010_final-review/)  

Only the task_run.json file from the first digitizer exhibits inconsistencies.  The output from the final
application uses the patched structure.

##### Digitizer Bug: Original Info Key #####

NOTE: Each list of vertexes is nested within an additional unused list
>        'info': {'done': {'tasks': 1},  
>                 'selection': 'done',  
>                 'shape': {'coordinates': [[[-79.77771873394, 40.129319804207],  
>                                            [-79.777383349799, 40.1294248643],  
>                                            [-79.777173229614, 40.12900462393],  
>                                            [-79.777534878778, 40.128887441519],  
>                                            [-79.77771873394, 40.129319804207]]],  
>                           'type': 'Polygon'},  
>                  'timings': {'presentTask': 231250, 'reportAnswer': 231596}}


##### Digitizer Bug: Patched Info Key #####

For sites with a single pond, the shapes key contains a list with a single element.  
NOTE: Each list of vertices is nested within an additional list unused
>        'info': {'done': {'tasks': 1},
>                 'selection': 'done',
>                 'shapes': [{'coordinates': [[[-77.916892032231, 41.871592973047],
>                                              [-77.916578816183, 41.871451459773],
>                                              [-77.916582589871, 41.871385420245],
>                                              [-77.916725989989, 41.871228812221],
>                                              [-77.917103358721, 41.871421270274],
>                                              [-77.916935429635, 41.871592973047],
>                                              [-77.916892032231, 41.871592973047]]],
>                             'type': 'Polygon'},
>                            {'coordinates': [[[-77.917186379842, 41.87189298119],
>                                              [-77.916944863854, 41.871753354759],
>                                              [-77.916956184916, 41.8716816547],
>                                              [-77.917199587748, 41.871485422959],
>                                              [-77.917450537955, 41.871694862605],
>                                              [-77.917235437778, 41.871906189095],
>                                              [-77.917186379842, 41.87189298119]]],
>                             'type': 'Polygon'}],
>                 'timings': {'presentTask': 73966, 'reportAnswer': 74292}}


4. Export Data
--------------

Due to bugs in the digitizer, the tasks were completed in two applications,
`first-review` and `final-review`.  The data was exported and stored in the
following locations:

>       Transformations_and_QAQC/Digitizer/tasks/first-review/task.json
>       Transformations_and_QAQC/Digitizer/tasks/first-review/task_run.json
>       Transformations_and_QAQC/Digitizer/tasks/final-review/task.json
>       Transformations_and_QAQC/Digitizer/tasks/final-review/task_run.json


5. Transform Data
-----------------

Similar to the previous applications, a `task2shp.py` utility is included
to handle all the necessary transforms and data aggregations.  The output
data structure is similar to the other utilities that server the same
purpose but the features are polygons representing ponds.  The input data
is slightly different in that the other `task2shp.py` utilities require
both the task.json and task_run.json, this one ONLY takes a modified
task_run.json file.  The next steps prepare that file for processing.

Before running the `task2shp.py` utility, a few pre-processing steps must
be done.  The first takes the task_run.json and adds all the associated
task.json attributes to each task run:

>       ~/GitHub/CrowdProjects/bin/mergeExport.py \
>           Transformations_and_QAQC/Digitizer/tasks/first-review/task.json \
>           Transformations_and_QAQC/Digitizer/tasks/first-review/task_run.json\
>           Transformations_and_QAQC/Digitizer/transform/first-review/tasks-with-added-fields/task_run_added_fields.json
>
>       ~/GitHub/CrowdProjects/bin/mergeExport.py \
>           Transformations_and_QAQC/Digitizer/tasks/final-review/task.json \
>           Transformations_and_QAQC/Digitizer/tasks/final-review/task_run.json \
>           Transformations_and_QAQC/Digitizer/transform/final-review/tasks-with-added-fields/task_run_added_fields.json

Additionally, a classification field was added to the task.json and
task_run.json to note which digitizer it passed through.

NOTE: The overwrite flag on two of the commands is to allow the utility
      to add the field to the file in place.

>       ~/GitHub/CrowdProjects/bin/editJSON.py \
>           -a class=first \
>           Transformations_and_QAQC/Digitizer/tasks/first-review/task.json \
>           Transformations_and_QAQC/Digitizer/transform/first-review/tasks-with-added-fields/task_added_fields.json
>
>       ~/GitHub/CrowdProjects/bin/editJSON.py \
>           --overwrite \
>           -a class=first \
>           Transformations_and_QAQC/Digitizer/transform/first-review/tasks-with-added-fields/task_run_added_fields.json \
>           Transformations_and_QAQC/Digitizer/transform/first-review/tasks-with-added-fields/task_run_added_fields.json
>
>       ~/GitHub/CrowdProjects/bin/editJSON.py \
>           -a class=first \
>           Transformations_and_QAQC/Digitizer/tasks/final-review/task.json \
>           Transformations_and_QAQC/Digitizer/transform/final-review/tasks-with-added-fields/task_added_fields.json
>
>       ~/GitHub/CrowdProjects/bin/editJSON.py \
>           --overwrite \
>           -a class=first \
>           Transformations_and_QAQC/Digitizer/transform/final-review/tasks-with-added-fields/task_run_added_fields.json \
>           Transformations_and_QAQC/Digitizer/transform/final-review/tasks-with-added-fields/task_run_added_fields.json

Tasks that were completed in both applications will be manually resolved
later so the task.json and task_run.json can now be combined.  The
previous step added a classification field that can be used to determine
which application a given task or task run came from.

>       ~/GitHub/CrowdProjects/bin/mergeFiles.py \
>           Transformations_and_QAQC/Digitizer/transform/first-review/tasks-with-added-fields/task_run_added_fields.json \
>           Transformations_and_QAQC/Digitizer/transform/final-review/tasks-with-added-fields/task_run_added_fields.json \
>           Transformations_and_QAQC/Digitizer/derivative-data/Merged_Task_Runs.json

Now that the task run files have been combined the data can be handed
off to the `task2shp.py` utility, which converts the JSON to pond
polygons with attributes.

>       Transformations_and_QAQC/Digitizer/bin/task2shp.py \
>           --process-extra-fields \
>           Transformations_and_QAQC/Digitizer/derivative-data/Merged_Task_Runs.json \
>           Transformations_and_QAQC/Digitizer/derivative-data/deliverable-ponds-candidate.shp


6. Resolve Intersecting Ponds
-----------------------------

Due to the nature of the the data and the bugs discovered in the digitizer application, some ponds
intersect other ponds in the file.  In some cases this intersection is caused by the pond existing for
multiple years, but some ponds were actually digitized twice.  All of the ponds marked as intersecting
with another feature were manually examined and marked for deletion, but only if it was digitized twice.
Of the ponds that were digitized twice, some were digitized in both the first and final applications, and
some were digitized twice a single application.  For ponds that were digitized in both applications the
pond digitized in the first application was marked for deletion and the pond digitized in the second was
kept.  For ponds that were digitized twice in a single application the pond with the larger task_id
was kept.  The digitizer began serving ponds in a random order by after doing about 1/4 of them the order
was changed to serial which means that larger task_ids were completed later and have a better chance of
being digitized after the bugs were discovered.


7. Sample Data
--------------

A random subsample of 100 digitized ponds were manually examined to verify both the data transformations
explained above and the quality of the data.  The main goal was to ensure that the attributes were properly
copied from the merged task_run.json to the proper pond.  Imagery was also used to verify the geometry.
No issues were encountered. 
