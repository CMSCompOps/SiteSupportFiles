logdir=`date +%m/%d`
webdir=$HOME/www/readiness
mkdir -p $webdir $logdir
./SiteReadiness.py -p $webdir -c DailyMetricsCorrections.txt -u http://cern.ch/test-readiness -x true
./UsableSites.py  -p /tmp/usable -u http://lhcweb.cern.xch/cms
