#!/usr/bin/env python

""" @author: Josep Flix (jflix@pic.es) """

import sys, xml.dom.minidom, os, datetime, time, pprint
from xml import xpath
from optparse import OptionParser
import httplib
import json
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
	
#SiteDB_url="https://cmsweb.cern.ch/sitedb/reports/showXMLReport?reportid=naming_convention.ini"
#print "Getting the url %s" % SiteDB_url
#os.system("curl -ks -H 'Accept: text/xml'  '%s' > %s" % (SiteDB_url,fileSiteDB))
#f=file(fileSiteDB,'r')
#t= xml.dom.minidom.parse(f)
#f.close()

def fetch_all_sites(url,api):
  headers = {"Accept": "application/json"}
  if 'X509_USER_PROXY' in os.environ:
    print 'X509_USER_PROXY found'
    conn = httplib.HTTPSConnection(url, cert_file = os.getenv('X509_USER_PROXY'), key_file = os.getenv('X509_USER_PROXY'))
  elif 'X509_USER_CERT' in os.environ and 'X509_USER_KEY' in os.environ:
    print 'X509_USER_CERT and X509_USER_KEY found'
    conn = httplib.HTTPSConnection(url, cert_file = os.getenv('X509_USER_CERT'), key_file = os.getenv('X509_USER_KEY'))
  elif os.path.isfile('/data/certs/servicecert.pem') and os.path.isfile('/data/certs/servicekey.pem'):
    conn = httplib.HTTPSConnection(url, cert_file = '/data/certs/servicecert.pem', key_file = '/data/certs/servicekey.pem')
  else:
    print 'You need a valid proxy or cert/key files'
    sys.exit()
  r1=conn.request("GET",api, None, headers)
  r2=conn.getresponse()
  inputjson=r2.read()
  jn = json.loads(inputjson)
  conn.close()
  return jn

url = "cmsweb.cern.ch"
api = "/sitedb/data/prod/federations-sites"
SiteDB_url = url + api
SiteDB_sites=[]

allSitesList = fetch_all_sites(url, api)
info = {}
for site in allSitesList['result']:
  #print site[3]
  SiteDB_sites.append(site[3])

#for urls in xpath.Evaluate('/report/result/item', t):

#	info={}
#	for target in xpath.Evaluate("cms", urls):
#      		if target.hasChildNodes():
#		      	s=target.firstChild.nodeValue.encode('ascii')
#	       	else:
#	      		s=""
#		if s not in SiteDB_sites:
#			SiteDB_sites.append(s)

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
