Workflow
========

Author: Kevin Wurster <kevin@skytruth.org>
[GitHub Repository](https://github.com/SkyTruth/CrowdProjects)
Software: QGIS 2.2, GDAL 1.11.0, Python 2.7.7, PyCharm 3.4.1, Mac 10.9.3

An explanation of how input tasks were generated



### General Description ###
1. Generate input tasks
2. Load into application
3. Classify



1. Generate Input Tasks
-----------------------

Output from `Tadpole` was processed into a set of input tasks for MoorFrog using the following
commands:

>       ./bin/taskGenerator.py ../Tadpole/transform/stats/tadpole-stats.shp input_tasks/from_internal.json -query "p_crd_a >= 66 AND crowd_sel = 'pad'" --add-info-class=internal  
>       ./bin/taskGenerator.py ../Tadpole/transform/stats/tadpole-stats.shp input_tasks/from_public.json -query "p_crd_a >= 70 AND crowd_sel = 'pad'" --add-info-class=public
>       CrowdProjects/bin/mergeFiles.py input_tasks/from_* input_tasks/combined_input_tasks.json



2. Load Tasks
-------------

