Ohio 2010-2013 QA/QA
=====================
###Overview
1. Summarize Crowd's Response by Rate of Agreement
2. Manually Validate a Sample Set of Sites and Calculate Area
3. Calculate Area of Reduced Ponds that Correspond to Validated Sites
4. Calculate Combined Areas
5. Calculate Intersecting Area
6. Calculate % Area


1. Summarize Crowd's Response by Rate of Agreement
-------------------------------------------------------------

Using the following tools and methods, shapefiles containing the best simple representation of the crowds responses were generated. These simplified representations were calculated by % agreement as well as a geometric mean.

>	    OH/2010-2013/Pad-Delineator/bin/pad-reducer.py
>
>	    ./pad-reducer.py \ 
>		     OH/2010-2013/Pad-Delineator/transform.shp \
>		     OH/2010-2013/Pad-Delineator/transform/reduced-pads/50percent-agreement.shp \
>		     -- agreement 0.50

2. Manually Validate a Sample Set of Sites and Calculate Area
-------------------------------------------------------------
NAIP for Ohio 2010-2013, as well as results from the pad delineator app, was loaded into QGIS. A vector file was created, containing manually delineated pads from randomly selected sites.
	
>		OH/2010-2013/Pad-Delineator/transform/pad_delineations.shp
>		https://mapsengine.google.com/06136759344167181854-11845109403981099587-4/mapview/?authuser=0
>	 
>		Output: comparison-set.shp


Reproject to a pseudo mercator, allowing the area to be calculated in meters.

		Input: comparison-set.shp
		 - CRS: WGS 84/Pseudo Mercator
		Output: comparison-mercator.shp

3. Calculate Area of Reduced Ponds that Correspond to Validated Sites
--------------------------------------------------------------------
###Resolve overlapping geometries for input.

 - Dissolve:

		Input: 50percent-agreement.shp
		Output: 50-all-dissolved.shp

 - Explode via Multipart to Singleparts:

		Input: 50-all-resolved.shp


###Select sites that correspond to comparison set.

 - Spatial Query:
	
		Source features: 50-all-resolved.shp
		Where feature: Intersects
		Reference feature: comparison-set.shp

 - For `50-all-resolved.shp`, save only selected features, reprojecting* in Save As... dialogue box.

	
		CRS: WGS 84/Pseudo Mercator
		Output: 50-sample-mercator.shp
		
	**Reprojecting to a pseudo mercator allows the area to be calculated in meters.*


###Calculate and export area

 - Create a new field in the attribute table and calculate Area via **Field Calculator** on `50-sample-mercator.shp`.

 - Save attributes as CSV
		
		Input: 50-sample-mercator.shp
		Output: 50-sample-mercator.csv

4. Calculate Combined Areas
------------------------------------------------------------------
###Combine both layers to calculate total area.
 - Merge Shapefiles to One:
 - 
		Inputs: comparison-mercator.shp, 50-sample-mercator.shp
		Output: 50percent-merged.shp  - Dissolve:	
		Input: 50-comp-merged.shp
		Output: 50-comp-merged-dissolved.shp - Explode via Multipart to Singleparts:
		Input: 50-comp-merged-dissolved.shp
		Output: 50-comp-merged-dissolved-exploded.shp

###Calculate and export combined areas
 - Delete any existing fields in the attribute table labeled **'Area'**.  - Create a new field in the attribute table and calculate Area via **Field Calculator** on `50-comp-merged-dissolved-exploded.shp`. - Save attributes as CSV				Input: 50-comp-merged-dissolved-exploded.shp		Output: 50-comp-merged-area.csv

5. Calculate Intersecting Area
-------------------------------------------------------------------

###Find intersection of polygons

 - Intersect: 			Input: 50-sample-mercator.shp		 - Intersect: comparison-mercator.shp		Output: 50-comp-intersection.shp
###Calculate and export intersecting area
 - Create a new field in the attribute table and calculate Area via **Field Calculator** on `50-comp-intersection.shp`. - Save attributes as CSV				Input: 50-comp-intersection.shp		Output: 50-comp-intersecting-area.csv6. Calculate % Errors----------------------------------------------------------------###Calculate areas

- Area of Validated Sites = sum of areas in `50-sample-mercator.csv`- Area of Comparison Set = sum of areas in `comparison-mercator.csv`- Intersecting Area = sum of areas in `50-comp-intersecting-area.csv`- Combined Area = sum of areas in `50-comp-merged-area.csv`###Calculate Errors
- % Error = |Area by Agreement - Area of Comparison Set| / Area of Comparison Set- % Error by Omission = |Intersecting Area - Area of Comparison Set| / Area of Comparison Set- % Error by Inclusion = |Combined Area - Area of Comparison Set| / Area of Comparison Set- Total Error of Omission & Inclusion = % Error by Omission + % Error by Inclusion