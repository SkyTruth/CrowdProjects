MoorFrog 2013 Workflow
======================

Author: Kevin Wurster <kevin@skytruth.org>
[GitHub Repository](https://github.com/SkyTruth/CrowdProjects)

### General Description ###

1. Generate input tasks
2. Load into application
3. Classify ponds



1. Generate Input Tasks
-----------------------

An explanation of how the input task queries were determined can be found in `2013/Tadpole/README.md`

Output from `Tadpole` was processed into a set of input tasks for MoorFrog using the following
commands:

>       ./bin/taskGenerator.py ../Tadpole/transform/stats/tadpole-stats.shp input_tasks/from_internal.json -query "p_crd_a >= 66 AND crowd_sel = 'pad' AND class = 'internal'" --add-info-class=internal  
>       ./bin/taskGenerator.py ../Tadpole/transform/stats/tadpole-stats.shp input_tasks/from_public.json -query "p_crd_a >= 70 AND crowd_sel = 'pad' AND class = 'public'" --add-info-class=public
>       CrowdProjects/bin/mergeFiles.py input_tasks/from_* input_tasks/combined_input_tasks.json



2. Load Tasks
-------------

Tasks were loaded with the `createTasks.py` utility, which can be found in the [pybossa_tools](https://github.com/skytruth/pybossa_tools)
repository.

>       createTasks.py 

