#!/usr/bin/env python

""" @author: Josep Flix (jflix@pic.es) """

import sys, xml.dom.minidom, os, datetime, time, pprint
from xml import xpath
from optparse import OptionParser
import simplejson as json

usage = "usage: (example) %prog -p /home/jflix/tmp2"
parser = OptionParser(usage=usage, version="%prog 1.0")
parser.add_option("-p", "--path_out", dest="path_out", help="Sets the PATH to store the produced data", metavar="PATH")
(options, args) = parser.parse_args()

if len(sys.argv) != 3:
	parser.error("incorrect number of arguments. Check needed arguments with --help")

today=datetime.datetime.utcnow()
todaystamp=today.strftime("%Y-%m-%d")
todaystampfile=today.strftime("%Y-%m-%d %H:%M:%S")
todaystampfileSSB=today.strftime("%Y-%m-%d 00:00:01")
todaystamptofile=today.strftime("%Y%m%d_%H")
todaystamptotxt=today.strftime("%Y%m%d %H")

reptime="# - Report made on %s (UTC)\n" % todaystampfile

pathSiteDB=options.path_out + "/INPUTxmls"
fileSiteDB=pathSiteDB + "/sitedb.xml"
pathout= options.path_out + "/toSSB"
pathoutHTML= options.path_out + "/HTML"
pathoutPLOTS= options.path_out + "/PLOTS"
pathoutASCII= options.path_out + "/ASCii"
ssbout="%s/IsSiteInSiteDB_SSBfeed.txt" % pathout

if not os.path.exists(options.path_out):
        os.makedirs(options.path_out)
if not os.path.exists(pathout):
	os.makedirs(pathout)
if not os.path.exists(pathoutHTML):
	os.makedirs(pathoutHTML)
if not os.path.exists(pathoutPLOTS):
	os.makedirs(pathoutPLOTS)
if not os.path.exists(pathSiteDB):
	os.makedirs(pathSiteDB)
if not os.path.exists(pathoutASCII):
	os.makedirs(pathoutASCII)
	
SiteDB_url="https://cmsweb.cern.ch/sitedb/data/prod/federations-sites"
SiteDB_sites=[]

print "Getting the url %s" % SiteDB_url
os.system("curl -ks --cert $X509_USER_PROXY --key $X509_USER_PROXY  '%s' > %s" % (SiteDB_url,fileSiteDB))
	
f=file(fileSiteDB,'r')
rows=json.loads(f)
f.close()

for siteName in rows['result']:
	SiteDB_sites.append(siteName[3]) 

f=file(ssbout,'w')
f.write('# Is Site in SiteDB?\n')
f.write('# Information taken daily from SiteDB: ' + SiteDB_url + '\n')
f.write('#\n')
f.write(reptime)
f.write('#\n')

SiteDB_sites.sort()

for i in SiteDB_sites:
	site=i
	status="true"
	color="green"
	link = SiteDB_url
	f.write('%s\t%s\t%s\t%s\t%s\n' % (todaystampfileSSB, site, status, color, link))

f.close()
						
sys.exit(0)
