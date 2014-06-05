SkyTruth QAQC Workflow
======================



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



MooreFrog - Click on Ponds
--------------------------
Points classified as ponds in Tadpole were given to MooreFrog as input, which asked users to click on all ponds within a 1200 m x 1600 m bounding box, centered on the Tadpole point.  Unfortunately, this bounding box was only provided for reference and was not used to trash clicks outside the bounding box.  The resulting clicks were then clustered into pond points, but the clustering algorithm did have a minimum number of clicks to create a pond point, which means that even single clicks were turned into ponds.
This is important because because it created some rules for sampling.  Any ponds outside the bounding box were completely ignored, and the number of omitted ponds was counted for each scene.

### Applications ###
Public

### Data ###
Original Tasks: moorefrog/task-backup/
Shapefiles: moorefrog/transform/stats/
Additional Layers: moorefrog/layers
Random Samples: moorefrog/sampling
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