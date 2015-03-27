#!/bin/sh
# Script to run a secondary version of the SR script when the main script fails:
# acronjob in acrontab jartieda
# 38 0,6,12,18 * * * lxplus /afs/cern.ch/user/j/jartieda/SiteSupportFiles/SiteReadiness/run_local.sh &> /dev/null
# 43 * * * * lxplus ssh vocms202 cp -a $HOME/www/SR2/. /afs/cern.ch/cms/LCG/www/sreadiness/SiteReadiness/ &> /dev/null
# 43 * * * * lxplus ssh vocms202 cp -a $HOME/www/SR2/. /afs/cern.ch/cms/LCG/www/sreadiness/CommLinksReports/ &> /dev/null
location=$HOME/SiteSupportFiles/SiteReadiness
webdir=$HOME/www/SR2
webofficial=/afs/cern.ch/cms/LCG/www/sreadiness/SiteReadiness
webofficial2=/afs/cern.ch/cms/LCG/www/sreadiness/CommLinksReports
link=http://cms-site-readiness.web.cern.ch/cms-site-readiness

# Running all necessary scripts
cd $location
# Active links
echo "*** EnabledLinksFromPhEDExDataSrv.py ***"
python EnabledLinksFromPhEDExDataSrv.py -p $webdir -u $link

# Site Readiness python
echo "*** SiteReadiness.py ***"
./SiteReadiness.py -p $webdir -u $link
# $webdir: output location
# $link: address to use inside files for output links

# Usable sites for analysis
#echo "*** UsableSites.py ***"
#python UsableSites.py -p $webdir -u $link

# copy all output files to web location
cp -a $webdir/. $webofficial/
cp -a $webdir/. $webofficial2/
echo "*** All copies completed ***"