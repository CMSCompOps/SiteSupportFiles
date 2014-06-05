#!/bin/sh
# Script to run a secondary version of the SR script when the main script fails:
# acronjob in acrontab jartieda
# 38 0,6,12,18 * * * lxplus /afs/cern.ch/user/j/jartieda/SiteSupportFiles/SiteReadiness/run_local.sh
# 43 * * * * lxplus ssh vocms202 cp -a $HOME/www/SR2/. /afs/cern.ch/cms/LCG/www/sreadiness/SiteReadiness/
location=$HOME/SiteSupportFiles/SiteReadiness
webdir=$HOME/www/SR2
webofficial=/afs/cern.ch/cms/LCG/www/sreadiness/SiteReadiness
link=http://cms-site-readiness.web.cern.ch/cms-site-readiness

# Running all necessary scripts
# Active links
python EnabledLinksFromPhEDExDataSrv.py -p $webdir -u $link

# Site Readiness python
cd $location
./SiteReadiness.py -p $webdir -u $link
# $webdir: output location
# $link: address to use inside files for output links

# Usable sites for analysis
python UsableSites.py -p $webdir -u $link

# copy all output files to web location
cp -a $webdir/. $webofficial/
echo "*** All copies completed ***"