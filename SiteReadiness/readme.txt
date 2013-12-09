README.TXT
-----------

The production version, the scripts that are continually running to generate the SR reports, are located here:
https://svnweb.cern.ch/trac/cmsfomon/browser/SiteReadiness/trunk/

To make any changes or modifications to the production version contact
- Diego da Silva Gomes <diego@cern.ch>
- Alan Malta Rodrigues <alan.malta@cern.ch>

Github repositories (for official changes contact John Artieda <artiedaj@fnal.gov>)
Official: https://github.com/CMSCompOps/SiteSupportFiles/tree/master/SiteReadiness
Duncan Ralph: https://github.com/psathyrella/SiteSupportFiles/tree/merge-amaltaro-savannah/SiteReadiness

How long does it take to run the scripts?
SiteReadiness.py takes about 30 seconds to run

--
To generate own (rewritten version) of CMS Site Readiness Reports.
- run from lxplus:
webdir=$HOME/www/readiness
mkdir -p $webdir
./SiteReadiness.py -p $webdir -u $HOME/www

--
Adding/Excluding a metric in the reports is super easy.
- you need the column number from SSB
- add it to this file: https://github.com/CMSCompOps/SiteSupportFiles/blob/master/SiteReadiness/data/readiness.conf
- here you can comment a line to exclude a metric (need reorganizing of order of all metrics)
- Also, you can specify the tiers you want to apply this new metric to and the order in which you want it to appear (need reorganizing of order of metrics)

--
Configuration to enable combining information from multiple sites into the readiness report of 1 site (T1 MSS + Disk under 1 Site SR Report)
- the following link will soon be merged to the official Github repository: 
https://github.com/psathyrella/SiteSupportFiles/blob/merge-amaltaro-savannah/SiteReadiness/data/credit-transfers.conf

--
Html printing function:
OutputWriter.py