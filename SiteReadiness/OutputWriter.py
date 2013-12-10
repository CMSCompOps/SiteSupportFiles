import sys,datetime,time,os,pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pylab import *
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.cm as cm
from datetime import date
# local imports
from ProgressBar import ProgressBar

class OutputWriter:
    def __init__(self, options, cinfo, tinfo, matrices):
        self.options = options
        self.matrices = matrices
        self.ssbOutDir   = options.path_out + "/toSSB"
        self.htmlOutDir  = options.path_out + "/HTML"
        self.plotOutDir  = options.path_out + "/PLOTS"
        self.asciiOutDir = options.path_out + "/ASCii"
        self.fileSSB = self.ssbOutDir + '/SiteReadiness_SSBfeed.txt'
        self.fileReadinessStat = self.asciiOutDir + '/SiteReadiness_HistoricStatistics.txt'
        self.SRMatrixColors = { "R":"green", "W":"yellow", "NR":"red", "SD":"brown", " ":"white", "n/a":"white", "n/a*":"white" }
        self.cinfo = cinfo
        self.tinfo = tinfo
        self.reptime = "Report made on %s (UTC)\n" % self.tinfo.todaystampfile

        if not os.path.exists(self.ssbOutDir):   os.makedirs(self.ssbOutDir)
        if not os.path.exists(self.htmlOutDir):  os.makedirs(self.htmlOutDir)
        if not os.path.exists(self.plotOutDir):  os.makedirs(self.plotOutDir)
        if not os.path.exists(self.asciiOutDir): os.makedirs(self.asciiOutDir)
            
    #----------------------------------------------------------------------------------------
    # don't write any output for this site?
    def SkipSiteOutput(self, sitename):
        if sitename.find("T0_CH_CERN") == 0 : return 1
        if sitename.find("_Disk") >= 0 : return 1
        if sitename.find("T3_") == 0 : return 1
    
        # don't write info for sites that are 'n/a' for the entire time period
        dayVals = self.matrices.readiValues[sitename].keys()
        dayVals.sort()
        j = 0; k = 0
        for day in dayVals:
            j += 1
            if self.matrices.readiValues[sitename][day].find("n/a") == 0 or self.matrices.readiValues[sitename][day].find("n/a*") == 0:
                k += 1
        if j==k:
            return 1
        
        return 0
    
    #----------------------------------------------------------------------------------------
    # make file for SSB input
    def ProduceSiteReadinessSSBFile(self):
        print "\nProducing Site Readiness SSB input file\n"
        prog = ProgressBar(0, 100, 77)
        fileHandle = open(self.fileSSB,'w')
    
        sitesit = self.matrices.readiValues.keys()
        sitesit.sort()
        for sitename in sitesit:
            prog.increment(100./len(sitesit))
    
            if self.SkipSiteOutput(sitename): continue
    
            status = self.matrices.readiValues[sitename][self.tinfo.yesterdaystamp]
            colorst = self.SRMatrixColors[status]
    
            linkSSB = self.options.url + "/SiteReadiness/HTML/SiteReadinessReport_" + self.tinfo.timestamphtml + '.html'
            tofile = self.tinfo.todaystampfileSSB + '\t' + sitename + '\t' + status + '\t' + colorst + '\t' + linkSSB + "#" + sitename + "\n"
            fileHandle.write(tofile)
            
        fileHandle.close()
        prog.finish()

    #----------------------------------------------------------------------------------------
    # write SR info from last 15 days to html file    
    def ProduceSiteReadinessHTMLViews(self):
        print "\nProducing Site Readiness HTML view\n"
        colspans1 = str(self.cinfo.daysToShow+1)
        colspans2 = str(self.cinfo.daysToShow+1)
        colspans22 = str(self.cinfo.daysToShow+2)
        colspans3 = str(self.cinfo.daysSC)
        colspans4 = str(self.cinfo.daysSC)
        colspans5 = str(self.cinfo.daysToShow-self.cinfo.daysSC)
    
        dw = 45
        mw = 325
    
        tablew = str((self.cinfo.daysToShow)*dw+mw)
        dayw = str(dw)
        metricw = str(mw)
        daysw = str((self.cinfo.daysToShow)*dw)
        scdaysw1 = str((self.cinfo.daysSC)*dw)
        scdaysw = str((self.cinfo.daysSC)*dw)
    
        filehtml = self.htmlOutDir + '/SiteReadinessReport_' + self.tinfo.timestamphtml +'.html'
        fileHandle = open ( filehtml , 'w' )    
    
        fileHandle.write("<html><head><title>CMS Site Readiness</title><link type=\"text/css\" rel=\"stylesheet\" href=\"./style-css-reports.css\"/></head>\n")
        fileHandle.write("<body><center>\n")
    
        sitesit = self.matrices.readiValues.keys()
        sitesit.sort()
    
        prog = ProgressBar(0, 100, 77)
        for sitename in sitesit:
            prog.increment(100./len(sitesit))
            if not self.SkipSiteOutput(sitename): 
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
    
                dates = self.matrices.dailyMetrics[sitename].keys()
                dates.sort()
    
                fileHandle.write("<tr height=4><td width=" + metricw + "></td>\n")
                fileHandle.write("<td width=" + daysw + " colspan=" + colspans1 + " bgcolor=black></td></tr>\n")
            
                fileHandle.write("<tr><td width=" + metricw + "></td>\n")
                fileHandle.write("<td width=" + scdaysw1 + " colspan=" + colspans3 + "><div id=\"daily-metric-header\">Site Readiness Status: </div></td>\n")
            
                igdays=0
                for datesgm in dates: # write out 'Site Readiness Status' line
                    igdays+=1
                    if (self.cinfo.days - igdays)>(self.cinfo.daysToShow - self.cinfo.daysSC): continue
    
                    if not self.matrices.readiValues[sitename].has_key(datesgm):
                        continue
                    state=self.matrices.readiValues[sitename][datesgm]
                    datesgm1 = datesgm[8:10]
                    c = datetime.datetime(*time.strptime(datesgm,"%Y-%m-%d")[0:5])
                    fileHandle.write("<td width=\"" + dayw + "\" bgcolor=" + self.cinfo.colors[state] + "><div id=\"daily-metric\">" + state + "</div></td>\n")
    
                fileHandle.write("</tr><tr height=4><td width=" + metricw + "></td>\n")
                fileHandle.write("<td width=" + daysw + " colspan=" + colspans1 + " bgcolor=black></td></tr>\n")
                
                fileHandle.write("<tr height=7><td width=" + metricw + "></td>\n")
                fileHandle.write("<td width=" + daysw + " colspan=" + colspans1 + "></td></tr>\n")
                
                fileHandle.write("<tr height=4><td width=" + tablew + " colspan=" + colspans2 + " bgcolor=black></td></tr>\n")
    
                fileHandle.write("<td width=\"" + metricw + "\"><div id=\"daily-metric-header\">Daily Metric: </div></td>\n")
    
                igdays=0
    
                for datesgm in dates: # write out 'Daily Metric' line
    
                    igdays+=1
                    if (self.cinfo.days - igdays)>self.cinfo.daysToShow-1: continue
    
                    state = self.matrices.dailyMetrics[sitename][datesgm]
    
                    datesgm1 = datesgm[8:10]
                    c = datetime.datetime(*time.strptime(datesgm,"%Y-%m-%d")[0:5])
                    if (c.weekday() == 5 or c.weekday() == 6) and sitename.find('T2_') == 0: # id. weekends
                        if state!=" ":
                            fileHandle.write("<td width=\"" + dayw + "\" bgcolor=grey><div id=\"daily-metric\">" + state + "</div></td>\n")
                        else:
                            fileHandle.write("<td width=\"" + dayw + "\" bgcolor=white><div id=\"daily-metric\">" + state + "</div></td>\n")
                    else:
                        fileHandle.write("<td width=\"" + dayw + "\" bgcolor=" + self.cinfo.colors[state] + "><div id=\"daily-metric\">" + state + "</div></td>\n")
    
    
                fileHandle.write("<tr height=4><td width=" + tablew + " colspan=" + colspans2 + " bgcolor=black></td></tr>\n")
    
                fileHandle.write("<tr height=7><td width=" + metricw + "></td>\n")
                fileHandle.write("<td width=" + daysw + " colspan=" + colspans1 + "></td></tr>\n")
    
                fileHandle.write("<tr height=4><td width=" + tablew + " colspan=" + colspans2 + " bgcolor=black></td></tr>\n")
                
                indmetrics = self.cinfo.metorder.keys()
                indmetrics.sort()
    
                for metnumber in indmetrics:
    
                    met=self.cinfo.metorder[metnumber]
    
                    if not self.matrices.columnValues[sitename][dates[0]].has_key(met) or met == 'IsSiteInSiteDB': continue # ignore 
                    if sitename.find("T1_CH_CERN") == 0 and met == 'T1linksfromT0': continue # ignore 
    
                    if met == 'SAMAvailability':
                        fileHandle.write("<tr><td width=\"" + metricw + "\"><div id=\"metrics-header\"><font color=\"orange\">" + self.cinfo.metlegends[met] + ": </font></div></td>\n")
                    else:
                        fileHandle.write("<tr><td width=\"" + metricw + "\"><div id=\"metrics-header\">" + self.cinfo.metlegends[met] + ": </div></td>\n")
                        
                    igdays=0
                    for datesgm in dates: # write out a line for each constituent metric
                        igdays+=1
                        if (self.cinfo.days - igdays)>self.cinfo.daysToShow-1: continue
    
                        state = self.matrices.columnValues[sitename][datesgm][met]['Status']
                        colorst=self.matrices.columnValues[sitename][datesgm][met]['Color']
                        datesgm1 = datesgm[8:10]
                        c = datetime.datetime(*time.strptime(datesgm,"%Y-%m-%d")[0:5])
                        
                        if (c.weekday() == 5 or c.weekday() == 6) and sitename.find('T2_') == 0: # id. weekends
                            if state != " " :
                                if self.matrices.columnValues[sitename][datesgm][met].has_key('URL') and self.matrices.columnValues[sitename][datesgm][met]['URL'] != ' ' :
                                    stateurl=self.matrices.columnValues[sitename][datesgm][met]['URL']
                                    fileHandle.write("<td width=\"" + dayw + "\" bgcolor=grey><a href=\""+stateurl+"\">"+"<div id=\"metrics2\">" + state + "</div></a></td>\n")
                                else:
                                    fileHandle.write("<td width=\"" + dayw + "\" bgcolor=grey><div id=\"metrics2\">" + state + "</div></td>\n")
                            else:
                                    fileHandle.write("<td width=\"" + dayw + "\" bgcolor=white><div id=\"metrics2\">" + state + "</div></td>\n")
                        else:
                            if self.matrices.columnValues[sitename][datesgm][met].has_key('URL') and self.matrices.columnValues[sitename][datesgm][met]['URL'] != ' ' :
                                stateurl=self.matrices.columnValues[sitename][datesgm][met]['URL']
                                fileHandle.write("<td width=\"" + dayw + "\" bgcolor=" + colorst + "><a href=\""+stateurl+"\">"+"<div id=\"metrics2\">" + state + "</div></a></td>\n")
                            else:
                                fileHandle.write("<td width=\"" + dayw + "\" bgcolor=" + colorst + "><div id=\"metrics2\">" + state + "</div></td>\n")
                    fileHandle.write("</tr>\n")
                    
                fileHandle.write("<tr height=4><td width=" + tablew + " colspan=" + colspans22 + " bgcolor=black></td></tr>\n")
                fileHandle.write("<tr height=4><td width=" + metricw + "></td>\n")
    
                igdays=0
                
                for datesgm in dates:
                    igdays+=1
    
                    if (self.cinfo.days - igdays)>self.cinfo.daysToShow-1: continue
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
                    if (self.cinfo.days - igdays)>self.cinfo.daysToShow-1: continue
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
                
                fileHandle.write("<div id=\"leg1\">" + self.reptime + "</div>\n")
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
        prog.finish()

    #----------------------------------------------------------------------------------------
    # Evaluate statistics for Site Readiness  (last week, last month)
    def ProduceSiteReadinessStatistics(self):
        print "\nProducing Site Readiness Statistics\n"
        sitesit = self.matrices.readiValues.keys()
        sitesit.sort()
        prog = ProgressBar(0, 100, 77)
        for dayspan in 30, 15, 7:
            prog.increment(100./3.)
            for sitename in sitesit:
                if self.SkipSiteOutput(sitename): continue
                
                countR = 0;  countW = 0;  countNR = 0;  countSD = 0;  countNA = 0
                infostats2 = {}
                if not self.matrices.stats.has_key(sitename):
                    self.matrices.stats[sitename]={}        
    
                for i in range(0,dayspan):
                    deltaT = datetime.timedelta(i)
                    datestamp = self.tinfo.yesterday - deltaT
    
                    state = self.matrices.readiValues[sitename][datestamp.strftime("%Y-%m-%d")]
                    
                    if state == "R":  countR  += 1
                    if state == "W":  countW  += 1
                    if state == "NR": countNR += 1
                    if state == "SD": countSD += 1
                    if state.find("n/a") == 0: countNA += 1
                    
                if not self.matrices.stats[sitename].has_key(dayspan):
                    self.matrices.stats[sitename][dayspan]={}   
    
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
                
                self.matrices.stats[sitename][dayspan]=infostats2
    
        prog.finish()

    #----------------------------------------------------------------------------------------
    # 
    def ProduceSiteReadinessSSBFiles(self):
        print "\nProducing Site Readiness SSB files to commission view\n"
        prog = ProgressBar(0, 100, 77)
        for dayspan in 30, 15, 7:
            prog.increment(100./3.)
            fileSSBRanking = self.ssbOutDir + '/SiteReadinessRanking_SSBfeed_last' + str(dayspan) + 'days.txt' 
            fileHandle = open ( fileSSBRanking , 'w' )
    
            sitesit = self.matrices.readiValues.keys()
            sitesit.sort()
            for sitename in sitesit:
                if self.SkipSiteOutput(sitename): continue
                pl = "R+Wcorr_perc"
                color = "red"
                if sitename.find("T1") == 0 and self.matrices.stats[sitename][dayspan][pl]>90:
                    color="green"
                if sitename.find("T2") == 0 and self.matrices.stats[sitename][dayspan][pl]>80:
                    color="green"
                if self.matrices.stats[sitename][dayspan][pl] != "n/a":
                    filenameSSB = self.options.url + "/SiteReadiness/PLOTS/" + sitename.split("_")[0] + "_" + pl + "_last" + str(dayspan) + "days_" + self.tinfo.timestamphtml + ".png"
                    tofile = self.tinfo.todaystampfileSSB + '\t' + sitename + '\t' + str(self.matrices.stats[sitename][dayspan][pl]) + '\t' + color + '\t' + filenameSSB + "\n"
                    fileHandle.write(tofile)
                            
        fileHandle.close()
        prog.finish()

    #----------------------------------------------------------------------------------------
    #
    def ProduceSiteReadinessRankingPlots(self):
        print "\nProducing Site Readiness Ranking plots\n"
        prog = ProgressBar(0, 100, 77)
        sitesit = self.matrices.readiValues.keys()
        sitesit.sort()
        for dayspan in 30, 15, 7:
            prog.increment(100./3.)
            for pl in 'SD_perc', 'R+Wcorr_perc':
                for i in "T1","T2":
                    dataR = {}
                    filename = self.plotOutDir + "/" + i + "_" + pl + "_last" + str(dayspan) + "days_" + self.tinfo.timestamphtml + ".png"
    
                    for sitename in sitesit:
                        if not sitename.find(i+"_") == 0 : continue
                        if self.SkipSiteOutput(sitename): continue
                        if pl == 'SD_perc' and self.matrices.stats[sitename][dayspan][pl]==0.: continue # Do not show Up sites on SD plots.
                        dataR[sitename+" ("+str(self.matrices.stats[sitename][dayspan]["SD_perc"])+"%)"] = self.matrices.stats[sitename][dayspan][pl]
                    
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
                    dataS = dataR.items()
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
                        total += 1
                        if i == 'T1' and dataS[t][1] <= 90 : ent+=1
                        if i == 'T1' and dataS[t][1] > 90 : ent2+=1
                        if i == 'T2' and dataS[t][1] <= 80 : ent+=1
                        if i == 'T2' and dataS[t][1] > 80 : ent2+=1
    
                    if pl == 'R+Wcorr_perc':
                        metadataR = {'title':'%s Readiness Rank last %i days (+SD %%) [%s]' % (i,int(dayspan),self.tinfo.todaystamp), 'fixed-height':False }
                    if pl == 'SD_perc':
                        metadataR = {'title':'Rank for %s Scheduled Downtimes last %i days [%s]' % (i,int(dayspan),self.tinfo.todaystamp), 'fixed-height':True}
    
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
    
        prog.finish()

    def PrintDailyMetricsStats(self):
        print "\nPrinting Daily Metrics Statistics\n"
        prog = ProgressBar(0, 100, 77)
        fileHandle = open(self.asciiOutDir + '/Daily_HistoricStatistics.txt', 'w')
        sites = self.matrices.dailyMetrics.keys()
        sites.sort()
        for sitename in sites:
            dates = self.matrices.dailyMetrics[sitename].keys()
            dates.sort()
            continue
    
        for i in "T1","T2":
            prog.increment(100./2.)
            for dat in dates:
                countO=0; countE=0; countSD=0; countna=0
                for sitename in sites:
                    if sitename.find("T1_CH_CERN") == 0: continue
                    if not sitename.find(i+"_") == 0: continue
                    if self.SkipSiteOutput(sitename): continue
                    
                    state = self.matrices.dailyMetrics[sitename][dat]
                    if state == "O":
                        countO+=1
                    if state == "E":
                        countE+=1
                    if state.find("n/a") == 0:
                        countna+=1
                    if state == "SD":
                        countSD+=1
    
                if dat == self.tinfo.todaystamp: continue
                tofile = "Daily Metric " + i + " " + dat + " " + str(countE) + " " +  str(countO) + " " + str(countna) + " " + str(countSD) + " " + str(countE+countO+countSD+countna) + "\n"
                fileHandle.write(tofile)
    
        fileHandle.close()
        prog.finish()

    def PrintSiteReadinessMetricsStats(self):
        print "\nPrinting Site Readiness Metrics Statistics\n"
        prog = ProgressBar(0, 100, 77)
        fileHandle = open(self.fileReadinessStat , 'w')
        sites = self.matrices.readiValues.keys()
        sites.sort()
        for sitename in sites:
            dates = self.matrices.readiValues[sitename].keys()
            dates.sort()
            continue
    
        for i in "T1","T2":
            prog.increment(100./2.)
            for dat in dates:
                countR=0; countW=0; countNR=0; countSD=0; countna=0
                for sitename in sites:
                    if sitename.find("T1_CH_CERN") == 0: continue
                    if not sitename.find(i+"_") == 0: continue
                    if self.SkipSiteOutput(sitename): continue
                    
                    state = self.matrices.readiValues[sitename][dat]
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
    
                if dat == self.tinfo.todaystamp: continue
                tofile = "Site Readiness Metric " + i + " " + dat + " " + str(countR) + " " + str(countNR) + " " + str(countna) + " " + str(countW) + " " + str(countSD) + " " + str(countR+countNR+countW+countna+countSD) + "\n"
                fileHandle.write(tofile)
    
        fileHandle.close()
        prog.finish()
    
    def PrintDailyMetrics(self):
        prog = ProgressBar(0, 100, 77)
        indmetrics = self.cinfo.metorder.keys()
        indmetrics.sort()
        sites = self.matrices.columnValues.keys()
        sites.sort()
        for sitename in sites:
            prog.increment(100./3.)
            dates = self.matrices.dailyMetrics[sitename].keys()
            dates.sort()
            for dat in dates:
                if self.SkipSiteOutput(sitename): continue
                for metnumber in indmetrics:
                    met = self.cinfo.metorder[metnumber]
                    if not self.matrices.columnValues[sitename][dat].has_key(met) or met == 'IsSiteInSiteDB': continue # ignore 
    
                    if self.matrices.columnValues[sitename][dat][met].has_key('URL'):
                        url = self.matrices.columnValues[sitename][dat][met]['URL']
                    else:
                        url = "-"
                    print dat, sitename, met, self.matrices.columnValues[sitename][dat][met]['Status'], self.matrices.columnValues[sitename][dat][met]['Color'],url
    
        prog.finish()
    
                    
    def CreateSimbLinks(self):
        os.chdir(self.htmlOutDir)
        slinkhtml= './SiteReadinessReport.html'
        if os.path.isfile(slinkhtml): os.remove(slinkhtml)
        filehtml = self.htmlOutDir + '/SiteReadinessReport_' + self.tinfo.timestamphtml +'.html'
        os.symlink(os.path.split(filehtml)[1], slinkhtml)
        os.chdir(self.plotOutDir)
        for dayspan in 30, 15, 7:
            for pl in 'SD_perc', 'R+Wcorr_perc':
                for i in "T1","T2":
                    filepng = self.plotOutDir + "/" + i + "_" + pl + "_last" + str(dayspan) + "days_" + self.tinfo.timestamphtml + ".png"
                    slinkhtml = "./" + i + "_" + pl + "_last" + str(dayspan) + "days.png"
                    if os.path.isfile(slinkhtml): os.remove(slinkhtml)
                    os.symlink(os.path.split(filepng)[1],slinkhtml)
    
    # Matrices were renamed for clarity from original code, but we keep the .pck names the same
    # for backward compatibility (note, I don't know if anything actually uses the pickle files, but
    # we're playing it safe here)
    #
    # SiteCommMatrix --> columnValues
    # SiteCommMatrixT1T2 --> dailyMetrics
    # SiteCommGlobalMatrix --> readiValues
    # SiteCommStatistics --> stats
    def DumpPickleFiles(self):
        file = self.asciiOutDir + "/SiteCommMatrix.pck"
        file1 = open(file, "w")
        pickle.dump(self.matrices.columnValues, file1)
        file1.close()
    
        file = self.asciiOutDir + "/SiteCommMatrixT1T2.pck"
        file1 = open(file, "w")
        pickle.dump(self.matrices.dailyMetrics, file1)
        file1.close()
    
        file = self.asciiOutDir + "/SiteCommGlobalMatrix.pck"
        file1 = open(file, "w")
        pickle.dump(self.matrices.readiValues, file1)
        file1.close()

    #----------------------------------------------------------------------------------------
    # write all output
    def write(self):
        self.ProduceSiteReadinessSSBFile()
        self.ProduceSiteReadinessHTMLViews()
        self.ProduceSiteReadinessStatistics()
        self.ProduceSiteReadinessSSBFiles()
        self.ProduceSiteReadinessRankingPlots()
        self.PrintDailyMetricsStats()
        self.PrintSiteReadinessMetricsStats()
        self.CreateSimbLinks()
        self.DumpPickleFiles()
