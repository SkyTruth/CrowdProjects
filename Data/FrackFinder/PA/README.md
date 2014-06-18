Source Data Procurement and Processing
======================================

Author: Yolandita Franklin <yolandita@skytruth.org>



Tadpole
-------

### Input data ###

Scraped spuds and permits - conventional vs unconventional. clustered by 100 meter radius. (semi-clustering) once site
is created it doesnt move.  unconventional sites means at least on unconventional permit/spud. extracted all sites
marked as unconventional for FF.

>       C:\Users\Yolandita\Documents\FRACKFINDER\Pennsylvania\Categorizer-Pads_PA-TADPOLE\site info\FrackFinder-Tadpole-sites.csv
>       PA NAIP - 2005, 2008, 2010


### Methodology ###

Three tasks were created for each site -- one task for each year. Links to clipped NAIP imagery for corresponding areas
were included in each task.  Users identified each site as one of the following:

* Well pad - with equipment
* Well pad - empty
* No well pad visible
    
All sites with ?low agreement? rates were uploaded to an internal app to be sorted by SkyTruth staff. Final results for both applications were combined.

### Output Data ###

>       https://sites.google.com/a/skytruth.org/frack/frackfinder/frackfinder-tadpole-pennsylvania-results/2005_WellPads_in_PA_ProjectTADPOLE.csv?attredirects=0&d=1
>       https://sites.google.com/a/skytruth.org/frack/frackfinder/frackfinder-tadpole-pennsylvania-results/2008_WellPads_in_PA_ProjectTADPOLE.csv?attredirects=0&d=1
>       https://sites.google.com/a/skytruth.org/frack/frackfinder/frackfinder-tadpole-pennsylvania-results/2010_WellPads_in_PA_ProjectTADPOLE.csv?attredirects=0&d=1



MoorFrog
--------

### Input Data ###

>       C:\Users\Yolandita\Documents\GitHub\CrowdProjects\FrackFinder\Global_QAQC\moorefrog\task-backup\task.json
>       PA NAIP - 2005, 2008, 2010	(WMS LINKS)

### Methodology ###

A ?buffer? was put around each wellpad found in Tadpole. Each of those sites were observed over 3 years of NAIP - 2005, 2008, 2010.
A WMS layer was served up along with a bounding box representing the buffer zone around each wellpad.
Users marked any ponds found within the bounding box.
    
### Output Data ###

Somewhere on GitHub



DartFrog
--------

### Input Data ###

>       Kind of all over the place
>       PA NAIP - 2005, 2008, 2010	(WMS LINKS)

### Methodology ###

For each site where a pond was identified, a task was created for the years 2005, 2008, and 2010.
Users identified each site as one of the following:

* Frack Pond
* Other
* Unknown

All unknown sites and sites with ?low agreement? rate were uploaded to an internal app to be sorted by SkyTruth staff. Final results for public and internal applications were combined.

### Output data ###

GitHub/CrowdProjects/FrackFinder/Global_QAQC/dartfrog/Compiled_Output.csv



Pollywog
--------

### Input data ###

On Ubuntu - /home/tita/SecretBox/pybossa_tools/digitizer-pond/tasks

### Methodology ###
 
Ponds from DartFrog were buffered by 20 meters. Overlapping buffers were dissolved into one site. Centroids of all buffers were merged with attributes from original ponds. Tasks were created from these new sites and were uploaded to digitizer-pond app.
For each task, the following options were given: 'not a pond', 'skip', or 'Done' (for ponds that were digitized).

### Output Data ###

NOT YET CREATED



Tadpole 2.0
-----------

### Input Data ###

>       GitHub\CrowdProjects\FrackFinder\Global_QAQC\dartfrog\Scrubbed_Output.csv
>       PA NAIP - 2005, 2008, 2010	(WMS LINKS)

### Methodology ###

Tasks were created for fracking ponds found in DartFrog output; one each, only for the years in which they were identified as existing.
Tasks were uploaded to a delimiter app in which SkyTruth staff digitized the perimeter of each pond.
The option was given to identify a site as "Not a Pond," in the case that a non-pond site met the requirements to be included in this stage of the project.

### Output Data ###

NOT YET CREATED
