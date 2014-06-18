FrackFinder PA 2005-2010
========================




General Description
-------------------
1. Download all task.json and task_run.json for each application
2. Convert each application's JSON files into a single shapefile with one point per task and aggregated crowd responses
3. Randomly sample shapefiles from previous step
4. Determine which tasks must be re-examined based on the sampling results
5. Extract tasks to be re-examined and load into a new internally accessible application - complete tasks
6. Stitch together tasks from all applications into a single final dataset with one row per task and full attributes
7. Extract tasks that were confidently classified as fracking and digitize



Tadpole - Identify Wellpads
---------------------------
Manually examined 100 sample sites in each year from each year by loading the data into QGIS and manually examining each site

### Applications ###
Public

### Data ###
Original Tasks: tadpole/task-backup
Shapefiles: tadpole/transform/stats
Random Samples: tadpole/sampling

### Pre-sampling Filters ###
None

### Results ###
2005 - 6 disagreements
2008 - 4 disagreements
2010 - 2 disagreements



MoorFrog - Click on Ponds
--------------------------
Points classified as ponds in Tadpole were given to MoorFrog as input, which asked users to click on all ponds within a 1200 m x 1600 m bounding box, centered on the Tadpole point.  Unfortunately, this bounding box was only provided for reference and was not used to trash clicks outside the bounding box.  The resulting clicks were then clustered into pond points, but the clustering algorithm did have a minimum number of clicks to create a pond point, which means that even single clicks were turned into ponds.
This is important because because it created some rules for sampling.  Any ponds outside the bounding box were completely ignored, and the number of omitted ponds was counted for each scene.

### Applications ###
Public

### Data ###
Original Tasks: moorfrog/task-backup/
Shapefiles: moorfrog/transform/stats/
Additional Layers: moorfrog/layers
Random Samples: moorfrog/sampling
NOTE: The additional layers includes the actual user clicks, pads, and bboxes

### Pre-sampling Filters ###
All points that did not fall within a bounding box were thrown away

### Results ###
2005 - 18 omitted ponds - None appear to be fracking related
2008 - 19 omitted ponds - None appear to be fracking related
2010 - 6 omitted ponds - 2 appear to be fracking related



DartFrog - Classify Ponds
-------------------------

### Applications ###
Public
First Internal
Final Internal
Sweeper
Missing Tasks

#### Explanation ####
The crowd was slowing down on their DartFrog completion, so a set of

### Data ###

#### Tasks ####
Public Tasks: dartfrog/task-backup/public
First Internal Tasks: dartfrog/task-backup/first-internal
Final Internal Tasks: dartfrog/task-backup/final-internal
Sweeper Internal Tasks: dartfrog/task-backup/sweeper-internal
Missing Tasks: dartfrog/task-backup/missing

#### Shapefiles ####
Public Shapefile: dartfrog/transform/public/stats
First Internal Shapefile: first-internal/transform/public/stats
Final Internal Shapefile: dartfrog/final-internal/public/stats
Sweeper Tasks Shapefile: dartfrog/sweeper/public/stats
Missing Tasks Shapefile: dartfrog/missing/public/stats

### Pre-sampling Filters ###
Public sampling: "p_crd_a" >= 80 AND "n_tot_res" >= 10
Internal sampling: "p_crd_a" >= 66

### Results ###
2005 First Internal - Sampled 50 - disagreed with 2 pond classifications
2008 First Internal - Sampled 50 - disagreed with 5 pond classifications
2010 First Internal - Sampled 50 - disagreed with 4 pond classifications
2005 Final Internal - Sampled 50 - disagreed with 0 pond classifications
2008 Final Internal - Sampled 50 - disagreed with 0 pond classifications
2010 Final Internal - NO SAMPLE - All DartFrog 2010 tasks were completed by the public or the First Internal app
2005 Public - NO SAMPLE - All DartFrog 2005 tasks were completed in the internal applications
2008 Public - Sampled 99 - disagreed with 18 pond classifications (unsure why 99 sites were sampled and not 100)
2010 Public - Sampled 100 - disagreed with 10 pond classifications
2005 Sweeper Internal - Sampled all 6 sites - disagreed with 0 pond classifications
2008 Sweeper Internal - Sampled 50 - disagreed with 6 pond classifications
2010 Sweeper Internal - Sampled 50 - disagreed with 6 pond classifications



Digitizer
---------

### Results ###
Currently in progress



Additional Notes
----------------
There is a bug in the QGIS random sampling tool that causes it to ignore filters, which creates a problem for our method of sampling every year in every application.  The solution to this problem is to apply the required filters and then save to a new file.  Random samples can then be pulled from this file without issue.




FrackFinder Deliverable Ponds 2005-2010 Workflow
================================================

Author: Kevin Wurster - <kevin@skytruth.org>  
[GitHub Repository](https://github.com/SkyTruth/CrowdProjects)

An explanation of how the ponds delivered to JHU were generated from FrackFinder data



### General Description ###
1. Digitize ponds via a private internal PyBossa application
2. Download all task.json and task_run.json for each application (first/final review)
3. Copy the attributes of each task.json object into the associated task_run.json objects
4. Join the two task_run.json files together
5. Convert the combined task_run.json file to a shapefile and mark intersecting ponds
6. Manually mark intersecting ponds for deletion
7. Manual QAQC to verify data transformations
8. Manually remove unnecessary fields and ponds marked for deletion



1. Digitize Ponds
--------------
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
[First Digitizer](http://crowd.dev.skytruth.org/app/frackfinder_pa_digitizer-pond/)  
[Final Digitizer](http://crowd.dev.skytruth.org/app/digitizer_pond_2005-2010_final-review/)  
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




2. Download Data
----------------
The exported task.json and task_run.json files from each application were stored in the CrowdProjects repo
and in the following locations:


    First Pass 2005-2010: CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/first-review/task-backup
  
    Final Pass 2005-2010: CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/final-review/task-backup



3. Copy Attributes
------------------
A utility was developed to add all task.json attributes to the accompanying task_run.json file.

First Digitizer
>        ./CrowdProjects/bin/mergeExport.py \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/first-review/transform/tasks/task.json \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/first-review/transform/tasks/task_run.json \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/first-review/transform/tasks-with-added-fields/task_run_added_fields.json

Final Digitizer
>        ./CrowdProjects/bin/mergeExport.py \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/final-review/transform/tasks/task.json \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/final-review/transform/tasks/task_run.json \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/final-review/transform/tasks-with-added-fields/task_run_added_fields.json

Additionally, a classification field was added to the task.json and task_run.json to note which digitizer
it passed through.

First Digitizer
>        ./CrowdProjects/bin/editJSON.py \
>            --overwrite \
>            -a class=first \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/first-review/transform/tasks-with-added-fields/task_run_added_fields.json \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/first-review/transform/tasks-with-added-fields/task_run_added_fields.json
>
>        ./CrowdProjects/bin/editJSON.py \
>            -a class=first \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/first-review/transform/tasks/task.json \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/first-review/transform/tasks-with-added-fields/task_added_fields.json

Final Digitizer
>        ./CrowdProjects/bin/editJSON.py \
>            --overwrite \
>            -a class=final \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/final-review/transform/tasks-with-added-fields/task_run_added_fields.json \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/final-review/transform/tasks-with-added-fields/task_run_added_fields.json
>
>        ./CrowdProjects/bin/editJSON.py \
>            -a class=final \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/final-review/transform/tasks/task.json \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/final-review/transform/tasks-with-added-fields/task_added_fields.json            



4. Join Data
------------
The utility that converts the task_run.json file into a spatial format is aware enough to ignore any item
that does not have a `shape` or `shapes` key in the info block, so the task_run.json files from both
digitizers can safely be combined into a single file in preparation for processing.  There are scenarios
where digitized ponds will intersect between applications, but the class field that was added in
the previous step will be used to determine which polygon is kept and which is thrown away.

>        ./CrowdProjects/bin/mergeFiles.py \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/final-review/transform/tasks-with-added-fields/task_run_added_fields.json \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/final-review/transform/tasks-with-added-fields/task_added_fields.json \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/Merged_Task_runs.json



5. Convert Data
---------------
The merged task_run.json file can now be converted to a spatial format containing 839 ponds, a set of
attributes, and a field noting whether or not any given feature intersects any other features within
the file.  An area calculation was performed on each feature in its corresponding UTM zone and then
copied into the unaltered input geometry.

>        ./CrowdProjects/FrackFinder/Final_Deliverable/bin/digitizer-task2shp.py \
>            --process-extra-fields \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/Merged_Task_runs.json \
>            CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/Deliverable_Ponds/Deliverable_Ponds.shp



6. Handle Intersecting Ponds
----------------------------
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



7. QAQC/Validation
------------------
A random subsample of 100 digitized ponds were manually examined to verify both the data transformations
explained above and the quality of the data.  The main goal was to ensure that the attributes were properly
copied from the merged task_run.json to the proper pond.  Imagery was also used to verify the geometry.
No issues were encountered. 



8. Ship It!
-----------
The following fields were removed:
  
    selection
    intersect
    delete

The following fields were renamed:
    
    location -> uid

Leaving the following fields:

    task_id: Integer (10.0) -> The task_id from task_run.json
    county: String (254.0)  -> County name
    state: String (254.0)   -> State name
    year: String (254.0)    -> The year the NAIP the user was looking at to identify ponds was collected 
    area_m: Real (254.2)    -> Pond area in meters
    uid: String (254.0)     -> Location key (lat + long + year) - this maps back to previous steps in the processing chain

The shippable ponds are located here:

    CrowdProjects/FrackFinder/Final_Deliverable/digitizer/2005-2010/Shipped_Ponds/Shipped_Ponds.shp