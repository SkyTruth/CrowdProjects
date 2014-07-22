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

>       ./2010-2013/Tadpole/bin/permits2sites.py \
>           2010-2013/Tadpole/source_data/Utica_071914_No_Headers.csv \
>           2010-2013/Tadpole/transform/clustered_sites_071914.csv
>
>       ./2010-2013/Tadpole/bin/generateTadpoleTasks.py \
>           2010-2013/Tadpole/transform/clustered_sites_071914.csv \
>           2010-2013/Tadpole/input_tasks/input_tasks.json

NAIP imagery was downloaded from the NRCS Data Gateway for 2010, 2011, and 2013.
Unfortunately the uncompressed GeoTiff's were not available so SID's were used.
