#!/usr/bin/env python

""" @author: Josep Flix (jflix@pic.es) """

import sys, xml.dom.minidom, os, datetime, time, pprint
from xml import xpath
from datetime import date
import simplejson as json

# OptParse
from optparse import OptionParser


usage = "usage: (example) %prog -p /home/jflix/tmp2 -u http://lhcweb.pic.es/cms"
parser = OptionParser(usage=usage, version="%prog 1.0")
parser.add_option("-p", "--path_out", dest="path_out", help="Sets the PATH to store the produced data", metavar="PATH")
parser.add_option("-u", "--url", dest="url", help="Sets the base URL where produced data is accessible", metavar="URL")
(options, args) = parser.parse_args()

if len(sys.argv) != 5:
	parser.error("incorrect number of arguments. Check needed arguments with --help")
		
today=datetime.datetime.utcnow()
todaystamp=today.strftime("%Y-%m-%d")
todaystampfile=today.strftime("%Y-%m-%d %H:%M:%S")
todaystamptofile=today.strftime("%Y%m%d_%H")
todaystamptotxt=today.strftime("%Y%m%d %H")

GetURLs=True

pathN=options.path_out + "/INPUTxmls"
pathout= options.path_out + "/toSSB"
pathoutHTML= options.path_out + "/HTML"
pathoutPLOTS= options.path_out + "/PLOTS"
pathoutASCII= options.path_out + "/ASCii"

if not os.path.exists(options.path_out):
	os.makedirs(options.path_out)
if not os.path.exists(pathout):
	os.makedirs(pathout)
if not os.path.exists(pathoutHTML):
	os.makedirs(pathoutHTML)
if not os.path.exists(pathoutPLOTS):
	os.makedirs(pathoutPLOTS)
if not os.path.exists(pathN):
	os.makedirs(pathN)
if not os.path.exists(pathoutASCII):
	os.makedirs(pathoutASCII)
	
hours=1 # Number of hours to get info from SSB

fileSSB= pathout + '/UsableSites_SSBfeed.txt'

# Functions

def ProduceSiteReadinessSSBFile(usable, not_usable, fileSSB, todaystamptofile, downtime):

	todaydate = date.today()

	today=datetime.datetime.utcnow()
	todaystampfileSSB=today.strftime("%Y-%m-%d %H:00:01")

	linkSSB= options.url + "/SiteReadinessAnalysis/ASCii/UsableSites_" + todaystamptofile + ".txt"
	
	fileHandle = open ( fileSSB , 'w' )

	siteus = usable.keys()
	siteus.sort()
	
	for sitename in siteus:
		tofile=todaystampfileSSB + '\t' + sitename + '\t' + "usable" + '\t' + "green" + '\t' + linkSSB + "\n"
		fileHandle.write(tofile)
	
	sitenous = not_usable.keys()
	sitenous.sort()
	
	for sitename in sitenous:
		if sitename in downtime:	
			tofile=todaystampfileSSB + '\t' + sitename + '\t' + "scheduled_downtime" + '\t' + "brown" + '\t' + linkSSB + "\n"
			fileHandle.write(tofile)
		else:
			tofile=todaystampfileSSB + '\t' + sitename + '\t' + "not_usable" + '\t' + "red" + '\t' + linkSSB + "\n"
			fileHandle.write(tofile)
			
# URLs with SSB inputs --------------------------------------------------------------------------------------

#webserver_devel="http://dashb-ssb-devel.cern.ch"
webserver="http://dashb-ssb.cern.ch"

Downtimes_top= webserver + "/dashboard/request.py/getplotdata?columnid=121&batch=1&time=" + str(hours) 
Ranking= webserver + "/dashboard/request.py/getplotdata?columnid=96&batch=1&time=" + str(hours)
CE_sam= webserver + "/dashboard/request.py/getplotdata?columnid=128&batch=1&time=" + str(hours)
SRM_sam= webserver + "/dashboard/request.py/getplotdata?columnid=132&batch=1&time=" + str(hours)

ColumnMatrix = {}  # SSB URLs Matrix
ColumnMatrix['Downtimes_top']=Downtimes_top
ColumnMatrix['CE_sam']=CE_sam
ColumnMatrix['SRM_sam']=SRM_sam
ColumnMatrix['Ranking']=Ranking

# -----------------------------------------------------------------------------------------------------------
	
SiteDB_url="https://cmsweb.cern.ch/sitedb/data/prod/federations-sites"
SiteDB_sites=[]
fileSiteDB = "sitedb.json"
print "Getting the url %s" % SiteDB_url
os.system("curl -ks --cert $X509_USER_PROXY --key $X509_USER_PROXY  '%s' > %s" % (SiteDB_url,fileSiteDB))
	
f=file(fileSiteDB,'r')
rows=json.loads(f)
f.close()

for siteName in rows['result']:
	SiteDB_sites.append(siteName[3]) 

########################################################
# Reading data from SSB
########################################################

sites={}

ColumnItems = ColumnMatrix.keys()
ColumnItems.sort()
ColumnItems.reverse()

for col in ColumnItems:
	
#	print col
	
	url=ColumnMatrix[col]

	fileN=pathN+"/"+col+".xml"

	if GetURLs == True:
		print "Getting the url %s" % url
		os.system("curl -s -H 'Accept: text/xml'  '%s' > %s" % (url,fileN))
	
	f=file(fileN,'r')
	t= xml.dom.minidom.parse(f)
	f.close()

	for urls in xpath.Evaluate('/getplotdata/csvdata/item', t):

                info={}
		for option in ('Status', "COLOR", 'Time', 'EndTime','VOName'):
			for target in xpath.Evaluate(option, urls):
				if target.hasChildNodes():
					s=target.firstChild.nodeValue.encode('ascii')
				else:
					s=""
				info[option]=s

		if col == "Downtimes_top":

			# Ignore future downtimes
			sdstarttime=datetime.datetime(*time.strptime(info['Time'], "%Y-%m-%d %H:%M:%S")[0:6])
			currenttime=datetime.datetime(*time.strptime(todaystampfile, "%Y-%m-%d %H:%M:%S")[0:6])

			#Convert to epoch seconds
			sdstarttime_s=time.mktime(sdstarttime.timetuple())
			currenttime_s=time.mktime(currenttime.timetuple())

			if (sdstarttime_s-currenttime_s) > 0 :
				continue

		if not sites.has_key(info['VOName']):
			sites[info['VOName']]={}
		if not sites[info['VOName']].has_key(col):
			sites[info['VOName']][col]={}
		sites[info['VOName']][col][info['Time']]=info


filetxt= pathoutASCII + '/UsableSites_' + todaystamptofile + ".txt"

fileHandle = open ( filetxt , 'w' )    

reptime="# Usable Sites Report made on %s (UTC)\n" % todaystampfile

fileHandle.write("#\n")
fileHandle.write(reptime)
fileHandle.write("#\n")
fileHandle.write("# Usability procedure described in: https://twiki.cern.ch/twiki/bin/view/CMS/FacOps_Tier2UsableForAnalysis\n")
fileHandle.write("#\n\n")

site = sites.keys()
site.sort()

usability={}
usable={}
not_usable={}
downtime=[]

for sitename in site:
	
	if sitename.find("T3_") == 0 or sitename.find("T0_") == 0 or sitename.find("T1_") == 0: continue
       	if not sitename in SiteDB_sites: continue
       	if sitename.find("T2_CH_CAF") == 0 or sitename.find("T2_PT_LIP_Coimbra") == 0: continue

	useit=1
        down=False
	
	for col in ColumnMatrix:

		if not sites[sitename].has_key(col):
			continue
		
		items = sites[sitename][col].keys()
		items.sort()
			
		lastState= ""
		lastColor= ""
		lastBegin= ""
		lastEnd= ""
		for i in items:
			lastState=sites[sitename][col][i]['Status']
			lastBegin=sites[sitename][col][i]['Time']
			lastEnd=sites[sitename][col][i]['EndTime']
			lastColor=sites[sitename][col][i]['COLOR']

#		print sitename, col, lastState, lastBegin, lastEnd, lastColor

		if lastState != "":

			if col == "Ranking":
				if lastState == "n/a":
					useit=0
					continue
				if sitename.find("T1_") == 0 and int(lastState)<90:
					useit=0
				if sitename.find("T2_") == 0 and int(lastState)<80:
					useit=0
		      	if col == "CE_sam" and lastState == "CRITICAL":
				useit=0
	       	      	if col == "SRM_sam" and lastState == "CRITICAL":
			       	useit=0
		      	if col == "Downtimes_top" and lastColor == "1":
			       	useit=0
				down=True

	if down == True:
		downtime.append(sitename)
		
	usability[sitename]=useit
       	if usability[sitename] == 1:		
		if not usable.has_key(sitename): usable[sitename]=1
       	else:
		if not not_usable.has_key(sitename): not_usable[sitename]=0


############################################################
		
fileHandle.write("---------- USABLE SITES FOR ANALYSIS ---------- \n\n")

siteus = usable.keys()
siteus.sort()

for sitename in siteus: fileHandle.write(sitename+"\n")

fileHandle.write("\n---------- *NOT* USABLE SITES FOR ANALYSIS ---------- \n\n")

sitenous = not_usable.keys()
sitenous.sort()

for sitename in sitenous:
	if sitename in downtime: fileHandle.write(sitename+" (SD)\n")
	else: fileHandle.write(sitename+"\n")

############################################################

totalsites=len(usable)+len(not_usable)

fileHandle.write("\n--------- Statistics ---------- \n\n")
fileHandle.write(todaystamptotxt + " / " + str(len(usable)) + " usable sites" + " / " + str(len(not_usable)) + " not usable sites\n\n")

fileHandle.write("\n--------- Detailed Site Status ---------- \n\n")

for sitename in sites:
	
	if sitename.find("T3_") == 0 or sitename.find("T0_") == 0 or sitename.find("T1_") == 0: continue
       	if not sitename in SiteDB_sites:
#     		fileHandle.write("Site is not on SiteDB\n\n")
		continue
       	if sitename.find("T2_CH_CAF") == 0 or sitename.find("T2_PT_LIP_Coimbra") == 0:
#		fileHandle.write("Site shall be skipped\n\n")
		continue
	
	for col in ColumnMatrix:

		if not sites[sitename].has_key(col):
			continue
		
		items = sites[sitename][col].keys()
		items.sort()
			
		lastState= ""
		lastBegin= ""
		lastEnd= ""
		for i in items:
			lastState=sites[sitename][col][i]['Status']
			lastBegin=sites[sitename][col][i]['Time']
			lastEnd=sites[sitename][col][i]['EndTime']
		if lastState != "":
			if col == "Ranking":
				mes = sitename + "," + col + " : " + lastState + "%\n" 
			else:
				mes = sitename + "," + col + " : " + lastState + "\n" 
		       	fileHandle.write(mes)
       	if usability[sitename] == 1:		
		fileHandle.write(sitename + " is usable\n\n")
       	else:
		fileHandle.write(sitename + " is *not* usable\n\n")

#pprint.pprint(usable)
#pprint.pprint(not_usable)

fileHandle.close()

os.chdir(pathoutASCII)
slinktxt= './UsableSites.txt'
if os.path.isfile(slinktxt): os.remove(slinktxt)
os.symlink(os.path.split(filetxt)[1],slinktxt)

ProduceSiteReadinessSSBFile(usable, not_usable, fileSSB, todaystamptofile,downtime)

sys.exit(0)
