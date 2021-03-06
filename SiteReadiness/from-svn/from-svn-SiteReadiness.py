#!/usr/bin/env python

""" @author: Josep Flix (jflix@pic.es) """

# ------------------------------------------------------------
# Site Readiness States:
#                            READY (R)
#                            NOT-READY (NR)
#                            WARNING (W)
#                            SCHEDULED DOWNTIME (SD)
#
# https://twiki.cern.ch/twiki/bin/view/CMS/PADASiteCommissioning
# ------------------------------------------------------------


import sys, xml.dom.minidom, os, datetime, time, pprint, csv, pickle
from xml import xpath
from datetime import date

# To Produce Plots
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pylab import *
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.cm as cm

# OptParse
from optparse import OptionParser


usage = "usage: (example) %prog -p /home/jflix/tmp2 -c /home/jflix/MetricsCorrections.txt -u http://lhcweb.pic.es/cms -x true/false"
parser = OptionParser(usage=usage, version="%prog 1.0")
parser.add_option("-p", "--path_out", dest="path_out", help="Sets the PATH to store the produced data", metavar="PATH")
parser.add_option("-c", "--corr", dest="corr", help="Sets the ASCii file where the metrics corrections are provided", metavar="FILE")
parser.add_option("-u", "--url", dest="url", help="Sets the base URL where produced data is accessible", metavar="URL")
parser.add_option("-x", "--xml", dest="xml", help="Sets getting or not the XML files from SSB", metavar="BOOLEAN")
(options, args) = parser.parse_args()

#if len(sys.argv) != 9:
#	parser.error("incorrect number of arguments. Check needed arguments with --help")
		

todaydate = date.today()

today=datetime.datetime.utcnow()
todaystamp=today.strftime("%Y-%m-%d")
todaystampfile=today.strftime("%Y-%m-%d %H:%M:%S")
todaystampfileSSB=today.strftime("%Y-%m-%d 00:00:01")

d=datetime.timedelta(1);
yesterday=today-d
yesterdaystamp=yesterday.strftime("%Y-%m-%d")
yesterdaystampfileSSB=yesterday.strftime("%Y-%m-%d 00:00:01")
timestamphtml=today.strftime("%Y%m%d")

########################################################################################
#

basepath=os.path.split(sys.argv[0])[0]

pathN=options.path_out + "/INPUTxmls"
pathout= options.path_out + "/toSSB"
pathoutHTML= options.path_out + "/HTML"
pathoutPLOTS= options.path_out + "/PLOTS"
pathoutASCII= options.path_out + "/ASCii"

if options.xml == "true":
	GetURLs=True
else:
	if not os.path.exists(pathN):
		print
		print "WARNING: you cannot re-use the XML files as the files were not obtained before. Obtaining them..."
		print
		GetURLs=True
	else:
		GetURLs=False

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

#Corrections for Daily metrics, badly inserted on the SSB
DailyMetricsCorrected = options.corr

fileSSB= pathout + '/SiteReadiness_SSBfeed.txt'
fileDailyStat= pathoutASCII + '/Daily_HistoricStatistics.txt'
fileReadinessStat= pathoutASCII + '/SiteReadiness_HistoricStatistics.txt'

reptime="Report made on %s (UTC)\n" % todaystampfile

days=60  # Number of days to get the information from SSB -- We need these number of days to build the 30-plots view.
daysshow=21  # Number of days to get the information from SSB
dayssc=7  # Number of last days to build the Site Commissioning status
hours=str(days*24)

CountWeekendsT2=False

#
########################################################################################


# URLs with SSB inputs --------------------------------------------------------------------------------------

#webserver="http://dashb-ssb-dev.cern.ch"
webserver="http://dashb-ssb.cern.ch"

# Downtimes/Maintenances from SAM DB
#Downtimes_sam= webserver + '/dashboard/request.py/getplotdata?columnid=71&batch=1&time=' + hours 
#Downtimes_top = "http://dashb-cms-vo-feed.cern.ch/dashboard/request.py/getplotdata?columnid=121&batch=1&time=" + hours
Downtimes_top = webserver + '/dashboard/request.py/getplotdata?columnid=121&batch=1&time=' + hours

# Job Robot
SiteCommJR= webserver + '/dashboard/request.py/getplotdata?columnid=27&batch=1&time=' + hours
SiteCommJRDB= webserver + '/dashboard/request.py/getplotdata?columnid=119&batch=1&time=' + hours 

# HammerCloud
HammerCloud= webserver + '/dashboard/request.py/getplotdata?columnid=135&batch=1&time=' + hours

# SAM availability
# tmp SAMAvailability= webserver + '/dashboard/request.py/siteviewhistory?columnid=40&time=' + hours + "&fullstatus=1"
SAMNagiosAvailability= webserver + '/dashboard/request.py/getplotdata?columnid=116&batch=1&time=' + hours
SUMAvailability= webserver + '/dashboard/request.py/getplotdata?columnid=126&batch=1&time=' + hours

# DDT-commissioned links
T1linksfromT0= webserver + '/dashboard/request.py/getplotdata?columnid=33&batch=1&time=' + hours
T1linkstoT2s= webserver + '/dashboard/request.py/getplotdata?columnid=34&batch=1&time=' + hours
T1linksfromtoT1s= webserver + '/dashboard/request.py/getplotdata?columnid=35&batch=1&time=' + hours
T2linkstoT1s= webserver + '/dashboard/request.py/getplotdata?columnid=36&batch=1&time=' + hours
T2linksfromT1s= webserver + '/dashboard/request.py/getplotdata?columnid=37&batch=1&time=' + hours

# Good links based on data transfer qualities
GoodT1linksfromT0= webserver + '/dashboard/request.py/getplotdata?columnid=74&batch=1&time=' + hours
GoodT1linksfromT1s= webserver + '/dashboard/request.py/getplotdata?columnid=75&batch=1&time=' + hours
GoodT1linksfromT2s= webserver + '/dashboard/request.py/getplotdata?columnid=76&batch=1&time=' + hours
GoodT1linkstoT1s= webserver + '/dashboard/request.py/getplotdata?columnid=77&batch=1&time=' + hours
GoodT1linkstoT2s= webserver + '/dashboard/request.py/getplotdata?columnid=80&batch=1&time=' + hours
GoodT2linksfromT1s= webserver + '/dashboard/request.py/getplotdata?columnid=78&batch=1&time=' + hours
GoodT2linkstoT1s= webserver + '/dashboard/request.py/getplotdata?columnid=79&batch=1&time=' + hours

# Is Site in SiteDB?
IsSiteInSiteDB= webserver + '/dashboard/request.py/getplotdata?columnid=100&batch=1&time=' + hours
IsSiteInSiteDB_validsince=date(2009,11,03)


ColumnMatrix = {}  # SSB URLs Matrix
#ColumnMatrix["Downtimes_sam"]=Downtimes_sam
ColumnMatrix["Downtimes_top"]=Downtimes_top
ColumnMatrix["JobRobot"]=SiteCommJR
ColumnMatrix["JobRobotDB"]=SiteCommJRDB
ColumnMatrix["HammerCloud"]=HammerCloud
# tmp ColumnMatrix["SAMAvailability"]=SAMAvailability
#ColumnMatrix["SAMNagiosAvailability"]=SAMNagiosAvailability
ColumnMatrix["SUMAvailability"]=SUMAvailability
ColumnMatrix["T1linksfromT0"]=T1linksfromT0
ColumnMatrix["T1linkstoT2s"]=T1linkstoT2s
ColumnMatrix["T1linksfromtoT1s"]=T1linksfromtoT1s
ColumnMatrix["T2linksfromT1s"]=T2linksfromT1s
ColumnMatrix["T2linkstoT1s"]=T2linkstoT1s
ColumnMatrix["GoodT1linksfromT0"]=GoodT1linksfromT0
ColumnMatrix["GoodT1linksfromT1s"]=GoodT1linksfromT1s
ColumnMatrix["GoodT1linksfromT2s"]=GoodT1linksfromT2s
ColumnMatrix["GoodT1linkstoT1s"]=GoodT1linkstoT1s
ColumnMatrix["GoodT1linkstoT2s"]=GoodT1linkstoT2s
ColumnMatrix["GoodT2linksfromT1s"]=GoodT2linksfromT1s
ColumnMatrix["GoodT2linkstoT1s"]=GoodT2linkstoT1s
ColumnMatrix["IsSiteInSiteDB"]=IsSiteInSiteDB

# Add the color name <-> color index here
MatrixStatusColors = {}  # SSB XML Status colors
#MatrixStatusColors["Downtimes_sam"]={"4":"white", "5":"green", "6":"brown", "7":"yellow"}
MatrixStatusColors["Downtimes_top"]={"1":"brown", "4":"yellow", "5":"green", "6":"grey", "8":"white"}
MatrixStatusColors["JobRobot"]={"5":"green", "3":"red", "6":"white"}
MatrixStatusColors["JobRobotDB"]={"5":"green", "3":"red", "6":"white"}
MatrixStatusColors["HammerCloud"]={"5":"green", "3":"red", "6":"white", "8":"white"}
# tmp MatrixStatusColors["SAMAvailability"]={"4":"green", "5":"red"}
#MatrixStatusColors["SAMNagiosAvailability"]={"5":"green", "3":"red"}
MatrixStatusColors["SUMAvailability"]={"5":"green", "3":"red"} #20120215: Seguro?
MatrixStatusColors["T1linksfromT0"]={"5":"green", "3":"red"}
MatrixStatusColors["T1linksfromtoT1s"]={"5":"green", "3":"red"}
MatrixStatusColors["T1linkstoT2s"]={"5":"green", "3":"red"}
MatrixStatusColors["T2linksfromT1s"]={"5":"green", "3":"red"}
MatrixStatusColors["T2linkstoT1s"]={"5":"green", "3":"red"}
MatrixStatusColors["GoodT1linksfromT0"]={"3":"red", "5":"green"}
MatrixStatusColors["GoodT1linksfromT1s"]={"3":"red", "5":"green"}
MatrixStatusColors["GoodT1linksfromT2s"]={"3":"red", "5":"green"}
MatrixStatusColors["GoodT1linkstoT1s"]={"3":"red", "5":"green"}
MatrixStatusColors["GoodT1linkstoT2s"]={"3":"red", "5":"green"}
MatrixStatusColors["GoodT2linksfromT1s"]={"3":"red", "5":"green"}
MatrixStatusColors["GoodT2linkstoT1s"]={"3":"red", "5":"green"}
MatrixStatusColors["IsSiteInSiteDB"]={"5":"green"}

criterias = { "T0": [ 'JobRobot',
		      'JobRobotDB',
		      'HammerCloud',
		      'SAMNagiosAvailability',
		      'SUMAvailability'],
	      "T1": [ 'JobRobot',
		      'JobRobotDB',
		      'HammerCloud',
		      'SAMNagiosAvailability',
		      'SUMAvailability',
		      'T1linksfromT0',
		      'T1linksfromtoT1s',
		      'T1linkstoT2s',
		      'GoodT1linksfromT0',
		      'GoodT1linksfromT1s',
		      'GoodT1linksfromT2s',
		      'GoodT1linkstoT1s',
		      'GoodT1linkstoT2s'], 
	      "T2": [ 'JobRobot',
		      'JobRobotDB',
		      'HammerCloud',
		      'SAMNagiosAvailability',
		      'SUMAvailability',
		      'T2linksfromT1s',
		      'T2linkstoT1s',
		      'GoodT2linksfromT1s',
		      'GoodT2linkstoT1s'],
	      "T3": [ 'JobRobot',
	              'JobRobotDB',
		      'HammerCloud',
		      'SAMNagiosAvailability',
		      'SUMAvailability']}

colors = { "R":"green",
	   "NR":"red",
	   "n/a":"white",
	   "W":"yellow" ,
	   "SD":"brown",
	   "UD":"silver",
	   "CE-SD":"brown",
	   "SE-SD":"brown",
	   "~":"yellow",
	   "und":"black",
	   " ":"white",
	   "E": "red",
	   "O":"green" ,
	   "n/a*":"white"}
	
metorder = {    "01":"Downtimes_top",
		"02": "HammerCloud",
		"03":"SUMAvailability",
		"04":"GoodT1linksfromT0",
		"05":"GoodT1linksfromT1s",
		"06":"GoodT1linksfromT2s",
		"07":"GoodT1linkstoT1s",
		"08":"GoodT1linkstoT2s",
		"09":"GoodT2linksfromT1s",
		"10":"GoodT2linkstoT1s",
		"11":"T1linksfromT0",
		"12":"T1linksfromtoT1s",
		"13":"T1linkstoT2s",
		"14":"T2linksfromT1s",
		"15":"T2linkstoT1s",}

metlegends = {  "Downtimes_top":"Maintenance",
		"SAMNagiosAvailability":"Old SAM Availability", 
		"SUMAvailability":"SAM Availability", 
		"JobRobot":"Job Robot", 
		"JobRobotDB":"Job Robot 'DB' (info)",
		"HammerCloud":"HammerCloud",
		"T1linksfromT0":"Active T1 links from T0",
		"T1linksfromtoT1s":"Active T1 links from/to T1s",
		"T1linkstoT2s":"Active T1 links to T2s",
		"T2linksfromT1s":"Active T2 links from T1s",
		"T2linkstoT1s":"Active T2 links to T1s",
		"GoodT1linksfromT0":"Good T1 links from T0",
		"GoodT1linksfromT1s":"Good T1 links from T1s",
		"GoodT1linksfromT2s":"Good T1 links from T2s",
		"GoodT1linkstoT1s":"Good T1 links to T1s",
		"GoodT1linkstoT2s":"Good T1 links to T2s",
		"GoodT2linksfromT1s":"Good T2 links from T1s",
		"GoodT2linkstoT1s":"Good T2 links to T1s"}

#
# Functions : these should go soon on a module
#
# -----------------------------------------------------------------------------------------------------------

def GetCriteriasList(sitename, criterias):
	tier=sitename.split("_")[0]	
	return criterias[tier]

def CorrectGlobalMatrix(sitename,day,value):

	if sitename.find('T0_CH_CERN') == 0: 
		return 'n/a*'
	if sitename.find('_CH_CAF') == 0: 
		return 'n/a*'
	
	if sitename == 'T2_PL_Cracow':
		return 'n/a*'
		
       	if sitename == 'T1_DE_FZK':
		thedate=date(int(day[0:4]),int(day[5:7]),int(day[8:10]))
		fzk_notvalidsince=date(2009,9,25)

		if (thedate-fzk_notvalidsince).days > 0:
			return 'n/a*'
		
       	if sitename == 'T1_DE_KIT':
		thedate=date(int(day[0:4]),int(day[5:7]),int(day[8:10]))
		kit_validsince=date(2009,9,25)

		if (thedate-kit_validsince).days < 0:
			return 'n/a*'
		
	return value
	

def SiteExist(sites, sitename, date):
	
	items = sites[sitename]['IsSiteInSiteDB'].keys()
	items.sort()
	
	for coldate in items:
		if coldate.find(date) == 0:
			print coldate, sitename, sites[sitename]['IsSiteInSiteDB'][coldate]['Status']
						
def CheckInsertionDates(sites):
	
	items = sites.keys()
	items.sort()

	for sitename in items: 

		colitems = sites[sitename].keys()
		colitems.sort()
		
		for col in colitems:

			datitems = sites[sitename][col].keys()
			datitems.sort()
		
			for coldate in datitems:
				print col, coldate

def ShiftDayForMetric(datestamp,col):

	if col == "JobRobot" or col=="JobRobotDB" or col=="HammerCloud" or col == "SAMAvailability" or col == "SAMNagiosAvailability" or col == "SUMAvailability" or col.find("Good")==0:
		d=datetime.timedelta(1)
		yesterday=datestamp-d
		return yesterday.strftime("%Y-%m-%d")
	else:
		return datestamp.strftime("%Y-%m-%d")
	
	

def GetDailyMetricStatus(sites, SiteCommMatrix, MatrixStatusColors):

	prog = progressBar(0, 100, 77)
	iprog=0

	for sitename in sites:

		iprog+=100./len(sites)

		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()

		if not SiteCommMatrix.has_key(sitename):
			SiteCommMatrix[sitename]={}

		for col in ColumnMatrix:

			if not sites[sitename].has_key(col) or col == 'Downtimes_sam' or col == 'Downtimes_top':
				continue

			for i in range(0,days+1):
				
				d=datetime.timedelta(days-i);
				dayloop=today-d	
				dayloopstamp=dayloop.strftime("%Y-%m-%d")

				infocol = {}
				infocol['Status'] = 'n/a'
				infocol['Color'] = 'white'
				infocol['URL'] = ' '
				infocol['validity'] = 0

				if not SiteCommMatrix[sitename].has_key(dayloopstamp):
					SiteCommMatrix[sitename][dayloopstamp]={}
				if not SiteCommMatrix[sitename][dayloopstamp].has_key(col):
					SiteCommMatrix[sitename][dayloopstamp][col]={}

				SiteCommMatrix[sitename][dayloopstamp][col]=infocol

			items = sites[sitename][col].keys()
			items.sort()

			for coldate in items:

				xmltime=datetime.datetime(*time.strptime(sites[sitename][col][coldate]['Time'], "%Y-%m-%d %H:%M:%S")[0:6])
				xmlendtime=datetime.datetime(*time.strptime(sites[sitename][col][coldate]['EndTime'], "%Y-%m-%d %H:%M:%S")[0:6])

				startxmldatetmp=xmltime.strftime("%Y-%m-%d 00:00:00")
				startxmldate=datetime.datetime(*time.strptime(startxmldatetmp, "%Y-%m-%d %H:%M:%S")[0:6])

				EndTXML = True
				i=0
				
				while ( EndTXML ):
					
					d=datetime.timedelta(i);
					i+=1
					dayloop=startxmldate+d	
					dayloopstamp=dayloop.strftime("%Y-%m-%d")
					dayloopstamp2=dayloop.strftime("%Y-%m-%d 00:00:00")
					looptime=datetime.datetime(*time.strptime(dayloopstamp2, "%Y-%m-%d %H:%M:%S")[0:6])

					if dayloop > today:
						EndTXML=False
						continue
						
					diff1 = xmltime-looptime
					diff1s=(diff1.days*86400+diff1.seconds)
					diff2 = xmlendtime-looptime
					diff2s=(diff2.days*86400+diff2.seconds)
					diff3 = xmlendtime-xmltime
					diff3s=(diff3.days*86400+diff3.seconds)
					if diff1s<=0 and diff2s>0:
						if diff2s>=86400: validity=86400
						else: validity=diff2s
					if diff1s>0 and diff1s<86400:
						if diff2s>86400: validity=86400-diff1s
						else: validity=diff3s
					if diff1s<0 and diff2s<=0:
						EndTXML=False
						continue

					if MatrixStatusColors[col][sites[sitename][col][coldate]['COLOR']] == "green":
						status=sites[sitename][col][coldate]['Status']
						statusu=sites[sitename][col][coldate]['URL']
						statusc='green'
						if sites[sitename][col][coldate]['Status']=="pend":
							statusc='orange'
							status='-'
					elif MatrixStatusColors[col][sites[sitename][col][coldate]['COLOR']] == "white":
						statusu=' '
						status='n/a'
						statusc='white'
					elif MatrixStatusColors[col][sites[sitename][col][coldate]['COLOR']] == "red":
						status=sites[sitename][col][coldate]['Status']
						statusu=sites[sitename][col][coldate]['URL']
						statusc='red'
					else:
						status='???'
						statusu='???'
						statusc='white'

					infocol = {}
					infocol['Status'] = status
					infocol['Color'] = statusc
					infocol['URL'] = statusu
					infocol['validity'] = validity

					dayloopstamp3=ShiftDayForMetric(dayloop,col)
					todayst=date(int(todaystamp[0:4]),int(todaystamp[5:7]),int(todaystamp[8:10]))
					dayloop3=date(int(dayloopstamp3[0:4]),int(dayloopstamp3[5:7]),int(dayloopstamp3[8:10]))

					if abs((dayloop3-todayst).days) > days:
						continue

					if SiteCommMatrix[sitename][dayloopstamp3][col].has_key('validity'):
						if validity>SiteCommMatrix[sitename][dayloopstamp3][col]['validity']:
							SiteCommMatrix[sitename][dayloopstamp3][col]=infocol
					else:
						SiteCommMatrix[sitename][dayloopstamp3][col]=infocol	
								
					if dayloopstamp == todaystamp:
						infocol = {}
						infocol['Status'] = ' '
						infocol['Color'] = 'white'
						infocol['URL'] = ' '
						infocol['validity'] = '0' 						
						SiteCommMatrix[sitename][dayloopstamp][col]=infocol

	sys.stdout.write("\n")
	sys.stdout.flush()


def FilterSitesInTablesPlots(sitename, matrix=[], matrixgl=[]):

	if not matrix[sitename][yesterdaystamp].has_key('IsSiteInSiteDB'): return 0
	if matrix[sitename][yesterdaystamp]['IsSiteInSiteDB']['Color'] == 'white': return 0
		
	if sitename.find("T1_DE_FZK") == 0 : return 0
	if sitename.find("T2_CH_CAF") == 0 : return 0
	if sitename.find("T1_US_FNAL_Disk") == 0 : return 0
	if sitename.find("T2_TR_ULAKBIM") == 0 : return 0
	if sitename.find("_Disk") >= 0 : return 0

	if sitename.find("T3_") == 0 : return 0

	dt = SiteCommGlobalMatrix[sitename].keys()
	dt.sort()
	j=0
	k=0
	for i in dt:
		j+=1
		if matrixgl[sitename][i].find("n/a") == 0 or matrixgl[sitename][i].find("n/a*") == 0: k+=1
	if (j) == k : return 0
	
	return 1


def SSBXMLParser(sites, ColumnMatrix):

	prog = progressBar(0, 100, 77)
	iprog=0

	ColumnItems = ColumnMatrix.keys()
	ColumnItems.sort()

	for col in ColumnItems:

		iprog+=100./len(ColumnItems)

		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()

		url=ColumnMatrix[col]

		fileN=pathN+"/"+col+".xml"

		if GetURLs == True:
			print "Column %s - Getting the url %s" % (col, url)
			os.system("curl -s -H 'Accept: text/xml'  '%s' > %s" % (url,fileN))
	
		f=file(fileN,'r')
		t= xml.dom.minidom.parse(f)
		f.close()

		mes = "/getplotdata/csvdata/item"

		for urls in xpath.Evaluate(mes, t):

			info={}
			for option in ('Status', "COLOR", 'Time', 'EndTime','VOName','URL'):
				for target in xpath.Evaluate(option, urls):
					if target.hasChildNodes():
						s=target.firstChild.nodeValue.encode('ascii')
					else:
						s=""
					info[option]=s

                        if info['VOName'].find("T3_FR-IPNL") == 0: continue
			if info['VOName'].find("T2_TR_ULAKBIM") == 0: continue
			
			if not sites.has_key(info['VOName']):
				sites[info['VOName']]={}
			if not sites[info['VOName']].has_key(col):
				sites[info['VOName']][col]={}
			sites[info['VOName']][col][info['Time']]=info

			# Correct information from JobRobot --> 100%(600) -> 100% (example)

			if col=="JobRobotDB" or col=="HammerCloud":
				if sites[info['VOName']][col][info['Time']]['Status'] == "n/a":
					sites[info['VOName']][col][info['Time']]['Status']="n/a"
				else:
					tmp=int(float(sites[info['VOName']][col][info['Time']]['Status']))
					sites[info['VOName']][col][info['Time']]['Status']=str(tmp)

			if col=="JobRobot" or col == "JobRobotDB" or col=="HammerCloud":
				tmp=sites[info['VOName']][col][info['Time']]['Status']
				tmp2=tmp.split("(")[0]
				if not tmp2.find("%") == 0 and not tmp2.find("n/a") == 0: tmp2+="%"
				sites[info['VOName']][col][info['Time']]['Status']=tmp2
			if col=="SAMAvailability" or col=="SAMNagiosAvailability" or col=="SUMAvailability":
				tmp=sites[info['VOName']][col][info['Time']]['Status']
				if col=="SUMAvailability": tmp=str(int(round(float(tmp))))
				if not tmp.find("%") == 0: tmp+="%"
				sites[info['VOName']][col][info['Time']]['Status']=tmp

	sys.stdout.write("\n")
	sys.stdout.flush()

# -----------------------------------------------------------------------------------------------------------

class progressBar:
	def __init__(self, minValue = 0, maxValue = 10, totalWidth=12):
		self.progBar = "[]"   # This holds the progress bar string
		self.min = minValue
		self.max = maxValue
		self.span = maxValue - minValue
		self.width = totalWidth
		self.amount = 0       # When amount == max, we are 100% done
		self.updateAmount(0)  # Build progress bar string

	def updateAmount(self, newAmount = 0):
		if newAmount < self.min: newAmount = self.min
		if newAmount > self.max: newAmount = self.max
		self.amount = newAmount
		
		# Figure out the new percent done, round to an integer
		diffFromMin = float(self.amount - self.min)
		percentDone = (diffFromMin / float(self.span)) * 100.0
		percentDone = round(percentDone)
		percentDone = int(percentDone)
		
		# Figure out how many hash bars the percentage should be
		allFull = self.width - 2
		numHashes = (percentDone / 100.0) * allFull
		numHashes = int(round(numHashes))
		
		# build a progress bar with hashes and spaces
		self.progBar = "[" + '#'*numHashes + ' '*(allFull-numHashes) + "]"

		# figure out where to put the percentage, roughly centered
		percentPlace = (len(self.progBar) / 2) - len(str(percentDone))
		percentString = str(percentDone) + "%"

		# slice the percentage into the bar
		self.progBar = self.progBar[0:percentPlace] + percentString + self.progBar[percentPlace+len(percentString):]

	def __str__(self):
		return str(self.progBar)

def GetDailyScheduledDowntimeTopologyStatus(sites, SiteCommMatrix, MatrixStatusColors):

	# Leer Downtimes Topology (por ahora uso Time y EndTime para decidir cuanto duran los Downtimes)
	# por defecto todos los dias son Ok, y uso Time y EndTime para asignar los Downtimes.

	# Reading the Topology Downtimes

	ColumnMatrixD = {}  # SSB URLs Matrix
	ColumnMatrixD['Downtimes_top']=Downtimes_top

	prog = progressBar(0, 100, 77)
	iprog=0

	for sitename in sites:

		iprog+=100./len(sites)
		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()

		if not SiteCommMatrix.has_key(sitename):
			SiteCommMatrix[sitename]={}
		
		for col in ColumnMatrixD:

			infocol = {}

			if not sites[sitename].has_key(col):
				sites[sitename][col] = {}
			
			for i in range(0,days+1):
			
				d=datetime.timedelta(days-i);
				dayloop=today-d
				dayloopstamp=dayloop.strftime("%Y-%m-%d")

				if not SiteCommMatrix[sitename].has_key(dayloopstamp):
					SiteCommMatrix[sitename][dayloopstamp]={}

				infocol['Status'] = "Up"
				infocol['Color'] = "green"
				infocol['URL'] = ' ' 
				SiteCommMatrix[sitename][dayloopstamp][col]=infocol

			items = sites[sitename][col].keys()
			items.sort()
			
			for stdate in items:

				if MatrixStatusColors[col][sites[sitename][col][stdate]['COLOR']] == "white" or  MatrixStatusColors[col][sites[sitename][col][stdate]['COLOR']] == "green":
					continue

				sttdate=stdate[0:stdate.find(" ")]
				enddate=sites[sitename][col][stdate]['EndTime'][0:sites[sitename][col][stdate]['EndTime'].find(" ")]
				cl=sites[sitename][col][stdate]['COLOR']

				for i in range(0,days+1):
			
					d=datetime.timedelta(days-i);
					dayloop=today-d
					dayloopstamp=dayloop.strftime("%Y-%m-%d")

					kk=0

					if stdate.find(dayloopstamp) == 0:

						wloop=True
						while (wloop):

							infocol266={}
							
							c = datetime.datetime(*time.strptime(sttdate,"%Y-%m-%d")[0:5])
							d=datetime.timedelta(kk);
							dayloop=c+d
							dayloopstamp=dayloop.strftime("%Y-%m-%d")

							if SiteCommMatrix[sitename].has_key(col):
								if SiteCommMatrix[sitename][col].has_key(dayloopstamp):
									if SiteCommMatrix[sitename][col][dayloopstamp].has_key('Color'):
										if SiteCommMatrix[sitename][col][dayloopstamp].has_key('Color') == 'brown':
											kk+=1
											continue

							if MatrixStatusColors[col][sites[sitename][col][stdate]['COLOR']] == 'brown':
								infocol266['Color'] = 'brown'
								infocol266['Status'] = 'SD'
								infocol266['URL'] = sites[sitename][col][stdate]['URL']
	       						if MatrixStatusColors[col][sites[sitename][col][stdate]['COLOR']] == 'grey':
								if sites[sitename][col][stdate]['Status'].find("OUTAGE UNSCHEDULED") == 0:
									infocol266['Color'] = 'silver'
									infocol266['Status'] = 'UD'
									infocol266['URL'] = sites[sitename][col][stdate]['URL']
								else:
									infocol266['Color'] = 'yellow'
									infocol266['Status'] = '~'
									infocol266['URL'] = sites[sitename][col][stdate]['URL']
							if MatrixStatusColors[col][sites[sitename][col][stdate]['COLOR']] == 'yellow':
								infocol266['Color'] = 'yellow'
								infocol266['Status'] = '~'
								infocol266['URL'] = sites[sitename][col][stdate]['URL']
							
							if dayloop > today: break # ignore future downtimes

							SiteCommMatrix[sitename][dayloopstamp][col]=infocol266

							kk+=1

							if (dayloopstamp == enddate): wloop=False
						
			infocol27={}
			infocol27['Status'] = ' '
			infocol27['URL'] = ' '
			infocol27['Color'] = 'white'
			SiteCommMatrix[sitename][todaystamp][col]=infocol27

	sys.stdout.write("\n")
	sys.stdout.flush()

def CorrectDailyMetricsFromASCIIFile(sites, SiteCommMatrix, DailyMetricsCorrected):
	
	#
	# Plain text to be used to modify SSB inputs to build SiteReadiness tables
	# Useful to correct bugs and/or modify daily metric values for a given site or all sites
	#

	prog = progressBar(0, 100, 77)
	iprog=0
	
	f=open(DailyMetricsCorrected)
	flen=len(f.readlines())
	f.close()
	
	Reader = csv.reader(open(DailyMetricsCorrected), delimiter=',', quotechar='|')

	for row in Reader:
	
		iprog+=100./flen
		
		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()

		infomod = {}

		if len(row)==0: continue # skip empty lines
		if row[0].find("#")==0: continue # skip headers 
		if row[0] == 'ALL SITES':
			for sitename in sites:
				infomod['Status'] = row[4] + '*'
				infomod['Color'] = row[3]
				if SiteCommMatrix[sitename].has_key(row[1]):
					SiteCommMatrix[sitename][row[1]][row[2]]=infomod
		elif row[0] == 'T1_*':
			for sitename in sites:
				if sitename.find("T1_") == 0: 
					infomod['Status'] = row[4] + '*'
					infomod['Color'] = row[3]
					if SiteCommMatrix[sitename].has_key(row[1]):
						SiteCommMatrix[sitename][row[1]][row[2]]=infomod
		elif row[0] == 'T2_*':
			for sitename in sites:
				if sitename.find("T2_") == 0: 
					infomod['Status'] = row[4] + '*'
					infomod['Color'] = row[3]
					if SiteCommMatrix[sitename].has_key(row[1]):
						SiteCommMatrix[sitename][row[1]][row[2]]=infomod
		else:
			infomod['Status'] = row[4] + '*'
			infomod['Color'] = row[3]
			if SiteCommMatrix.has_key(row[0]):
				if SiteCommMatrix[row[0]].has_key(row[1]):
					SiteCommMatrix[row[0]][row[1]][row[2]]=infomod
	sys.stdout.write("\n")
	sys.stdout.flush()


def EvaluateDailyStatus(SiteCommMatrix, SiteCommMatrixT1T2, criterias):
	
	# Daily Metrics

	prog = progressBar(0, 100, 77)
	iprog=0

	for sitename in SiteCommMatrix:

		iprog+=100./len(SiteCommMatrix)
		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()

		SiteCommMatrixT1T2[sitename]={}

		items = SiteCommMatrix[sitename].keys()
		items.sort()

		status=' '

		for day in items:
			
			status = 'O'
			
			for crit in GetCriteriasList(sitename, criterias):

				if not SiteCommMatrix[sitename][day].has_key(crit):

					infocol3={}
					infocol3['Status']='n/a'
					infocol3['Color']='white'
					SiteCommMatrix[sitename][day][crit] = infocol3

				thedate=date(int(day[0:4]),int(day[5:7]),int(day[8:10]))
				sam_change=date(2011,5,11)
				sum_change=date(2012,2,13)

				if (thedate-sam_change).days > 0 and crit == "SAMAvailability": continue
				if (thedate-sam_change).days <= 0 and crit == "SAMNagiosAvailability": continue

				if (thedate-sum_change).days > 0 and crit == "SAMNagiosAvailability": continue
				if (thedate-sum_change).days <= 0 and crit == "SUMAvailability": continue

				jrdb_change=date(2012,3,28)
				if (thedate-jrdb_change).days > 0 and crit == "JobRobot": continue
				if (thedate-jrdb_change).days <= 0 and crit == "JobRobotDB": continue

				hc_change=date(2012,4,17)
				if (thedate-hc_change).days > 0 and (crit == "JobRobot" or crit == "JobRobotDB"): continue
				if (thedate-hc_change).days <= 0 and crit == "HammerCloud": continue

				if SiteCommMatrix[sitename][day][crit]['Color'] == 'red':
					status = 'E'

			if SiteCommMatrix[sitename][day]['Downtimes_top']['Color'] == 'brown':
				status = 'SD'

			testdate=date(int(day[0:4]),int(day[5:7]),int(day[8:10]))
			sitedbtimeint = testdate-IsSiteInSiteDB_validsince

			# exclude sites that are not in SiteDB
			if sitedbtimeint.days >= 0:
				if SiteCommMatrix[sitename][day].has_key('IsSiteInSiteDB'):
					if SiteCommMatrix[sitename][day]['IsSiteInSiteDB']['Color'] == 'white':
						status = 'n/a'

			if day == todaystamp:
				status = ' '

			SiteCommMatrixT1T2[sitename][day]=status

	sys.stdout.write("\n")
	sys.stdout.flush()


def EvaluateSiteReadiness(SiteCommMatrixT1T2, SiteCommGlobalMatrix):

	sitesit = SiteCommMatrixT1T2.keys()
	sitesit.sort()
	
	prog = progressBar(0, 100, 77)
	iprog=0

	for sitename in sitesit:

		iprog+=100./len(sitesit)
		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()

		if not SiteCommGlobalMatrix.has_key(sitename):
			SiteCommGlobalMatrix[sitename]={}

		tier=sitename.split("_")[0]
		
		for i in range(0,days-dayssc):
	
			d=datetime.timedelta(i);
			dayloop=today-d	
			dayloopstamp=dayloop.strftime("%Y-%m-%d")
			dm1=datetime.timedelta(1)
			dayloopm1=dayloop-dm1
			dayloopstampm1=dayloopm1.strftime("%Y-%m-%d")
			dm2=datetime.timedelta(2)
			dayloopm2=dayloop-dm2
			dayloopstampm2=dayloopm2.strftime("%Y-%m-%d")
			
			statusE=0
		
			for j in range(0,dayssc):

				dd=datetime.timedelta(j);
				dayloop2=dayloop-dd
				dayloopstamp2=dayloop2.strftime("%Y-%m-%d")

				dayofweek2=dayloop2.weekday()
				
				if SiteCommMatrixT1T2[sitename][dayloopstamp2] == 'E':
					if ( tier == "T2" or tier == "T3") and (dayofweek2 == 5 or dayofweek2 == 6):
						if CountWeekendsT2 == False: # skip Errors on weekends for T2s
							continue
					statusE+=1

			status="n/a"
			colorst="white"

			if statusE > 2:
				status="NR"
				colorst="red"
			if SiteCommMatrixT1T2[sitename][dayloopstamp] == 'E' and statusE <= 2 :
				status="W"
				colorst="yellow"
			if SiteCommMatrixT1T2[sitename][dayloopstamp] == 'O' and statusE <= 2 :
				status="R"
				colorst="green"
			if SiteCommMatrixT1T2[sitename][dayloopstamp] == 'O' and SiteCommMatrixT1T2[sitename][dayloopstampm1] == 'O':
				status="R"
				colorst="green"
			if SiteCommMatrixT1T2[sitename][dayloopstamp] == 'SD':
				status='SD'
				colorst="brown"
		
			SiteCommGlobalMatrix[sitename][dayloopstamp] = status

		if ( tier == "T2" or tier == "T3") :

			for i in range(0,days-dayssc):
	
				d=datetime.timedelta(i);
				dsc=datetime.timedelta(days-dayssc-1);
				dayloop=today-dsc+d
				dayofweek=dayloop.weekday()
				dayloopstamp=dayloop.strftime("%Y-%m-%d")
				dm1=datetime.timedelta(1)
				dayloopm1=dayloop-dm1
				dayloopstampm1=dayloopm1.strftime("%Y-%m-%d")

				if SiteCommMatrixT1T2[sitename][dayloopstamp] == 'E':
					if dayofweek == 5 or dayofweek == 6: # id. weekends
						if CountWeekendsT2 == False: # skip Errors on weekends for T2s
							if i == 0 or i == 1:
								SiteCommGlobalMatrix[sitename][dayloopstamp] == 'R'
								continue
							if SiteCommGlobalMatrix[sitename][dayloopstampm1] == 'SD':
								SiteCommGlobalMatrix[sitename][dayloopstamp] = 'R'
							else:
								SiteCommGlobalMatrix[sitename][dayloopstamp] = SiteCommGlobalMatrix[sitename][dayloopstampm1]
						

	sys.stdout.write("\n")
	sys.stdout.flush()

        ##############################
	# put in blank current day   #
        ##############################

        for sitename in SiteCommMatrixT1T2:
		for col in ColumnMatrix:
			if SiteCommMatrix[sitename][todaystamp].has_key(col):
				SiteCommMatrix[sitename][todaystamp][col]['Status'] = ' '
				SiteCommMatrix[sitename][todaystamp][col]['Color'] = 'white'
				SiteCommGlobalMatrix[sitename][todaystamp] = ' '

        ####################################################################
	# Correct some known sites metrics
        ####################################################################

	for sitename in SiteCommGlobalMatrix:
		for dt in SiteCommGlobalMatrix[sitename]:
			SiteCommGlobalMatrix[sitename][dt]=CorrectGlobalMatrix(sitename, dt, SiteCommGlobalMatrix[sitename][dt])
	for sitename in SiteCommMatrixT1T2:
		for dt in SiteCommMatrixT1T2[sitename]:
			SiteCommMatrixT1T2[sitename][dt]=CorrectGlobalMatrix(sitename, dt, SiteCommMatrixT1T2[sitename][dt])

def ProduceSiteReadinessSSBFile(SiteCommGlobalMatrix, fileSSB):

	fileHandle = open ( fileSSB , 'w' )
	
	sitesit = SiteCommGlobalMatrix.keys()
	sitesit.sort()
	
	prog = progressBar(0, 100, 77)
	iprog=0

	SRMatrixColors = { "R":"green", "W":"yellow", "NR":"red", "SD":"brown", " ":"white", "n/a":"white", "n/a*":"white" }

	for sitename in sitesit:

		iprog+=100./len(sitesit)
		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()

		if not FilterSitesInTablesPlots(sitename, SiteCommMatrix, SiteCommGlobalMatrix) : continue

		status=SiteCommGlobalMatrix[sitename][yesterdaystamp]
		colorst=SRMatrixColors[status]

		if options.url.find("pic.es") > 0:
			linkSSB= options.url + "/SiteReadinessReports/SiteReadinessReport_" + timestamphtml + '.html'
		elif options.url.find("cern.ch") > 0 :
			linkSSB= options.url + "/SiteReadiness/HTML/SiteReadinessReport_" + timestamphtml + '.html'
		else:
			linkSSB = "unknown"

		tofile=todaystampfileSSB + '\t' + sitename + '\t' + status + '\t' + colorst + '\t' + linkSSB + "#" + sitename + "\n"
		fileHandle.write(tofile)
		
	fileHandle.close()

	sys.stdout.write("\n")
	sys.stdout.flush()


def ProduceSiteReadinessHTMLViews(SiteCommGlobalMatrix, metorder, metlegends, colors, pathoutHTML):

        ####################################################################
	# Print Site html view  -- Not all historical data (only 15 days)
        ####################################################################

	colspans1 = str(daysshow+1)
	colspans2 = str(daysshow+1)
	colspans22 = str(daysshow+2)
	colspans3 = str(dayssc)
	colspans4 = str(dayssc)
	colspans5 = str(daysshow-dayssc)

	dw=45
	mw=325

	tablew = str((daysshow)*dw+mw)
	dayw = str(dw)
	metricw = str(mw)
	daysw = str((daysshow)*dw)
	scdaysw1 = str((dayssc)*dw)
	scdaysw = str((dayssc)*dw)

	filehtml= pathoutHTML + '/SiteReadinessReport_' + timestamphtml +'.html'
	fileHandle = open ( filehtml , 'w' )    

	fileHandle.write("<html><head><title>CMS Site Readiness</title><link type=\"text/css\" rel=\"stylesheet\" href=\"./style-css-reports.css\"/></head>\n")
	fileHandle.write("<body><center>\n")

	sitesit = SiteCommGlobalMatrix.keys()
	sitesit.sort()

	prog = progressBar(0, 100, 77)
	iprog=0

	for sitename in sitesit:

		iprog+=100./len(sitesit)
		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()

		if FilterSitesInTablesPlots(sitename, SiteCommMatrix, SiteCommGlobalMatrix) : 

			fileHandle.write("<a name=\""+ sitename + "\"></a>\n\n")
			fileHandle.write("<div id=para-"+ sitename +">\n")

			fileHandle.write("<table border=\"0\" cellspacing=\"0\" class=stat>\n")

			fileHandle.write("<tr height=4><td width=" + metricw + "></td>\n")
			fileHandle.write("<td width=" + daysw + " colspan=" + colspans1 + " bgcolor=black></td></tr>\n")

			fileHandle.write("<tr>\n")
			fileHandle.write("<td width=\"" + metricw + "\"></td>\n")
			fileHandle.write("<td width=\"" + daysw + "\" colspan=" + colspans1 + " bgcolor=darkblue><div id=\"site\">" + sitename + "</div></td>\n")
			fileHandle.write("</tr>\n")

			fileHandle.write("<tr height=4><td width=" + metricw + "></td>\n")
			fileHandle.write("<td width=" + daysw + " colspan=" + colspans1 + " bgcolor=black></td></tr>\n")
		
			fileHandle.write("<tr height=7><td width=" + metricw + "></td>\n")
			fileHandle.write("<td width=" + daysw + " colspan=" + colspans1 + "></td></tr>\n")

			dates = SiteCommMatrixT1T2[sitename].keys()
			dates.sort()

			fileHandle.write("<tr height=4><td width=" + metricw + "></td>\n")
			fileHandle.write("<td width=" + daysw + " colspan=" + colspans1 + " bgcolor=black></td></tr>\n")
		
			fileHandle.write("<tr><td width=" + metricw + "></td>\n")
			fileHandle.write("<td width=" + scdaysw1 + " colspan=" + colspans3 + "><div id=\"daily-metric-header\">Site Readiness Status: </div></td>\n")
		
			igdays=0

			for datesgm in dates:

				igdays+=1
				if (days - igdays)>(daysshow-dayssc): continue

				if not SiteCommGlobalMatrix[sitename].has_key(datesgm):
					continue
				state=SiteCommGlobalMatrix[sitename][datesgm]
				datesgm1 = datesgm[8:10]
				c = datetime.datetime(*time.strptime(datesgm,"%Y-%m-%d")[0:5])
				fileHandle.write("<td width=\"" + dayw + "\" bgcolor=" + colors[state] + "><div id=\"daily-metric\">" + state + "</div></td>\n")

			fileHandle.write("</tr><tr height=4><td width=" + metricw + "></td>\n")
			fileHandle.write("<td width=" + daysw + " colspan=" + colspans1 + " bgcolor=black></td></tr>\n")
			
			fileHandle.write("<tr height=7><td width=" + metricw + "></td>\n")
			fileHandle.write("<td width=" + daysw + " colspan=" + colspans1 + "></td></tr>\n")
			
			fileHandle.write("<tr height=4><td width=" + tablew + " colspan=" + colspans2 + " bgcolor=black></td></tr>\n")

			fileHandle.write("<td width=\"" + metricw + "\"><div id=\"daily-metric-header\">Daily Metric: </div></td>\n")

			igdays=0

			for datesgm in dates:

				igdays+=1
				if (days - igdays)>daysshow-1: continue

				state=SiteCommMatrixT1T2[sitename][datesgm]

				datesgm1 = datesgm[8:10]
				c = datetime.datetime(*time.strptime(datesgm,"%Y-%m-%d")[0:5])
				if (c.weekday() == 5 or c.weekday() == 6) and sitename.find('T2_') == 0: # id. weekends
					if state!=" ":
						fileHandle.write("<td width=\"" + dayw + "\" bgcolor=grey><div id=\"daily-metric\">" + state + "</div></td>\n")
					else:
						fileHandle.write("<td width=\"" + dayw + "\" bgcolor=white><div id=\"daily-metric\">" + state + "</div></td>\n")
				else:
					fileHandle.write("<td width=\"" + dayw + "\" bgcolor=" + colors[state] + "><div id=\"daily-metric\">" + state + "</div></td>\n")


			fileHandle.write("<tr height=4><td width=" + tablew + " colspan=" + colspans2 + " bgcolor=black></td></tr>\n")

			fileHandle.write("<tr height=7><td width=" + metricw + "></td>\n")
			fileHandle.write("<td width=" + daysw + " colspan=" + colspans1 + "></td></tr>\n")

			fileHandle.write("<tr height=4><td width=" + tablew + " colspan=" + colspans2 + " bgcolor=black></td></tr>\n")
			
			indmetrics = metorder.keys()
			indmetrics.sort()

			for metnumber in indmetrics:

				met=metorder[metnumber]

				if not SiteCommMatrix[sitename][dates[0]].has_key(met) or met == 'IsSiteInSiteDB': continue # ignore 
				if sitename.find("T1_CH_CERN") == 0 and met == 'T1linksfromT0': continue # ignore 

				if met == 'SAMAvailability':
					fileHandle.write("<tr><td width=\"" + metricw + "\"><div id=\"metrics-header\"><font color=\"orange\">" + metlegends[met] + ": </font></div></td>\n")
				else:
					fileHandle.write("<tr><td width=\"" + metricw + "\"><div id=\"metrics-header\">" + metlegends[met] + ": </div></td>\n")
					
				igdays=0
				for datesgm in dates:
					igdays+=1
					if (days - igdays)>daysshow-1: continue

					state=SiteCommMatrix[sitename][datesgm][met]['Status']
					colorst=SiteCommMatrix[sitename][datesgm][met]['Color']
					datesgm1 = datesgm[8:10]
					c = datetime.datetime(*time.strptime(datesgm,"%Y-%m-%d")[0:5])
					
					if (c.weekday() == 5 or c.weekday() == 6) and sitename.find('T2_') == 0: # id. weekends
						if state != " " :
							if SiteCommMatrix[sitename][datesgm][met].has_key('URL') and SiteCommMatrix[sitename][datesgm][met]['URL'] != ' ' :
								stateurl=SiteCommMatrix[sitename][datesgm][met]['URL']
								fileHandle.write("<td width=\"" + dayw + "\" bgcolor=grey><a href=\""+stateurl+"\">"+"<div id=\"metrics2\">" + state + "</div></a></td>\n")
							else:
								fileHandle.write("<td width=\"" + dayw + "\" bgcolor=grey><div id=\"metrics2\">" + state + "</div></td>\n")
						else:
								fileHandle.write("<td width=\"" + dayw + "\" bgcolor=white><div id=\"metrics2\">" + state + "</div></td>\n")
					else:
						if SiteCommMatrix[sitename][datesgm][met].has_key('URL') and SiteCommMatrix[sitename][datesgm][met]['URL'] != ' ' :
							stateurl=SiteCommMatrix[sitename][datesgm][met]['URL']
							fileHandle.write("<td width=\"" + dayw + "\" bgcolor=" + colorst + "><a href=\""+stateurl+"\">"+"<div id=\"metrics2\">" + state + "</div></a></td>\n")
						else:
							fileHandle.write("<td width=\"" + dayw + "\" bgcolor=" + colorst + "><div id=\"metrics2\">" + state + "</div></td>\n")
				fileHandle.write("</tr>\n")
				
			fileHandle.write("<tr height=4><td width=" + tablew + " colspan=" + colspans22 + " bgcolor=black></td></tr>\n")
			fileHandle.write("<tr height=4><td width=" + metricw + "></td>\n")

			igdays=0
			
			for datesgm in dates:
				igdays+=1

				if (days - igdays)>daysshow-1: continue
				datesgm1 = datesgm[8:10]
				c = datetime.datetime(*time.strptime(datesgm,"%Y-%m-%d")[0:5])
				if c.weekday() == 5 or c.weekday() == 6: # id. weekends
					fileHandle.write("<td width=" + dayw + " bgcolor=grey> <div id=\"date\">" + datesgm1 + "</div></td>\n")
				else:
					fileHandle.write("<td width=" + dayw + " bgcolor=lightgrey> <div id=\"date\">" + datesgm1 + "</div></td>\n")
			fileHandle.write("</tr>\n")

			fileHandle.write("<tr height=4><td width=" + metricw + "></td>\n")
			fileHandle.write("<td width=" + daysw + " colspan=" + colspans1 + " bgcolor=black></td></tr>\n")

			fileHandle.write("<tr><td width=" + metricw + "></td>\n")

			lastmonth=""
			igdays=0

			for datesgm in dates:
				igdays+=1
				if (days - igdays)>daysshow-1: continue
				c = datetime.datetime(*time.strptime(datesgm,"%Y-%m-%d")[0:5])
				month = c.strftime("%b")
				if month != lastmonth:
					fileHandle.write("<td width=" + dayw + " bgcolor=black> <div id=\"month\">" + month + "</div></td>\n")
					lastmonth=month
				else:
					fileHandle.write("<td width=" + dayw + "></td>\n")
			fileHandle.write("</tr>\n")
		
			fileHandle.write("<tr><td width=" + metricw + "></td>\n")
			fileHandle.write("<td width=" + scdaysw1 + " colspan=" + colspans3 + "></td>\n")
		
			fileHandle.write("</table>\n")

			# report time
			
			fileHandle.write("<div id=\"leg1\">" + reptime + "</div>\n")
			fileHandle.write("</div>\n")

			#legends

			lw1="15"
			lw2="425"

			fileHandle.write("<br>\n")
			fileHandle.write("<table border=\"0\" cellspacing=\"0\" class=leg>\n")
			
			fileHandle.write("<tr height=15>\n") 
			fileHandle.write("<td width=" + lw1 + " bgcolor=white><div id=legflag>*</div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Due to operational errors, the metric has been corrected manually (!=SSB).</div></td>\n")
			fileHandle.write("</tr>\n")
			fileHandle.write("<tr height=10>\n") 
			fileHandle.write("</tr>\n")

			if sitename.find('T2_') == 0:
				fileHandle.write("<tr height=15>\n") 
				fileHandle.write("<td width=" + lw1 + " bgcolor=grey><div id=legflag>--</div></td>\n")
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Errors on weekends are ignored on Site Readiness computation for T2s [<a href=\"https://twiki.cern.ch/twiki/bin/viewauth/CMSPublic/SiteCommRules\">+info</a>]</div></td>\n")
				fileHandle.write("</tr>\n")
				fileHandle.write("<tr height=10>\n") 
				fileHandle.write("</tr>\n")

			fileHandle.write("<tr height=15>\n") 
			mes="\"Site Readiness Status\" as defined in <a href=\"https://twiki.cern.ch/twiki/bin/viewauth/CMSPublic/SiteCommRules\">Site Commissioning Twiki</a>:" 
			fileHandle.write("<td width=" + lw2 + " colspan=2><div id=\"legendexp\">" + mes + "</div></td>\n")
			mes="\"Daily Metric\" as boolean AND of all invidual metrics:" 
			fileHandle.write("<td width=" + lw2 + " colspan=2><div id=\"legendexp\">" + mes + "</div></td>\n")
			fileHandle.write("</tr>\n")
			fileHandle.write("<tr height=15>\n") 
			fileHandle.write("<td width=" + lw1 + " bgcolor=green><div id=legflag>R</div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = READY </div></td>\n")
			fileHandle.write("<td width=" + lw1 + " bgcolor=green><div id=legflag>O</div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = OK (All individual metrics above Site Commissioning Thresholds; \"n/a\" ignored)</div></td>\n")
			fileHandle.write("</tr>\n")
			fileHandle.write("<tr height=15>\n") 
			fileHandle.write("<td width=" + lw1 + " bgcolor=yellow><div id=legflag>W</div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = WARNING </div></td>\n")
			fileHandle.write("<td width=" + lw1 + " bgcolor=red><div id=legflag>E</div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = ERROR (Some individual metrics below Site Commissioning Thresholds)</div></td>\n")
			fileHandle.write("</tr>\n")
			fileHandle.write("<tr height=15>\n") 
			fileHandle.write("<td width=" + lw1 + " bgcolor=red><div id=legflag>NR</div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = NOT-READY </div></td>\n")
			fileHandle.write("<td width=" + lw1 + " bgcolor=brown><div id=legflag>SD</div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = SCHEDULED-DOWNTIME</div></td>\n")
			fileHandle.write("</tr>\n")
			fileHandle.write("<tr height=15>\n") 
			fileHandle.write("<td width=" + lw1 + " bgcolor=brown><div id=legflag>SD</div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = SCHEDULED-DOWNTIME</div></td>\n")
			fileHandle.write("</tr>\n")
			
			fileHandle.write("<tr height=10>\n") 
			fileHandle.write("</tr>\n")
			
			fileHandle.write("<tr height=15>\n") 
			
			mes="- INDIVIDUAL METRICS -"
		
			fileHandle.write("<td width=" + lw2 + " colspan=6><div id=\"legendexp2\">" + mes + "</div></td>\n")
			fileHandle.write("</tr>\n")
			
			fileHandle.write("<tr height=10>\n") 
			fileHandle.write("</tr>\n")
			
			fileHandle.write("<tr height=15>\n") 
			mes="\"Scheduled Downtimes\": site maintenances" 
			fileHandle.write("<td width=" + lw2 + " colspan=2><div id=\"legendexp\">" + mes + "</div></td>\n")
			mes="\"Job Robot\":" 
			fileHandle.write("<td width=" + lw2 + " colspan=2><div id=\"legendexp\">" + mes + "</div></td>\n")
			mes="\"Good Links\":" 
			fileHandle.write("<td width=" + lw2 + " colspan=2><div id=\"legendexp\">" + mes + "</div></td>\n")
			fileHandle.write("</tr>\n")
			fileHandle.write("<tr height=15>\n") 
			fileHandle.write("<td width=" + lw1 + " bgcolor=green><div id=legflag>Up</div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Site is not declaring Scheduled-downtime </div></td>\n")
			fileHandle.write("<td width=" + lw1 + " bgcolor=green><div id=legflag></div></td>\n")
			if sitename.find('T1_') == 0:
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Job success rate is &ge; 90%</div></td>\n")
			else:
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Job success rate is &ge; 80%</div></td>\n")
			fileHandle.write("<td width=" + lw1 + " bgcolor=green><div id=legflag></div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = at least half of links have 'good' transfers (i.e. with transfer quality > 50%)</div></td>\n")
			fileHandle.write("</tr>\n")
			fileHandle.write("<tr height=15>\n") 
			fileHandle.write("<td width=" + lw1 + " bgcolor=brown><div id=legflag>SD</div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = full-site in SD OR all CMS SE(s) in SD OR all CMS CE(s) in SD</div></td>\n")
			fileHandle.write("<td width=" + lw1 + " bgcolor=red><div id=legflag></div></td>\n")
			if sitename.find('T1_') == 0:
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Job success rate is < 90%</div></td>\n")
			else:
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Job success rate is < 80%</div></td>\n")
			fileHandle.write("<td width=" + lw1 + " bgcolor=red><div id=legflag></div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Otherwise</div></td>\n")
			fileHandle.write("</tr>\n")
			fileHandle.write("<tr height=15>\n") 
			fileHandle.write("<td width=" + lw1 + " bgcolor=yellow><div id=legflag>~</div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Some SE or CE services (not all) Downtime</div></td>\n")
			fileHandle.write("<td width=" + lw1 + " bgcolor=orange><div id=legflag>-</div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Jobs submitted but not finished</div></td>\n")
			fileHandle.write("</tr>\n")
			fileHandle.write("<tr height=15>\n") 
			fileHandle.write("<td width=" + lw1 + " bgcolor=silver><div id=legflag>UD</div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = full-site in UD OR all CMS SE(s) in UD OR all CMS CE(s) in UD</div></td>\n")

			fileHandle.write("<td width=" + lw1 + " bgcolor=white><div id=legflag>n/a</div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Job success rate is n/a</div></td>\n")
			fileHandle.write("</tr>\n")

			fileHandle.write("<tr height=10>\n") 
			fileHandle.write("</tr>\n")

			fileHandle.write("<tr height=15>\n") 
			mes="\"SAM Availability\":" 
			fileHandle.write("<td width=" + lw2 + " colspan=2><div id=\"legendexp\">" + mes + "</div></td>\n")
			if sitename.find('T1_') == 0:
				mes="\"Active T1 links from T0\":" 
			else:
				mes="\"Active T2 links to T1s\":"
			fileHandle.write("<td width=" + lw2 + " colspan=2><div id=\"legendexp\">" + mes + "</div></td>\n")
			fileHandle.write("</tr>\n")
			fileHandle.write("<tr height=15>\n") 
			fileHandle.write("<td width=" + lw1 + " bgcolor=green><div id=legflag></div></td>\n")
			if sitename.find('T1_') == 0:
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = SAM availability is &ge; 90% </div></td>\n")
			else:	
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = SAM availability is &ge; 80% </div></td>\n")
			fileHandle.write("<td width=" + lw1 + " bgcolor=green><div id=legflag></div></td>\n")
			if sitename.find('T1_') == 0:
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Link from T0_CH_CERN is DDT-commissioned </div></td>\n")
			else:
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Site has &ge; 2 DDT-commissioned links to T1 sites </div></td>\n")			
			fileHandle.write("</tr>\n")
			fileHandle.write("<tr height=15>\n") 
			fileHandle.write("<td width=" + lw1 + " bgcolor=red><div id=legflag></div></td>\n")
			if sitename.find('T1_') == 0:
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = SAM availability is < 90%  <div></td>\n")
			else:
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = SAM availability is < 80%  <div></td>\n")	
			fileHandle.write("<td width=" + lw1 + " bgcolor=red><div id=legflag></div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Otherwise</div></td>\n")
			fileHandle.write("</tr>\n")
			
			fileHandle.write("<tr height=10>\n") 
			fileHandle.write("</tr>\n")

			fileHandle.write("<tr height=15>\n") 
			if sitename.find('T1_') == 0:
				mes="\"Active T1 links from/to T1s\":" 
			else:
				mes="\"Active T2 links from T1s\":"
			fileHandle.write("<td width=" + lw2 + " colspan=2><div id=\"legendexp\">" + mes + "</div></td>\n")

			if sitename.find('T1_') == 0:
				mes="\"Active T1 links to T2s\":" 
			else:
				mes=""
			fileHandle.write("<td width=" + lw2 + " colspan=2><div id=\"legendexp\">" + mes + "</div></td>\n")
			fileHandle.write("</tr>\n")
			fileHandle.write("<tr height=15>\n") 
			fileHandle.write("<td width=" + lw1 + " bgcolor=green><div id=legflag></div></td>\n")
			if sitename.find('T1_') == 0:
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Site has &ge; 4 DDT-commissioned links from and to, respectively, other T1 sites </div></td>\n")
			else:
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Site has &ge; 4 DDT-commissioned links from T1 sites </div></td>\n")	
	
			if sitename.find('T1_') == 0:
				fileHandle.write("<td width=" + lw1 + " bgcolor=green><div id=legflag></div></td>\n")
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Site has &ge; 20 DDT-commissioned links to T2 sites </div></td>\n")
			else:
				fileHandle.write("<td width=" + lw1 + " bgcolor=white><div id=legflag></div></td>\n")
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"></div></td>\n")
			fileHandle.write("</tr>\n")
			fileHandle.write("<tr height=15>\n") 
			fileHandle.write("<td width=" + lw1 + " bgcolor=red><div id=legflag></div></td>\n")
			fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Otherwise <div></td>\n")
			if sitename.find('T1_') == 0:
				fileHandle.write("<td width=" + lw1 + " bgcolor=red><div id=legflag></div></td>\n")
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"> = Otherwise </div></td>\n")
			else:
				fileHandle.write("<td width=" + lw1 + " bgcolor=white><div id=legflag></div></td>\n")
				fileHandle.write("<td width=" + lw2 + "><div id=\"legend\"></div></td>\n")

			fileHandle.write("</tr>\n")
			
			fileHandle.write("</table>\n")
			fileHandle.write("<p>\n")

			fileHandle.write("<p><br>\n")

	fileHandle.write("</center></html></body>")
	fileHandle.close()

	sys.stdout.write("\n")
	sys.stdout.flush()

def ProduceSiteReadinessStatistics(SiteCommMatrix, SiteCommGlobalMatrix, SiteReadinessStats2):

	# 
	# Evaluate statistics for Site Readiness  (last week, last month)
	# 

	sitesit = SiteCommGlobalMatrix.keys()
	sitesit.sort()

	prog = progressBar(0, 100, 77)
	iprog=0

	for dayspan in 30, 15, 7:

		iprog+=100./3.
		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()

		for sitename in sitesit:

			if not FilterSitesInTablesPlots(sitename, SiteCommMatrix, SiteCommGlobalMatrix) : continue
			
			countR=0; countW=0; countNR=0; countSD=0; countNA=0

			infostats2 = {}

			if not SiteReadinessStats2.has_key(sitename):
				SiteReadinessStats2[sitename]={}		

			for i in range(0,dayspan):

				d=datetime.timedelta(i)
				datestamp=yesterday-d

				state=SiteCommGlobalMatrix[sitename][datestamp.strftime("%Y-%m-%d")]
				
				if state == "R": countR+=1
				if state == "W": countW+=1
				if state == "NR": countNR+=1
				if state == "SD": countSD+=1
				if state.find("n/a") == 0: countNA+=1
				
			if not SiteReadinessStats2[sitename].has_key(dayspan):
				SiteReadinessStats2[sitename][dayspan]={}	

			infostats2['R_perc']= (int)(round(100.*countR/dayspan))
			infostats2['W_perc']= (int)(round(100.*countW/dayspan))
			infostats2['R+W_perc']= (int)(round(100.*(countR+countW)/dayspan))
			infostats2['NR_perc']= (int)(round(100.*countNR/dayspan))
			infostats2['SD_perc']= (int)(round(100.*countSD/dayspan))
			infostats2['R']= countR
			infostats2['W']= countW
			infostats2['R+W']= countW+countR
			infostats2['NR']= countNR
			infostats2['SD']= countSD
			infostats2['days']=dayspan

			if (dayspan-countSD-countNA)!=0:
				infostats2['Rcorr_perc']= (int)(round(100.*countR/(dayspan-countSD-countNA)))
				infostats2['Wcorr_perc']= (int)(round(100.*countW/(dayspan-countSD-countNA)))
				infostats2['R+Wcorr_perc']= (int)(round(100.*(countR+countW)/(dayspan-countSD-countNA)))
				infostats2['NRcorr_perc']= (int)(round(100.*countNR/(dayspan-countSD-countNA)))
			else:
				infostats2['Rcorr_perc']= 0
				infostats2['Wcorr_perc']= 0
				infostats2['R+Wcorr_perc']= 0
				infostats2['NRcorr_perc']= 100
			
			SiteReadinessStats2[sitename][dayspan]=infostats2

	sys.stdout.write("\n")
	sys.stdout.flush()


def ProduceSiteReadinessSSBFiles(SiteCommMatrix, SiteCommGlobalMatrix, SiteReadinessStats2, pathout):
	
	prog = progressBar(0, 100, 77)
	iprog=0

	for dayspan in 30, 15, 7:

		iprog+=100./3.
		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()

		fileSSBRanking= pathout + '/SiteReadinessRanking_SSBfeed_last' + str(dayspan) + 'days.txt' 
		fileHandle = open ( fileSSBRanking , 'w' )

		sitesit=SiteCommGlobalMatrix.keys()
		sitesit.sort()
		
		for sitename in sitesit:

			if not FilterSitesInTablesPlots(sitename, SiteCommMatrix, SiteCommGlobalMatrix) : continue

			pl = "R+Wcorr_perc"
			color="red"
			if sitename.find("T1") == 0 and SiteReadinessStats2[sitename][dayspan][pl]>90:
				color="green"
			if sitename.find("T2") == 0 and SiteReadinessStats2[sitename][dayspan][pl]>80:
				color="green"
			if SiteReadinessStats2[sitename][dayspan][pl] != "n/a":
				if options.url.find("pic.es") > 0:
					filenameSSB = options.url + "/SiteReadinessPlots/" + sitename.split("_")[0] + "_" + pl + "_last" + str(dayspan) + "days_" + timestamphtml + ".png"
				elif options.url.find("cern.ch") > 0 :
					filenameSSB = options.url + "/SiteReadiness/PLOTS/" + sitename.split("_")[0] + "_" + pl + "_last" + str(dayspan) + "days_" + timestamphtml + ".png"
				else:
					filenameSSB = "unknown"
				tofile=todaystampfileSSB + '\t' + sitename + '\t' + str(SiteReadinessStats2[sitename][dayspan][pl]) + '\t' + color + '\t' + filenameSSB + "\n"
				fileHandle.write(tofile)
						
	fileHandle.close()

	sys.stdout.write("\n")
	sys.stdout.flush()

def ProduceSiteReadinessRankingPlots(SiteCommMatrix, SiteCommGlobalMatrix, SiteReadinessStats2, pathoutPLOTS):
	
	prog = progressBar(0, 100, 77)
	iprog=0

	sitesit=SiteCommGlobalMatrix.keys()
	sitesit.sort()
		
	for dayspan in 30, 15, 7:

		iprog+=100./3.
		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()

		for pl in 'SD_perc', 'R+Wcorr_perc':

			for i in "T1","T2":
			
				dataR ={}
	
				filename = pathoutPLOTS + "/" + i + "_" + pl + "_last" + str(dayspan) + "days_" + timestamphtml + ".png"				

				for sitename in sitesit:

					if not sitename.find(i+"_") == 0 : continue
					if not FilterSitesInTablesPlots(sitename, SiteCommMatrix, SiteCommGlobalMatrix) : continue
					if pl == 'SD_perc' and SiteReadinessStats2[sitename][dayspan][pl]==0.: continue # Do not show Up sites on SD plots.
					
					dataR[sitename+" ("+str(SiteReadinessStats2[sitename][dayspan]["SD_perc"])+"%)"] = SiteReadinessStats2[sitename][dayspan][pl]

				
				if len(dataR) == 0:
					os.system("touch %s" % filename)
					continue
				
				norms = normalize(0,100)
				mapper = cm.ScalarMappable( cmap=cm.RdYlGn, norm=norms )
				# Hack to make mapper work:
				def get_alpha(*args, **kw):
					return 1.0
				mapper.get_alpha = get_alpha
				A = linspace(0,100,100)
				mapper.set_array(A)
				
				pos = arange(len(dataR))+.5    # the bar centers on the y axis
				dataS=dataR.items()
				dataS.sort(lambda x,y: cmp(x[1],y[1]))

				ytext = []
				val = []
				color = []
				total=0	
				ent=0
				ent2=0
				for t in range(0,len(dataS)):
					ytext.append(dataS[t][0])
					val.append(dataS[t][1])
					color.append( mapper.to_rgba( dataS[t][1] ) )
					total+=1
					if i == 'T1' and dataS[t][1] <= 90 : ent+=1
					if i == 'T1' and dataS[t][1] > 90 : ent2+=1
					if i == 'T2' and dataS[t][1] <= 80 : ent+=1
					if i == 'T2' and dataS[t][1] > 80 : ent2+=1

				if pl == 'R+Wcorr_perc':
					metadataR = {'title':'%s Readiness Rank last %i days (+SD %%) [%s]' % (i,int(dayspan),todaystamp), 'fixed-height':False }
			       	if pl == 'SD_perc':
					metadataR = {'title':'Rank for %s Scheduled Downtimes last %i days [%s]' % (i,int(dayspan),todaystamp), 'fixed-height':True}

				fig = Figure()
				canvas = FigureCanvas(fig)
				if i == 'T1':
					SRlim=90
					fig.set_size_inches(7,4)
				else:
					SRlim=80
					fig.set_size_inches(7.5,9.5)
				ax = fig.add_subplot(111)
				fig.subplots_adjust(left=0.2, right=0.97)
				ax.set_autoscale_on(False)
				ax.barh(pos,val, align='center',color=color)
				ax.set_xlim([0,100])
				ax.set_ylim([0,len(dataS)])
				ax.set_yticklabels(ytext,fontsize=8,family='sans-serif')
				ax.set_yticks(pos)
				ax.set_title(metadataR['title'],fontsize=14)
				ax.set_xlabel('Site Readiness %',fontsize=12,family='sans-serif')
			       	if pl == 'R+Wcorr_perc':
					ax.axvline(x=SRlim, ymin=0, ymax=1,color='red',ls=':',lw=3)
					if i == 'T1' :
						ax.text(91,0.65,str(ent2)+"/"+str(total)+" >90%",color='darkgreen',fontsize=6)
						ax.text(91,0.3,str(ent)+"/"+str(total)+" $\leq$90%",color='red',fontsize=6)
					if i == 'T2' :
						ax.text(81,2,str(ent2)+"/"+str(total)+" >80%",color='darkgreen',fontsize=6)
						ax.text(81,1,str(ent)+"/"+str(total)+" $\leq$80%",color='red',fontsize=6)
				canvas.print_figure(filename)

	sys.stdout.write("\n")
	sys.stdout.flush()

def PrintDailyMetricsStats(SiteCommMatrix, SiteCommMatrixT1T2, SiteCommGlobalMatrix, fileDailyStat):

	prog = progressBar(0, 100, 77)
	iprog=0

	fileHandle = open ( fileDailyStat , 'w' )

	sites = SiteCommMatrixT1T2.keys()
	sites.sort()

	# print stats
	for sitename in sites:

		dates = SiteCommMatrixT1T2[sitename].keys()
		dates.sort()
		continue

	for i in "T1","T2":

		iprog+=100./2.
		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()

		for dat in dates:
		
			countO=0; countE=0; countSD=0; countna=0
		
			for sitename in sites:

				if sitename.find("T1_CH_CERN") == 0: continue
				if not sitename.find(i+"_") == 0: continue
				if not FilterSitesInTablesPlots(sitename, SiteCommMatrix, SiteCommGlobalMatrix) : continue
				
				state=SiteCommMatrixT1T2[sitename][dat]
				
				if state == "O":
					countO+=1
				if state == "E":
					countE+=1
				if state.find("n/a") == 0:
					countna+=1
				if state == "SD":
					countSD+=1

			if dat == todaystamp: continue
			tofile = "Daily Metric " + i + " " + dat + " " + str(countE) + " " +  str(countO) + " " + str(countna) + " " + str(countSD) + " " + str(countE+countO+countSD+countna) + "\n"
			fileHandle.write(tofile)

	fileHandle.close()

	sys.stdout.write("\n")
	sys.stdout.flush()


def PrintSiteReadinessMetricsStats(SiteCommMatrix, SiteCommGlobalMatrix, fileReadinessStat):
	
	prog = progressBar(0, 100, 77)
	iprog=0

	fileHandle = open ( fileReadinessStat , 'w' )

	sites = SiteCommGlobalMatrix.keys()
	sites.sort()

	# print stats
	for sitename in sites:

		dates = SiteCommGlobalMatrix[sitename].keys()
		dates.sort()
		continue

	for i in "T1","T2":

		iprog+=100./2.
		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()

		for dat in dates:
		
			countR=0; countW=0; countNR=0; countSD=0; countna=0
		
			for sitename in sites:

				if sitename.find("T1_CH_CERN") == 0: continue
				if not sitename.find(i+"_") == 0: continue
				if not FilterSitesInTablesPlots(sitename, SiteCommMatrix, SiteCommGlobalMatrix) : continue
				
				state=SiteCommGlobalMatrix[sitename][dat]
				
				if state == "R":
					countR+=1
				if state == "W":
					countW+=1
				if state == "NR":
					countNR+=1
				if state.find("n/a") == 0:
					countna+=1
				if state == "SD":
					countSD+=1

			if dat == todaystamp: continue
			tofile = "Site Readiness Metric " + i + " " + dat + " " + str(countR) + " " + str(countNR) + " " + str(countna) + " " + str(countW) + " " + str(countSD) + " " + str(countR+countNR+countW+countna+countSD) + "\n"
			fileHandle.write(tofile)

	fileHandle.close()

	sys.stdout.write("\n")
	sys.stdout.flush()

def PrintDailyMetrics(SiteCommMatrix, SiteCommGlobalMatrix, metorder):
	
	prog = progressBar(0, 100, 77)
	iprog=0

	indmetrics = metorder.keys()
	indmetrics.sort()
	
	sites = SiteCommMatrix.keys()
	sites.sort()

	# print stats
	for sitename in sites:

		iprog+=100./3.
		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()
		
		dates = SiteCommMatrixT1T2[sitename].keys()
		dates.sort()

		for dat in dates:

			if not FilterSitesInTablesPlots(sitename, SiteCommMatrix, SiteCommGlobalMatrix) : continue
				
			for metnumber in indmetrics:
				
				met=metorder[metnumber]
			
				if not SiteCommMatrix[sitename][dat].has_key(met) or met == 'IsSiteInSiteDB': continue # ignore 

				if SiteCommMatrix[sitename][dat][met].has_key('URL'):
					url=SiteCommMatrix[sitename][dat][met]['URL']
				else:
					url="-"
				print dat, sitename, met, SiteCommMatrix[sitename][dat][met]['Status'], SiteCommMatrix[sitename][dat][met]['Color'],url

	sys.stdout.write("\n")
	sys.stdout.flush()

				
def CreateSimbLinks(pathoutHTML,pathoutPLOTS):
	
	prog = progressBar(0, 100, 77)
	iprog=0

	os.chdir(pathoutHTML)
	slinkhtml= './SiteReadinessReport.html'
	if os.path.isfile(slinkhtml): os.remove(slinkhtml)
	filehtml= pathoutHTML + '/SiteReadinessReport_' + timestamphtml +'.html'
	os.symlink(os.path.split(filehtml)[1],slinkhtml)

	os.chdir(pathoutPLOTS)
	for dayspan in 30, 15, 7:
		
		iprog+=100./3.
		prog.updateAmount(iprog)
		sys.stdout.write(str(prog)+'\r')
		sys.stdout.flush()
		
		for pl in 'SD_perc', 'R+Wcorr_perc':
			for i in "T1","T2":
				filepng = pathoutPLOTS + "/" + i + "_" + pl + "_last" + str(dayspan) + "days_" + timestamphtml + ".png"				
				slinkhtml = "./" + i + "_" + pl + "_last" + str(dayspan) + "days.png"
				if os.path.isfile(slinkhtml): os.remove(slinkhtml)
				os.symlink(os.path.split(filepng)[1],slinkhtml)
			
	sys.stdout.write("\n")
	sys.stdout.flush()


def DumpPickleFiles(SiteCommMatrix,SiteCommMatrixT1T2,SiteCommGlobalMatrix,pathoutASCII):

	prog = progressBar(0, 100, 77)
	iprog=0

	iprog+=100./3.
	prog.updateAmount(iprog)
	sys.stdout.write(str(prog)+'\r')
	sys.stdout.flush()
		
	file = pathoutASCII+"/SiteCommMatrix.pck"
	file1 = open(file, "w") # write mode
	pickle.dump(SiteCommMatrix,file1)
	file1.close()

	iprog+=100./3.
	prog.updateAmount(iprog)
	sys.stdout.write(str(prog)+'\r')
	sys.stdout.flush()
		
	file = pathoutASCII+"/SiteCommMatrixT1T2.pck"
	file1 = open(file, "w") # write mode
	pickle.dump(SiteCommMatrixT1T2,file1)
	file1.close()

	iprog+=100./3.
	prog.updateAmount(iprog)
	sys.stdout.write(str(prog)+'\r')
	sys.stdout.flush()
		
	file = pathoutASCII+"/SiteCommGlobalMatrix.pck"
	file1 = open(file, "w") # write mode
	pickle.dump(SiteCommGlobalMatrix,file1)
	file1.close()

	sys.stdout.write("\n")
	sys.stdout.flush()

########################################################
# Reading data from SSB and perform all actions
########################################################

sites={}
SiteCommMatrix={}
SiteCommGlobalMatrix = {}
SiteCommMatrixT1T2 = {}
SiteCommStatistics = {}

criteriasT1 = ( 'JobRobot', 'SAMNagiosAvailability', 'T1linksfromT0', 'T1linksfromtoT1s', 'T1linkstoT2s', 'GoodT1linksfromT0', 'GoodT1linksfromT1s', 'GoodT1linksfromT2s', 'GoodT1linkstoT1s', 'GoodT1linkstoT2s' )
criteriasT2 = ( 'JobRobot', 'SAMNagiosAvailability', 'T2linksfromT1s', 'T2linkstoT1s', 'GoodT2linksfromT1s', 'GoodT2linkstoT1s')

# parse SSB XML data from all relevants columns

print "\nObtaining XML info from SSB 'commission' view\n"
SSBXMLParser(sites, ColumnMatrix)

print "\nExtracting Daily Metrics for CMS sites\n"
GetDailyMetricStatus(sites, SiteCommMatrix, MatrixStatusColors)

print "\nExtracting Scheduled Downtime Topology Daily Metrics for CMS sites\n"
GetDailyScheduledDowntimeTopologyStatus(sites, SiteCommMatrix, MatrixStatusColors)

#print "\nCorrecting Daily Metrics from external ascii file\n"
#CorrectDailyMetricsFromASCIIFile(sites, SiteCommMatrix, DailyMetricsCorrected)

print "\nEvaluating Daily Status\n"
EvaluateDailyStatus(SiteCommMatrix, SiteCommMatrixT1T2, criterias)

print "\nEvaluating Site Readiness\n"
EvaluateSiteReadiness(SiteCommMatrixT1T2, SiteCommGlobalMatrix)

print "\nProducing Site Readiness SSB input file\n"
ProduceSiteReadinessSSBFile(SiteCommGlobalMatrix, fileSSB)

print "\nProducing Site Readiness HTML view\n"
ProduceSiteReadinessHTMLViews(SiteCommGlobalMatrix, metorder, metlegends, colors, pathoutHTML)

print "\nProducing Site Readiness Statistics\n"
ProduceSiteReadinessStatistics(SiteCommMatrix, SiteCommGlobalMatrix, SiteCommStatistics)

print "\nProducing Site Readiness SSB files to commission view\n"
ProduceSiteReadinessSSBFiles(SiteCommMatrix, SiteCommGlobalMatrix, SiteCommStatistics, pathout)

print "\nProducing Site Readiness Ranking plots\n"
ProduceSiteReadinessRankingPlots(SiteCommMatrix, SiteCommGlobalMatrix, SiteCommStatistics, pathoutPLOTS)

print "\nPrinting Daily Metrics Statistics\n"
PrintDailyMetricsStats(SiteCommMatrix, SiteCommMatrixT1T2, SiteCommGlobalMatrix,fileDailyStat)

print "\nPrinting Site Readiness Metrics Statistics\n"
PrintSiteReadinessMetricsStats(SiteCommMatrix, SiteCommGlobalMatrix,fileReadinessStat)

print "\nCreating Symbolic Links\n"
CreateSimbLinks(pathoutHTML,pathoutPLOTS)

print "\nCreating Pickle files\n"
DumpPickleFiles(SiteCommMatrix,SiteCommMatrixT1T2,SiteCommGlobalMatrix,pathoutASCII)

sys.exit(0)
