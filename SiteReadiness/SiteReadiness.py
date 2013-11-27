#!/usr/bin/env python

"""
SiteReadiness.py: calculate CMS Site Readiness according to
the criteria here: https://twiki.cern.ch/twiki/bin/view/CMS/PADASiteCommissioning

Possible Site Readiness States: READY (R), NOT-READY (NR), WARNING (W), SCHEDULED DOWNTIME (SD)
"""

__author__ = "original: Josep Flix (jflix@pic.es), rewrite: Duncan (dkralph@gmail.com)"

import sys,os
from optparse import OptionParser
# local imports
from ColumnInfo import ColumnInfo
from TimeInfo import TimeInfo
from OutputWriter import OutputWriter
from ReadinessMaker import ReadinessMaker

#----------------------------------------------------------------------------------------
# options
usage = "usage: (example) %prog -p /home/jflix/tmp2 -u http://lhcweb.pic.es/cms -x true/false"
parser = OptionParser(usage=usage, version="%prog 1.0")
parser.add_option("-p", "--path_out",metavar="PATH",    default="/tmp/"+os.environ['USER']+"/readiness", help="Sets the PATH to store the produced data")
parser.add_option("-u", "--url",     metavar="URL",     default="cern.ch",                               help="Sets the base URL where produced data is accessible")
parser.add_option("-x", "--xml",     metavar="BOOLEAN", default="true",                                  help="Sets whether to (re)download the XML files from SSB")
parser.add_option("-o", "--oneSite", metavar="SITE",    default="",                                      help="Ignore all sites except SITE")
parser.add_option("--t2weekends",    metavar="T2WKNDS", default=False,     action='store_true',          help="Count weekends for T2 sites?")
(options, args) = parser.parse_args()
if options.xml != 'true' and options.xml != 'false': # I don't know why this isn't a bolean, but I'm leaving for backwards compatibility
    print 'ERROR: bad xml option'
    sys.exit()

#----------------------------------------------------------------------------------------
# run the readiness calculation
cinfo = ColumnInfo() # read config file
tinfo = TimeInfo()   # set timestamp information
readimaker = ReadinessMaker(options, cinfo, tinfo)
readimaker.MakeReadiness()
owriter = OutputWriter(options, cinfo, tinfo, readimaker.matrices)
owriter.write()

sys.exit(0)
