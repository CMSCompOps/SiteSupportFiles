import sys, xml.dom.minidom, os, datetime, time
from xml import xpath
from datetime import date
from optparse import OptionParser
# local imports
from ProgressBar import ProgressBar
from TimeInfo import daterange
from datetime import timedelta as tdelta

class Matrices:
    # renaming scheme:
    # SiteCommMatrix --> columnValues: values for each column for each site
    # SiteCommMatrixT1T2 --> dailyMetrics: values for the 'Daily Metric'
    # SiteCommGlobalMatrix --> readiValues: actual 'Site Readiness' values
    # SiteCommStatistics --> stats: summary statistics
    def __init__(self):
        self.xmlInfo      = {}
        self.columnValues = {}
        self.dailyMetrics = {}
        self.readiValues  = {}
        self.stats        = {}
        # note: self.matrices.columnValues is a summary of self.matrices.xmlInfo, with indices site name, time, column and values status, color, url, and validity
        # self.matrices.columnValues[site name][time][column] = [status, color, url, validity]

class ReadinessMaker:
    def __init__(self, options, cinfo, tinfo):
        self.options = options
        self.cinfo = cinfo
        self.tinfo = tinfo
        self.matrices = Matrices()

    #----------------------------------------------------------------------------------------
    # return null ('n/a') info container
    def nullInfo(self):
        info = {}
        info['Status'] = 'n/a'
        info['Color'] = 'white'
        return info

    #----------------------------------------------------------------------------------------
    #        
    def ParseXML(self):
        print "\nObtaining XML info from SSB 'Site Readiness' view\n"
        prog = ProgressBar(0, 100, 77)

        xmlCacheDir = self.options.path_out + "/INPUTxmls"
        if not os.path.exists(xmlCacheDir):
            os.makedirs(xmlCacheDir)
        ColumnItems = self.cinfo.urls.keys()
        ColumnItems.sort()
        for col in ColumnItems:
            prog.increment(100./len(ColumnItems))
            url = self.cinfo.urls[col]
            xmlFile = xmlCacheDir + "/" + col + ".xml"
            if self.options.xml == 'false' and not os.path.exists(xmlCacheDir):
                print "\nWARNING: you cannot re-use the XML files as the files were not obtained before. Obtaining them...\n"
                self.options.xml = 'true'
            if self.options.xml == 'true': # download xml file if requested
                print "Column %s - Getting the url %s" % (col, url)
                os.system("curl -s -H 'Accept: text/xml'  '%s' > %s" % (url,xmlFile))
        
            f = file(xmlFile,'r') # read xml file that was either just written, or was written in the previous run
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

                voname = info['VOName']
                time = info['Time']
                xmlMatrix = self.matrices.xmlInfo
                if self.options.oneSite != "" and voname.find(self.options.oneSite) != 0: continue
                if not xmlMatrix.has_key(voname): # if site not already in dict, add an empty dict for it
                    xmlMatrix[voname] = {}
                if not xmlMatrix[voname].has_key(col): # if site entry doesn't already have this column, add an empty dict for this column
                    xmlMatrix[voname][col] = {}
                xmlMatrix[voname][col][time] = info # set the actual values

                # Correct some of the strings
                value = xmlMatrix[voname][col][time]['Status']
                if col=="HammerCloud" and value != "n/a":
                    value = str(int(float(value)))
                    if value.find("%") != 0:
                        value += "%"
                elif col=="SUMAvailability":
                    value = str(int(round(float(value))))
                    if value.find("%") != 0:
                        value += "%"
                xmlMatrix[voname][col][time]['Status'] = value
    
        prog.finish()
    
    #----------------------------------------------------------------------------------------
    #        
    def ShiftDayForMetric(self, datestamp, col):
        if col == "JobRobot" or col=="JobRobotDB" or col=="HammerCloud" or col == "SAMAvailability" or col == "SAMNagiosAvailability" or col == "SUMAvailability" or col.find("Good")==0:
            delta = datetime.timedelta(1)
            yesterday = datestamp - delta
            return yesterday.strftime("%Y-%m-%d")
        else:
            return datestamp.strftime("%Y-%m-%d")
        
    #----------------------------------------------------------------------------------------
    #        
    def FillSummaryMatrix(self):
        print "\nExtracting Column Info for CMS sites\n"
        prog = ProgressBar(0, 100, 77)
        for sitename in self.matrices.xmlInfo:
            prog.increment(100./len(self.matrices.xmlInfo))
            if not self.matrices.columnValues.has_key(sitename): # add site if not already there
                self.matrices.columnValues[sitename] = {}
            for col in self.cinfo.urls:
                if not self.matrices.xmlInfo[sitename].has_key(col) or col == 'Downtimes_top':
                    continue
    
                # set to null (default) values
                for iday in daterange(self.tinfo.today - tdelta(60), self.tinfo.today + tdelta(1)):
                    idaystamp = iday.strftime("%Y-%m-%d")
                    if not self.matrices.columnValues[sitename].has_key(idaystamp):
                        self.matrices.columnValues[sitename][idaystamp] = {}
                    if not self.matrices.columnValues[sitename][idaystamp].has_key(col):
                        self.matrices.columnValues[sitename][idaystamp][col] = {}
                    nullValues = {}
                    nullValues['Status'] = 'n/a'
                    nullValues['Color'] = 'white'
                    nullValues['URL'] = ' '
                    nullValues['validity'] = 0
                    self.matrices.columnValues[sitename][idaystamp][col] = nullValues
    
                items = self.matrices.xmlInfo[sitename][col].keys()
                items.sort()
                for coldate in items: # loop over each time/date combination
                    xmltime = datetime.datetime(*time.strptime(self.matrices.xmlInfo[sitename][col][coldate]['Time'], "%Y-%m-%d %H:%M:%S")[0:6])
                    xmlendtime = datetime.datetime(*time.strptime(self.matrices.xmlInfo[sitename][col][coldate]['EndTime'], "%Y-%m-%d %H:%M:%S")[0:6])
    
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
                        if dayloop > self.tinfo.today:
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
    
                        if self.cinfo.colorCodes[col][self.matrices.xmlInfo[sitename][col][coldate]['COLOR']] == "green":
                            status=self.matrices.xmlInfo[sitename][col][coldate]['Status']
                            statusu=self.matrices.xmlInfo[sitename][col][coldate]['URL']
                            statusc='green'
                            if self.matrices.xmlInfo[sitename][col][coldate]['Status']=="pend":
                                statusc='orange'
                                status='-'
                        elif self.cinfo.colorCodes[col][self.matrices.xmlInfo[sitename][col][coldate]['COLOR']] == "white":
                            statusu=' '
                            status='n/a'
                            statusc='white'
                        elif self.cinfo.colorCodes[col][self.matrices.xmlInfo[sitename][col][coldate]['COLOR']] == "red":
                            status=self.matrices.xmlInfo[sitename][col][coldate]['Status']
                            statusu=self.matrices.xmlInfo[sitename][col][coldate]['URL']
                            statusc='red'
                        else:
                            status='???'
                            statusu='???'
                            statusc='white'
    
                        dayloopstamp3 = self.ShiftDayForMetric(dayloop,col)
                        todayst = date(int(self.tinfo.todaystamp[0:4]),int(self.tinfo.todaystamp[5:7]),int(self.tinfo.todaystamp[8:10]))
                        dayloop3 = date(int(dayloopstamp3[0:4]),int(dayloopstamp3[5:7]),int(dayloopstamp3[8:10]))
    
                        if abs((dayloop3-todayst).days) > self.cinfo.days:
                            continue
    
                        # set the actual values in self.matrices.columnValues
                        infocol = {}
                        infocol['Status'] = status
                        infocol['Color'] = statusc
                        infocol['URL'] = statusu
                        infocol['validity'] = validity
                        if self.matrices.columnValues[sitename][dayloopstamp3][col].has_key('validity'):
                            if validity > self.matrices.columnValues[sitename][dayloopstamp3][col]['validity']:
                                self.matrices.columnValues[sitename][dayloopstamp3][col] = infocol
                        else:
                            self.matrices.columnValues[sitename][dayloopstamp3][col] = infocol
                                    
                        if dayloopstamp == self.tinfo.todaystamp:
                            infocol = {}
                            infocol['Status'] = ' '
                            infocol['Color'] = 'white'
                            infocol['URL'] = ' '
                            infocol['validity'] = '0'                       
                            self.matrices.columnValues[sitename][dayloopstamp][col] = infocol
    
        prog.finish()
    
    #----------------------------------------------------------------------------------------
    #        
    def GetDowntimes(self):
        print "\nExtracting Scheduled Downtime Topology Daily Metrics for CMS sites\n"
        # Leer Downtimes Topology (por ahora uso Time y EndTime para decidir cuanto duran los Downtimes)
        # por defecto todos los dias son Ok, y uso Time y EndTime para asignar los Downtimes.
        prog = ProgressBar(0, 100, 77)
        for sitename in self.matrices.xmlInfo:
            prog.increment(100./len(self.matrices.xmlInfo))
            if not self.matrices.columnValues.has_key(sitename): # add dict for site
                self.matrices.columnValues[sitename]={}
            for col in self.cinfo.urls: # loop over columns
                if col != "Downtimes_top":
                    continue
                infocol = {}
                if not self.matrices.xmlInfo[sitename].has_key(col):
                    self.matrices.xmlInfo[sitename][col] = {}
                # set downtime metric to green by default
                for i in range(0,self.cinfo.days+1):
                    delta = datetime.timedelta(self.cinfo.days-i);
                    dayloop = self.tinfo.today - delta
                    dayloopstamp = dayloop.strftime("%Y-%m-%d")

                    if not self.matrices.columnValues[sitename].has_key(dayloopstamp):
                        self.matrices.columnValues[sitename][dayloopstamp] = {}
                    infocol['Status'] = "Up"
                    infocol['Color'] = "green"
                    infocol['URL'] = ' ' 
                    self.matrices.columnValues[sitename][dayloopstamp][col] = infocol
    
                items = self.matrices.xmlInfo[sitename][col].keys()
                items.sort()
                for stdate in items:
                    colorTmp = self.cinfo.colorCodes[col][self.matrices.xmlInfo[sitename][col][stdate]['COLOR']] # color taken from self.matrices.xmlInfo
                    if colorTmp == "white" or  colorTmp == "green": # if they're ok, they don't need to be corrected for downtimes
                        continue
                    sttdate = stdate[0:stdate.find(" ")]
                    enddate = self.matrices.xmlInfo[sitename][col][stdate]['EndTime'][0:self.matrices.xmlInfo[sitename][col][stdate]['EndTime'].find(" ")]
                    cl = self.matrices.xmlInfo[sitename][col][stdate]['COLOR']
    
                    for i in range(0,self.cinfo.days+1):
                        delta = datetime.timedelta(self.cinfo.days-i);
                        dayloop = self.tinfo.today - delta
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
                                if self.matrices.columnValues[sitename].has_key(col):
                                    if self.matrices.columnValues[sitename][col].has_key(dayloopstamp):
                                        if self.matrices.columnValues[sitename][col][dayloopstamp].has_key('Color'):
                                            if self.matrices.columnValues[sitename][col][dayloopstamp].has_key('Color') == 'brown':
                                                kk+=1
                                                continue
    
                                # get downtime info from sites and put it into self.matrices.columnValues
                                values = {}
                                if colorTmp == 'brown':
                                    values['Color'] = 'brown'
                                    values['Status'] = 'SD'
                                    values['URL'] = self.matrices.xmlInfo[sitename][col][stdate]['URL']
                                if colorTmp == 'grey':
                                    if self.matrices.xmlInfo[sitename][col][stdate]['Status'].find("OUTAGE UNSCHEDULED") == 0:
                                        values['Color'] = 'silver'
                                        values['Status'] = 'UD'
                                        values['URL'] = self.matrices.xmlInfo[sitename][col][stdate]['URL']
                                    else:
                                        values['Color'] = 'yellow'
                                        values['Status'] = '~'
                                        values['URL'] = self.matrices.xmlInfo[sitename][col][stdate]['URL']
                                if colorTmp == 'yellow':
                                    values['Color'] = 'yellow'
                                    values['Status'] = '~'
                                    values['URL'] = self.matrices.xmlInfo[sitename][col][stdate]['URL']
                                
                                if dayloop > self.tinfo.today: break # ignore future downtimes
    
                                self.matrices.columnValues[sitename][dayloopstamp][col] = values
    
                                kk+=1
    
                                if (dayloopstamp == enddate): wloop=False
    
                # set today's downtime status to white
                nullVals = {}
                nullVals['Status'] = ' '
                nullVals['URL'] = ' '
                nullVals['Color'] = 'white'
                self.matrices.columnValues[sitename][self.tinfo.todaystamp][col] = nullVals
    
        prog.finish()

    #----------------------------------------------------------------------------------------
    #
#    def combineStatuses(self, status1, status2):
    def combineStatuses(self, receiverVal, giverVal):
#        if status2.find('(d)') == 0:
#            status2 = status2 + '\n + \n' + status1
#        else:
#            status2 = status2 + ' + ' + status1
        if receiverVal['Status'].find('(d)') == 0:
            receiverVal['Status'] = receiverVal['Status'] + '\n + \n' + giverVal['Status']
        else:
            receiverVal['Status'] = receiverVal['Status'] + ' + ' + giverVal['Status']

    #----------------------------------------------------------------------------------------
    #
    def combineDiskTape(self, receiverVal, giverVal):
        if receiverVal['Color'] == 'white': # receiver is n/a, so replace with giver
            receiverVal['Color']  = giverVal['Color']
            receiverVal['Status'] = giverVal['Status']
        elif giverVal['Color'] == 'red' and receiverVal['Color'] == 'green': # if one is bad and one is good, overall value should be red
            receiverVal['Color'] = 'red'
            self.combineStatuses(receiverVal, giverVal)
        elif giverVal['Color'] != 'white' and receiverVal['Color'] != 'white': # if neither is n/a, combine status strings with a '+'
            self.combineStatuses(receiverVal, giverVal)

    #----------------------------------------------------------------------------------------
    # give receiver site credit for giver site's value for the specified metrics
    def TransferCredit(self):
        print "\nTransfering credit for metrics\n"
        for transfer,transInfo in self.cinfo.creditTransfers.iteritems():
            receiver = transfer.split('<---')[0]
            giver    = transfer.split('<---')[1]
            action   = transInfo.keys()[0]
            metrics  = transInfo[action]
            if not self.matrices.columnValues.has_key(receiver) or not self.matrices.columnValues.has_key(giver):
                raise ValueError('bad receiver/giver in creditTransfers')
            items = self.matrices.columnValues[receiver].keys()
            items.sort()
            for day in items:
                for crit in metrics:
                    if not self.matrices.columnValues[giver][day].has_key(crit): # set to n/a if sites don't have this metric for this day
                        self.matrices.columnValues[giver][day][crit] = self.nullInfo()
                    if not self.matrices.columnValues[receiver][day].has_key(crit):
                        self.matrices.columnValues[receiver][day][crit] = self.nullInfo()
                    giverVal    = self.matrices.columnValues[giver][day][crit]
                    receiverVal = self.matrices.columnValues[receiver][day][crit]
                    if action == 'OW': # see comments in data/credit-transfers.conf
                        self.matrices.columnValues[receiver][day][crit] = self.matrices.columnValues[giver][day][crit]
                    elif action == 'ADD':
                        receiverVal = self.combineDiskTape(receiverVal,giverVal)
                    else:
                        raise ValueError('bad action in creditTransfers')
    
    #----------------------------------------------------------------------------------------
    #        
    def GetCriteriasList(self, sitename):
        # return list of columns (criteria) that apply to this site, based on its tier
        tier = sitename.split("_")[0]   
        return self.cinfo.criteria[tier]
    
    #----------------------------------------------------------------------------------------
    #        
    def EvaluateDailyMetric(self):
        print "\nEvaluating Daily Metric\n"
        # set value for the 'Daily Metric' column in self.matrices.dailyMetrics
        # NOTE: also sets n/a in columnValues for missing metrics
        prog = ProgressBar(0, 100, 77)
        for sitename in self.matrices.columnValues:
            prog.increment(100./len(self.matrices.columnValues))
            self.matrices.dailyMetrics[sitename] = {}
            items = self.matrices.columnValues[sitename].keys()
            items.sort()
            status  = ' '
            for day in items:
                status = 'O' # initial value is OK ('O')
                for crit in self.GetCriteriasList(sitename): # loop through the columns (criteria) that apply to this site and affect site status
                    if not self.matrices.columnValues[sitename][day].has_key(crit): # fill columnValues with 'n/a' for any missing values
                        self.matrices.columnValues[sitename][day][crit] = self.nullInfo()
                    if self.matrices.columnValues[sitename][day][crit]['Color'] == 'red': # if any individual metric is red, set status to error ('E')
                        status = 'E'
                if self.matrices.columnValues[sitename][day]['Downtimes_top']['Color'] == 'brown': # if site was in downtime set to 'SD'
                    status = 'SD'
    
                # exclude sites that are not in SiteDB
                testdate = date(int(day[0:4]),int(day[5:7]),int(day[8:10]))
                sitedbtimeint = testdate - date(2009,11,03) # magic number - no idea where it comes from.
                if sitedbtimeint.days >= 0:
                    if self.matrices.columnValues[sitename][day].has_key('IsSiteInSiteDB'):
                        if self.matrices.columnValues[sitename][day]['IsSiteInSiteDB']['Color'] == 'white':
                            status = 'n/a'
                            #status = status
    
                if day == self.tinfo.todaystamp: # set today's to the blank character
                    status = ' '
    
                self.matrices.dailyMetrics[sitename][day] = status
    
        prog.finish()
                            
    #----------------------------------------------------------------------------------------
    #        
    def EvaluateSiteReadiness(self):
        print "\nEvaluating Site Readiness\n"
        prog = ProgressBar(0, 100, 77)
        sitesit = self.matrices.dailyMetrics.keys()
        sitesit.sort()
        for sitename in sitesit:
            prog.increment(100./len(sitesit))
            if not self.matrices.readiValues.has_key(sitename):
                self.matrices.readiValues[sitename] = {}
            tier = sitename.split("_")[0]
            start = self.tinfo.today
            stop  = self.tinfo.today - datetime.timedelta(self.cinfo.days - self.cinfo.daysSC)
            for iday in daterange(start, stop, datetime.timedelta(-1)): # loop from today to the first day on which we try to calculate the readiness (default: today to (today - 60 - 7) days)
                idaystamp = iday.strftime("%Y-%m-%d")
                statusE = 0 # number of days over the previous daysSC days that dailyMetric was in error
                for jday in daterange(iday, iday - datetime.timedelta(self.cinfo.daysSC), datetime.timedelta(-1)): # loop over the dailyMetric values from the previous daysSC days
                    jdaystamp = jday.strftime("%Y-%m-%d")
                    if self.matrices.dailyMetrics[sitename][jdaystamp] == 'E': # if dailyMetric in error
                        if ( tier == "T2" or tier == "T3") and (jday.weekday() == 5 or jday.weekday() == 6):
                            if not self.options.t2weekends: # skip Errors on weekends for T2s
                                continue
                        statusE += 1
    
                status = "n/a"
                color = "white"
                previousDayStamp = (iday - datetime.timedelta(1)).strftime("%Y-%m-%d") # iday minus one day
                dailyMetric = self.matrices.dailyMetrics[sitename][idaystamp]
                if statusE > 2: # if in error for more than two of the last daysSC days
                    status="NR"
                    color="red"
                if dailyMetric == 'E' and statusE <= 2 : # if in error today
                    status="W"
                    color="yellow"
                if dailyMetric == 'O' and statusE <= 2 : # if ok
                    status="R"
                    color="green"
                if dailyMetric == 'O' and self.matrices.dailyMetrics[sitename][previousDayStamp] == 'O':
                    status="R"
                    color="green"
                if dailyMetric == 'SD':
                    status='SD'
                    color="brown"
                self.matrices.readiValues[sitename][idaystamp] = status # set actual SR value

            # correct weekend t2 and t3 readiness values to 'R' if they're in downtime, otherwise to friday's value
            if tier=="T2" or tier=="T3":
                start = self.tinfo.today - datetime.timedelta(self.cinfo.days - self.cinfo.daysSC - 3)
                stop  = self.tinfo.today
                for iday in daterange(start, stop):
                    idaystamp = iday.strftime("%Y-%m-%d")
                    previousDayStamp = (iday - datetime.timedelta(1)).strftime("%Y-%m-%d")
                    if self.matrices.dailyMetrics[sitename][idaystamp] == 'E':
                        if iday.weekday() == 5 or iday.weekday() == 6: # id. weekends
                            if not self.options.t2weekends: # skip Errors on weekends for T2s
                                if self.matrices.readiValues[sitename][previousDayStamp] == 'SD':
                                    self.matrices.readiValues[sitename][idaystamp] = 'R'
                                else:
                                    self.matrices.readiValues[sitename][idaystamp] = self.matrices.readiValues[sitename][previousDayStamp]
                            
        prog.finish()
    
        # put in blank current day
        for sitename in self.matrices.dailyMetrics:
            for col in self.cinfo.urls:
                if self.matrices.columnValues[sitename][self.tinfo.todaystamp].has_key(col):
                    self.matrices.columnValues[sitename][self.tinfo.todaystamp][col]['Status'] = ' '
                    self.matrices.columnValues[sitename][self.tinfo.todaystamp][col]['Color'] = 'white'
                    self.matrices.readiValues[sitename][self.tinfo.todaystamp] = ' '
    
    #----------------------------------------------------------------------------------------
    #
    def MakeReadiness(self):
        self.ParseXML()              # fill all info into matrices.xmlInfo
        self.FillSummaryMatrix()     # fill matrices.columnValues with a summary of matrices.xmlInfo
        self.GetDowntimes()          # set downtime values in matrices.columnValues using info from matrices.xmlInfo
        self.TransferCredit()        # give receiver site credit for giver site's value for the specified metrics
        self.EvaluateDailyMetric()   # set value for the 'Daily Metric' column in matrices.dailyMetrics (NOTE: also sets n/a in columnValues for missing metrics)
        self.EvaluateSiteReadiness() # set readiness values in matrices.readiValues
