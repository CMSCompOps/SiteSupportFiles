#!/bin/bash

dir1=$HOME/www/readiness
dir2=$HOME/www/readiness-from-svn

for item in ASCii/Daily_HistoricStatistics.txt ASCii/SiteReadiness_HistoricStatistics.txt; do
    diff $dir1/$item $dir2/$item
done

for dir in HTML PLOTS toSSB; do
    diff --recursive $dir1/$dir $dir2/$dir
done
