logdir=`date +%m/%d`
webdir=$HOME/www/readiness
mkdir -p $webdir $logdir
#./SiteReadiness.py -p $webdir -u http://cern.ch/test-readiness -x true
./SiteReadiness.py -p $webdir -u $HOME/www -x false
#./UsableSites.py  -p /tmp/$USER/usable -u http://lhcweb.cern.xch/cms
