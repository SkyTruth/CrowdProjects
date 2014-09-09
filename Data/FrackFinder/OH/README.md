SkyTruth FrackFinder OH {TODO: Years} Methodology
=================================================


Permitting information can be downloaded in a computer readable delimited
format from the Oil and Gas division of the Ohio DNR:

>       http://oilandgas.ohiodnr.gov/shale

Data was downloaded on `2014-07-22` and is currently located in the following
locations:

    2010-2013/Tadpole/source_data/Utica_071914.pdf
    2010-2013/Tadpole/source_data/Utica_071914.xls
    2010-2013/Tadpole/source_data/Utica_Weekly_071914.pdf

The table contains a few header and footer rows that are not needed for
processing, so they were removed and the file saved as:

>       2010-2013/Tadpole/source_data/Utica_071914_No_Headers.csv

The data was further transformed with the commands listed below.  Information
about each utility can be found with `$UTILITY --help`:
\#TODO: add marcellus to commands below and fix file paths

>       ./2010-2013/Tadpole/bin/permits2sites.py \
>           2010-2013/Tadpole/source_data/Utica_071914_No_Headers.csv \
>           2010-2013/Tadpole/transform/clustered_sites_071914.csv
>
>       ./2010-2013/Tadpole/bin/generateTadpoleTasks.py \
>           2010-2013/Tadpole/transform/clustered_sites_071914.csv \
>           2010-2013/Tadpole/input_tasks/input_tasks.json

NAIP imagery was downloaded from the NRCS Data Gateway for 2010, 2011, and 2013.
Unfortunately the uncompressed GeoTiff's were not available so SID's were used.




FrackFinder Ohio 2014
=====================



Tadpole 2014 Workflow
=====================

##### General Description #####

1. Identify, generate and load tasks
2. ...
3. Export and transform


1. Identify, Generate and Load Tasks
------------------------------------

A WMS layer for LightHawk's 2014 aerial imagery was loaded into QGIS and a vector layer was created, outlining the boundary of the imagery.

	https://mapsengine.google.com/06136759344167181854-11845109403981099587-4/wms/
	Layer ID: 06136759344167181854-02429742455903582501-4

	2014/Tadpole/transform/2014_aerial_image_boundary.shp

The clustered sites that were used to create tasks for OH padmapper 2010-2013 was loaded into QGIS,  and a spatial query was done to filter tasks within the 2014 aerial image boundary, ensuring that no sites fell on the edge of the boundary. Sites within the boundary were saved in the 2014 directory

	
	2010-2013/Tadpole/transform/utica_marcellus_clustered_sites_071914.csv

	2014/Tadpole/transform/utica_marcellus_clustered_sites_071914.csv

Using a following tools and methods, new tasks were created and added to a categorizer-pad app 

	2014/Tadpole/bin/generateTadpoleTasks.py

        $ ./createTasks.py \
            -n 10 -c \
            -s http://crowd.skytruth.org \ 
            -k "{YOUR_API_KEY}" \
            -a categorizer-pad \
            -r OH-padmapper-2014 \
            -t ~/CrowdProjects/Data/FrackFinder/OH/2014/Tadpole/transform/input_tasks/utica_marcellus_071914_input_tasks.json

The input tasks can be found here

	2014/Tadpole/input_tasks/utica_marcellus_071914_input_tasks.json


3. Export and Transform
-----------------------

Input tasks and task runs were placed in `Tadpole/output_tasks` and aggregated stats were produced with:

        $ ./Tadpole/bin/task2shp.py \
                output_tasks/task.json \
                output_tasks/task_run.json \
                transform/output-stats.shp
                