FrackFinder Source Data
=======================

A description of the source data used to select the original sites used for FrackFinder

### Sites ###
We used a set of sites extracted from a project called SiteInfo which creates "Sites" by spatially clustering drilling
permits, spud reports, FracFocus reports and whatever else we can get our hands on that has good spatial information.

In PA, we used Permits and SPUDS and clustered based on proximity, with the location of the site set to the centroid
of the cluster.

TODO: Find out what clustering radius we used

The SiteInfo data lives in postgres here

    host: ewn3.skytruth.org
    db: skytruth
    tables: public.appomatic_siteinfo.*

This query connects a SiteID guid as using in the FrackFinder project with the individual well APIs that were clustered
to create it.

    select *
    from public.appomatic_siteinfo_well  w
    JOIN public.appomatic_siteinfo_basemodel b
    ON w.site_id = b.id
    where b.guuid = 'b487cb9b-7da9-5685-b8ee-c6d10e548386'

The output of this query for all sites is stored here in siteinfo.csv