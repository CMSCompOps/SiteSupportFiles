import urllib2
import simplejson

url = "http://dashb-ssb.cern.ch/dashboard/request.py/getsitereadinessrankdata?columnid=45&time=%s&sites=T2"
percentageThreshold = 0.6


def getData(url, headers=None):

    request = urllib2.Request(url, headers = headers)

    response = urllib2.urlopen(request)

    data = response.read()

    rows = simplejson.loads(data)

    return rows

def extractSitesUnderPercentage(dataRows, percentageThreshold):

    sites = []

    for row in dataRows['data']:
	siteName = row[0].split(' ')[0]

	sitePercentage = float(row[1][0][1])

	if sitePercentage < percentageThreshold:
	    sites.append(siteName)

    return sites


oneWeekDataRows = getData(url % '168', headers={"Accept":"application/json"})
threeMonthsDataRows = getData(url % '2184', headers={"Accept":"application/json"})


oneWeekBadSites = extractSitesUnderPercentage(oneWeekDataRows, percentageThreshold)
threeMonthsBadSites = extractSitesUnderPercentage(threeMonthsDataRows, percentageThreshold)


badSites = [val for val in oneWeekBadSites if val in threeMonthsBadSites]
print badSites


