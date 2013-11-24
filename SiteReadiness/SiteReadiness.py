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

import sys, xml.dom.minidom, os, datetime, time
from xml import xpath
from datetime import date
from optparse import OptionParser
# local imports
from ColumnInfo import ColumnInfo
from ProgressBar import ProgressBar
from OutputWriter import OutputWriter
from TimeInfo import TimeInfo

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

def ShiftDayForMetric(datestamp,col):
    if col == "JobRobot" or col=="JobRobotDB" or col=="HammerCloud" or col == "SAMAvailability" or col == "SAMNagiosAvailability" or col == "SUMAvailability" or col.find("Good")==0:
        delta = datetime.timedelta(1)
        yesterday = datestamp - delta
        return yesterday.strftime("%Y-%m-%d")
    else:
        return datestamp.strftime("%Y-%m-%d")
    
def GetDailyMetricStatus(sites, SiteCommMatrix, colorCodes, urls, cinfo, tinfo):
    prog = ProgressBar(0, 100, 77)
    for sitename in sites:
        prog.increment(100./len(sites))
        if not SiteCommMatrix.has_key(sitename): # add site if not already there
            SiteCommMatrix[sitename]={}

        for col in urls:
            if not sites[sitename].has_key(col) or col == 'Downtimes_sam' or col == 'Downtimes_top':
                continue

            # set to null (default) values
            for i in range(0,cinfo.days+1):
                delta = datetime.timedelta(cinfo.days-i)
                dayloop = tinfo.today - delta
                dayloopstamp = dayloop.strftime("%Y-%m-%d")
                if not SiteCommMatrix[sitename].has_key(dayloopstamp):
                    SiteCommMatrix[sitename][dayloopstamp] = {}
                if not SiteCommMatrix[sitename][dayloopstamp].has_key(col):
                    SiteCommMatrix[sitename][dayloopstamp][col] = {}
                nullValues = {}
                nullValues['Status'] = 'n/a'
                nullValues['Color'] = 'white'
                nullValues['URL'] = ' '
                nullValues['validity'] = 0
                SiteCommMatrix[sitename][dayloopstamp][col] = nullValues

            items = sites[sitename][col].keys()
            items.sort()
            for coldate in items: # loop over each time/date combination
                xmltime = datetime.datetime(*time.strptime(sites[sitename][col][coldate]['Time'], "%Y-%m-%d %H:%M:%S")[0:6])
                xmlendtime = datetime.datetime(*time.strptime(sites[sitename][col][coldate]['EndTime'], "%Y-%m-%d %H:%M:%S")[0:6])

                startxmldatetmp = xmltime.strftime("%Y-%m-%d 00:00:00")
                startxmldate = datetime.datetime(*time.strptime(startxmldatetmp, "%Y-%m-%d %H:%M:%S")[0:6])

                EndTXML = True
                i = 0
                while ( EndTXML ):
                    d = datetime.timedelta(i) # convert i to number of days
                    i += 1
                    dayloop = startxmldate + d
                    dayloopstamp = dayloop.strftime("%Y-%m-%d")
                    dayloopstamp2 = dayloop.strftime("%Y-%m-%d 00:00:00")
                    looptime = datetime.datetime(*time.strptime(dayloopstamp2, "%Y-%m-%d %H:%M:%S")[0:6])

                    if dayloop > tinfo.today:
                        EndTXML = False
                        continue
                        
                    diff1  = xmltime-looptime
                    diff1s = (diff1.days*86400+diff1.seconds)
                    diff2  = xmlendtime-looptime
                    diff2s = (diff2.days*86400+diff2.seconds)
                    diff3  = xmlendtime-xmltime
                    diff3s = (diff3.days*86400+diff3.seconds)
                    if diff1s<=0 and diff2s>0:
                        if diff2s>=86400: validity=86400
                        else: validity=diff2s
                    if diff1s>0 and diff1s<86400:
                        if diff2s>86400: validity=86400-diff1s
                        else: validity=diff3s
                    if diff1s<0 and diff2s<=0:
                        EndTXML=False
                        continue

                    if colorCodes[col][sites[sitename][col][coldate]['COLOR']] == "green":
                        status=sites[sitename][col][coldate]['Status']
                        statusu=sites[sitename][col][coldate]['URL']
                        statusc='green'
                        if sites[sitename][col][coldate]['Status']=="pend":
                            statusc='orange'
                            status='-'
                    elif colorCodes[col][sites[sitename][col][coldate]['COLOR']] == "white":
                        statusu=' '
                        status='n/a'
                        statusc='white'
                    elif colorCodes[col][sites[sitename][col][coldate]['COLOR']] == "red":
                        status=sites[sitename][col][coldate]['Status']
                        statusu=sites[sitename][col][coldate]['URL']
                        statusc='red'
                    else:
                        status='???'
                        statusu='???'
                        statusc='white'

                    dayloopstamp3 = ShiftDayForMetric(dayloop,col)
                    todayst = date(int(tinfo.todaystamp[0:4]),int(tinfo.todaystamp[5:7]),int(tinfo.todaystamp[8:10]))
                    dayloop3 = date(int(dayloopstamp3[0:4]),int(dayloopstamp3[5:7]),int(dayloopstamp3[8:10]))

                    if abs((dayloop3-todayst).days) > cinfo.days:
                        continue

                    # set the actual values in SiteCommMatrix
                    infocol = {}
                    infocol['Status'] = status
                    infocol['Color'] = statusc
                    infocol['URL'] = statusu
                    infocol['validity'] = validity
                    if SiteCommMatrix[sitename][dayloopstamp3][col].has_key('validity'):
                        if validity > SiteCommMatrix[sitename][dayloopstamp3][col]['validity']:
                            SiteCommMatrix[sitename][dayloopstamp3][col] = infocol
                    else:
                        SiteCommMatrix[sitename][dayloopstamp3][col] = infocol
                                
                    if dayloopstamp == tinfo.todaystamp:
                        infocol = {}
                        infocol['Status'] = ' '
                        infocol['Color'] = 'white'
                        infocol['URL'] = ' '
                        infocol['validity'] = '0'                       
                        SiteCommMatrix[sitename][dayloopstamp][col] = infocol

    prog.finish()

def SSBXMLParser(sites, urls):
    prog = ProgressBar(0, 100, 77)
    xmlCacheDir = options.path_out + "/INPUTxmls"
    if not os.path.exists(xmlCacheDir):
        os.makedirs(xmlCacheDir)
    ColumnItems = urls.keys()
    ColumnItems.sort()
    for col in ColumnItems:
        prog.increment(100./len(ColumnItems))

        url = urls[col]
        fileN = xmlCacheDir + "/" + col + ".xml"
        if options.xml == 'false' and not os.path.exists(xmlCacheDir):
            print "\nWARNING: you cannot re-use the XML files as the files were not obtained before. Obtaining them...\n"
            options.xml = 'true'
        if options.xml == 'true': # download xml file if requested
            print "Column %s - Getting the url %s" % (col, url)
            os.system("curl -s -H 'Accept: text/xml'  '%s' > %s" % (url,fileN))
    
        f = file(fileN,'r') # read xml file that was either just written, or was written in the previous run
        t = xml.dom.minidom.parse(f)
        f.close()

        for subUrl in xpath.Evaluate("/getplotdata/csvdata/item", t):
            info = {} # basic info about the site for this column
            for option in ('Status', "COLOR", 'Time', 'EndTime','VOName','URL'):
                for target in xpath.Evaluate(option, subUrl):
                    if target.hasChildNodes():
                        s = target.firstChild.nodeValue.encode('ascii')
                    else:
                        s = ""
                    info[option] = s

            if options.oneSite != "" and info['VOName'].find(options.oneSite) != 0: continue

            if info['VOName'].find("T3_FR-IPNL") == 0: continue
            if info['VOName'].find("T2_TR_ULAKBIM") == 0: continue
            
            if not sites.has_key(info['VOName']): # if site not already in dict, add an empty dict for it
                sites[info['VOName']] = {}
            if not sites[info['VOName']].has_key(col): # if site entry doesn't already have this column, add an empty dict for this column
                sites[info['VOName']][col] = {}
            sites[info['VOName']][col][info['Time']] = info # set the actual values

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

    prog.finish()

def GetDailyScheduledDowntimeTopologyStatus(sites, SiteCommMatrix, colorCodes, urls, cinfo, tinfo):
    # Leer Downtimes Topology (por ahora uso Time y EndTime para decidir cuanto duran los Downtimes)
    # por defecto todos los dias son Ok, y uso Time y EndTime para asignar los Downtimes.
    prog = ProgressBar(0, 100, 77)
    for sitename in sites:
        prog.increment(100./len(sites))
        if not SiteCommMatrix.has_key(sitename): # add dict for site
            SiteCommMatrix[sitename]={}
        
        for col in urls: # loop over columns
            if col != "Downtimes_top":
                continue
            infocol = {}

            if not sites[sitename].has_key(col):
                sites[sitename][col] = {}

            # set downtime metric to green by default
            for i in range(0,cinfo.days+1):
                delta = datetime.timedelta(cinfo.days-i);
                dayloop = tinfo.today - delta
                dayloopstamp = dayloop.strftime("%Y-%m-%d")

                if not SiteCommMatrix[sitename].has_key(dayloopstamp):
                    SiteCommMatrix[sitename][dayloopstamp] = {}

                infocol['Status'] = "Up"
                infocol['Color'] = "green"
                infocol['URL'] = ' ' 
                SiteCommMatrix[sitename][dayloopstamp][col] = infocol

            items = sites[sitename][col].keys()
            items.sort()
            for stdate in items:
                colorTmp = colorCodes[col][sites[sitename][col][stdate]['COLOR']] # color taken from sites
                if colorTmp == "white" or  colorTmp == "green": # if they're ok, they don't need to be corrected for downtimes
                    continue
                sttdate = stdate[0:stdate.find(" ")]
                enddate = sites[sitename][col][stdate]['EndTime'][0:sites[sitename][col][stdate]['EndTime'].find(" ")]
                cl = sites[sitename][col][stdate]['COLOR']

                for i in range(0,cinfo.days+1):
                    delta = datetime.timedelta(cinfo.days-i);
                    dayloop = tinfo.today - delta
                    dayloopstamp = dayloop.strftime("%Y-%m-%d")
                    kk=0
                    if stdate.find(dayloopstamp) == 0:
                        wloop=True
                        while (wloop):
                            cdate = datetime.datetime(*time.strptime(sttdate,"%Y-%m-%d")[0:5])
                            delta = datetime.timedelta(kk);
                            dayloop = cdate + delta
                            dayloopstamp  = dayloop.strftime("%Y-%m-%d")

                            # I'm guessing that this is supposed skip brown entries, but the first and last if statements seem to have typos.
                            if SiteCommMatrix[sitename].has_key(col):
                                if SiteCommMatrix[sitename][col].has_key(dayloopstamp):
                                    if SiteCommMatrix[sitename][col][dayloopstamp].has_key('Color'):
                                        if SiteCommMatrix[sitename][col][dayloopstamp].has_key('Color') == 'brown':
                                            kk+=1
                                            continue

                            # get downtime info from sites and put it into SiteCommMatrix
                            values = {}
                            if colorTmp == 'brown':
                                values['Color'] = 'brown'
                                values['Status'] = 'SD'
                                values['URL'] = sites[sitename][col][stdate]['URL']
                            if colorTmp == 'grey':
                                if sites[sitename][col][stdate]['Status'].find("OUTAGE UNSCHEDULED") == 0:
                                    values['Color'] = 'silver'
                                    values['Status'] = 'UD'
                                    values['URL'] = sites[sitename][col][stdate]['URL']
                                else:
                                    values['Color'] = 'yellow'
                                    values['Status'] = '~'
                                    values['URL'] = sites[sitename][col][stdate]['URL']
                            if colorTmp == 'yellow':
                                values['Color'] = 'yellow'
                                values['Status'] = '~'
                                values['URL'] = sites[sitename][col][stdate]['URL']
                            
                            if dayloop > tinfo.today: break # ignore future downtimes

                            SiteCommMatrix[sitename][dayloopstamp][col] = values

                            kk+=1

                            if (dayloopstamp == enddate): wloop=False

            # set today's downtime status to white
            nullVals = {}
            nullVals['Status'] = ' '
            nullVals['URL'] = ' '
            nullVals['Color'] = 'white'
            SiteCommMatrix[sitename][tinfo.todaystamp][col] = nullVals

    prog.finish()

def GetCriteriasList(sitename, criteria):
    # return list of columns (criteria) that apply to this site, based on its tier
    tier = sitename.split("_")[0]   
    return criteria[tier]

def EvaluateDailyStatus(SiteCommMatrix, SiteCommMatrixT1T2, criteria, tinfo):
    # set value for the 'Daily Metric' column in SiteCommMatrixT1T2
    prog = ProgressBar(0, 100, 77)
    for sitename in SiteCommMatrix:
        prog.increment(100./len(SiteCommMatrix))

        SiteCommMatrixT1T2[sitename] = {}
        items = SiteCommMatrix[sitename].keys()
        items.sort()

        status  = ' '
        for day in items:
            status = 'O'
            for crit in GetCriteriasList(sitename, criteria): # loop through the columns (criteria) that apply to this site
                if not SiteCommMatrix[sitename][day].has_key(crit):
                    infocol3 = {}
                    infocol3['Status'] = 'n/a'
                    infocol3['Color'] = 'white'
                    SiteCommMatrix[sitename][day][crit] = infocol3

                if SiteCommMatrix[sitename][day][crit]['Color'] == 'red':
                    status = 'E'

            if SiteCommMatrix[sitename][day]['Downtimes_top']['Color'] == 'brown':
                status = 'SD'

            # exclude sites that are not in SiteDB
            testdate = date(int(day[0:4]),int(day[5:7]),int(day[8:10]))
            sitedbtimeint = testdate - date(2009,11,03) # magic number - no idea where it comes from. Something to do with site db, of course
            if sitedbtimeint.days >= 0:
                if SiteCommMatrix[sitename][day].has_key('IsSiteInSiteDB'):
                    if SiteCommMatrix[sitename][day]['IsSiteInSiteDB']['Color'] == 'white':
                        status = 'n/a'

            if day == tinfo.todaystamp:
                status = ' '

            SiteCommMatrixT1T2[sitename][day] = status

    prog.finish()

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
                        
def EvaluateSiteReadiness(SiteCommMatrixT1T2, SiteCommGlobalMatrix, urls, daysSC, cinfo, tinfo):
    # fill SiteCommGlobalMatrix with actual readiness values
    prog = ProgressBar(0, 100, 77)
    sitesit = SiteCommMatrixT1T2.keys()
    sitesit.sort()
    for sitename in sitesit:
        prog.increment(100./len(sitesit))
        if not SiteCommGlobalMatrix.has_key(sitename):
            SiteCommGlobalMatrix[sitename]={}

        tier = sitename.split("_")[0]
        
        for i in range(0,cinfo.days-daysSC):
            delta = datetime.timedelta(i)
            dayloop = tinfo.today - delta
            dayloopstamp = dayloop.strftime("%Y-%m-%d")
            dm1 = datetime.timedelta(1)
            dayloopm1 = dayloop-dm1
            dayloopstampm1 = dayloopm1.strftime("%Y-%m-%d")
            dm2 = datetime.timedelta(2)
            dayloopm2 = dayloop-dm2
            dayloopstampm2 = dayloopm2.strftime("%Y-%m-%d")
            
            statusE = 0
            for j in range(0,daysSC):
                dd = datetime.timedelta(j);
                dayloop2 = dayloop-dd
                dayloopstamp2 = dayloop2.strftime("%Y-%m-%d")

                dayofweek2 = dayloop2.weekday()
                
                if SiteCommMatrixT1T2[sitename][dayloopstamp2] == 'E': # Daily Metric value
                    if ( tier == "T2" or tier == "T3") and (dayofweek2 == 5 or dayofweek2 == 6):
                        if not options.t2weekends: # skip Errors on weekends for T2s
                            continue
                    statusE += 1

            status = "n/a"
            colorst = "white"
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
        
            SiteCommGlobalMatrix[sitename][dayloopstamp] = status # set actual SR value

        if ( tier == "T2" or tier == "T3") :
            for i in range(0,cinfo.days-daysSC):
                d = datetime.timedelta(i);
                dsc = datetime.timedelta(cinfo.days-daysSC-1);
                dayloop = tinfo.today - dsc + d
                dayofweek = dayloop.weekday()
                dayloopstamp = dayloop.strftime("%Y-%m-%d")
                dm1 = datetime.timedelta(1)
                dayloopm1 = dayloop-dm1
                dayloopstampm1 = dayloopm1.strftime("%Y-%m-%d")

                if SiteCommMatrixT1T2[sitename][dayloopstamp] == 'E':
                    if dayofweek == 5 or dayofweek == 6: # id. weekends
                        if not options.t2weekends: # skip Errors on weekends for T2s
                            if i == 0 or i == 1:
                                SiteCommGlobalMatrix[sitename][dayloopstamp] == 'R'
                                continue
                            if SiteCommGlobalMatrix[sitename][dayloopstampm1] == 'SD':
                                SiteCommGlobalMatrix[sitename][dayloopstamp] = 'R'
                            else:
                                SiteCommGlobalMatrix[sitename][dayloopstamp] = SiteCommGlobalMatrix[sitename][dayloopstampm1]
                        
    prog.finish()

    # put in blank current day
    for sitename in SiteCommMatrixT1T2:
        for col in urls:
            if SiteCommMatrix[sitename][tinfo.todaystamp].has_key(col):
                SiteCommMatrix[sitename][tinfo.todaystamp][col]['Status'] = ' '
                SiteCommMatrix[sitename][tinfo.todaystamp][col]['Color'] = 'white'
                SiteCommGlobalMatrix[sitename][tinfo.todaystamp] = ' '

    # Correct some known sites metrics
    for sitename in SiteCommGlobalMatrix:
        for dt in SiteCommGlobalMatrix[sitename]:
            SiteCommGlobalMatrix[sitename][dt] = CorrectGlobalMatrix(sitename, dt, SiteCommGlobalMatrix[sitename][dt])
    for sitename in SiteCommMatrixT1T2:
        for dt in SiteCommMatrixT1T2[sitename]:
            SiteCommMatrixT1T2[sitename][dt] = CorrectGlobalMatrix(sitename, dt, SiteCommMatrixT1T2[sitename][dt])


cinfo = ColumnInfo()
tinfo = TimeInfo()
sites={}
SiteCommMatrix={}
SiteCommGlobalMatrix = {}
SiteCommMatrixT1T2 = {}
SiteCommStatistics = {}

# note: SiteCommMatrix is a summary of sites, with indices site name, time, column and values status, color, url, and validity
# SiteCommMatrix[site name][time][column] = [status, color, url, validity]

print "\nObtaining XML info from SSB 'commission' view\n"
SSBXMLParser(sites, cinfo.urls) # fill all info into sites

print "\nExtracting Daily Metrics for CMS sites\n"
GetDailyMetricStatus(sites, SiteCommMatrix, cinfo.colorCodes, cinfo.urls, cinfo, tinfo) # fill SiteCommMatrix with info from sites

print "\nExtracting Scheduled Downtime Topology Daily Metrics for CMS sites\n"
GetDailyScheduledDowntimeTopologyStatus(sites, SiteCommMatrix, cinfo.colorCodes, cinfo.urls, cinfo, tinfo) # set downtime values in SiteCommMatrix using info from sites

print "\nEvaluating Daily Status\n"
EvaluateDailyStatus(SiteCommMatrix, SiteCommMatrixT1T2, cinfo.criteria, tinfo) # set value for the 'Daily Metric' column in SiteCommMatrixT1T2

print "\nEvaluating Site Readiness\n"
EvaluateSiteReadiness(SiteCommMatrixT1T2, SiteCommGlobalMatrix, cinfo.urls, cinfo.daysSC, cinfo, tinfo) # set readiness values in SiteCommGlobalMatrix

# SiteCommMatrix --> allInfo
# SiteCommMatrixT1T2 --> dailyMetrics
# SiteCommGlobalMatrix --> readiValues
# SiteCommStatistics --> stats
class Matrices:
    def __init__(self, allInfo, dailyMetrics, readiValues, stats):
        self.allInfo      = allInfo
        self.dailyMetrics = dailyMetrics
        self.readiValues  = readiValues
        self.stats        = stats

matrices = Matrices(SiteCommMatrix, SiteCommMatrixT1T2, SiteCommGlobalMatrix, SiteCommStatistics)
owriter = OutputWriter(options, cinfo, matrices, tinfo)
owriter.write()

sys.exit(0)
