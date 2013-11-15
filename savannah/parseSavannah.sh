#!/bin/bash
webdir=$HOME/www/savannah
mkdir -p $webdir
python26 ./parseSavannah.py                  >& $webdir/savannah.html
#python26 ./savannahStatistics.py --days 7    >& $webdir/savannah_statistics_last_7_days.html
#python26 ./savannahStatistics.py --days 30   >& $webdir/savannah_statistics_last_30_days.html
#python26 ./savannahStatistics.py             >& $webdir/savannah_statistics_last_year.html
#python26 ./savannahStatistics.py --days 9999 >& $webdir/savannah_statistics_2011_2012.html
#python26 ./savannahSummary.py                >& $webdir/savannah_summary_last_year.html
