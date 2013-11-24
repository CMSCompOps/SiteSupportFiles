#logdir=`date +%m/%d`

me=me
if [ $me ]; then
    webdir=$HOME/www/readiness
    mkdir -p $webdir $logdir
    ./SiteReadiness.py -p $webdir -u $HOME/www -x false #--oneSite T2_RU_PNPI
    #./UsableSites.py  -p /tmp/$USER/usable -u http://lhcweb.cern.xch/cms
    # old:
    #./SiteReadiness.py -p $webdir -u http://cern.ch/test-readiness -x true
else
    webdir=$HOME/www/readiness-from-svn
    mkdir -p $webdir $logdir
    ./from-svn/from-svn-SiteReadiness.py -p $webdir -u $HOME/www -x false #--oneSite T2_US_Caltech
fi
