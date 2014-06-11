DartFrog
========

Phase 3 of FrackFinder PA 2005-2013.  Users were shown a NAIP scene containing a pond
that was identified during MooreFrog (phase 2) and were asked to classify it as
'Fracking', 'Not Fracking', or 'Unknown'.

Unless otherwise noted with a README, data transforms were performed with the following command:

>       ./bin/dartfrog-task2shp.py \
>           tasks/{APP-NAME}/task.json \
>           tasks/{APP-NAME}/task_run.json \
>           transform/{APP-NAME}/stats/{APP-NAME}-stats.shp