me=me
if [ $me ]; then
    webdir=$HOME/www/readiness
    mkdir -p $webdir
    ./SiteReadiness.py -p $webdir -u $HOME/www -x false #--oneSite T2_RU_PNPI
    #./UsableSites.py  -p /tmp/$USER/usable -u http://lhcweb.cern.xch/cms
else
    webdir=$HOME/www/readiness-from-svn
    mkdir -p $webdir
    ./from-svn/from-svn-SiteReadiness.py -p $webdir -u $HOME/www -x false #--oneSite T2_US_Caltech
fi
