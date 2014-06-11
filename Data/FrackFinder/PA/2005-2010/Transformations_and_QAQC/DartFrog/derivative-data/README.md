Derivative Data Notes
=====================

Author: Kevin Wurster - <kevin@skytruth.org>
[GitHub Repository](https://github.com/SkyTruth/CrowdProjects)



Compiled Output
---------------
The `dartfrog-taskCompiler.py` utility analyzes tasks from all applications and constructs a full history
for each task, in addition to a final set of attributes.  The two `Compiled_Output.*` files contain the full
history and the `Scrubbed_Output.csv` contains just the final set of attributes, but when using for
analytical purposes it is probably best to pull this information out of the first several columns in the
`Compiled_Output.*` files due to how `Scrubbed_Output.csv` is generated.  The data isn't bad, it just isn't
generated the EXACT same way the `Compiled_Output.*` data is constructed.



Compiled Output Data Description
--------------------------------


##### General Structure #####
Each row represents one task and each column represents some attribute.  The information in task_run.json
was analyzed for each task and condensed into a set of attributes that describe the actual input task,
which in turn describes a pond.


##### Application Prioritization #####
The applications were completed serially and when selecting which attributes to use for a given task, the
most recent application should always be used. For instance, if a task was only completed in the `public`
and `sweeper` applications, the final values should be selected from `sweeper application`.  This logic
was followed in the `dartfrog-taskCompiler.py` utility.  The hierarchy is as follows:

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
name to denote which application they represent

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
>
>       
>       -+= Public Application Attributes =+-
>       
>       p_crd_a
>       p_s_crd_a
>       p_n_frk_res
>       p_n_oth_res
>       p_n_unk_res
>       p_n_tot_res
>       p_crowd_sel
>       p_p_crd_a   
>       p_p_s_crd_a 
>
>
>       -+= Attributes from the First Internal =+-
>
>       fi_n_frk_res
>       fi_n_oth_res
>       fi_n_unk_res
>       fi_n_tot_res
>       fi_crowd_sel
>       fi_p_crd_a
>       fi_p_s_crd_a
>
>
>       -+= Attributes from the Final Internal Application =+->
>
>       fn_n_frk_res
>       fn_n_oth_res
>       fn_n_unk_res
>       fn_n_tot_res
>       fn_crowd_sel
>       fn_p_crd_a
>       fn_p_s_crd_a
>
>
>       -+= Attributes from the Sweeper Internal Application =+->
>
>       sw_n_frk_res
>       sw_n_oth_res
>       sw_n_unk_res
>       sw_n_tot_res
>       sw_crowd_sel
>       sw_p_crd_a
>       sw_p_s_crd_a
>
>
>       -+= Attributes from the Missing Internal Application =+->
>
>       mt_n_frk_res
>       mt_n_oth_res
>       mt_n_unk_res
>       mt_n_tot_res
>       mt_crowd_sel
>       mt_p_crd_a  
>       mt_p_s_crd_a
