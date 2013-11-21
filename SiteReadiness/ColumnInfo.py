import string

class ColumnInfo:
    def __init__(self,days):
        webserver="http://dashb-ssb.cern.ch" #"http://dashb-ssb-dev.cern.ch"
        
        self.urls = {}  # SSB URLs Matrix
        self.criteria = {'T0':[],'T1':[],'T2':[],'T3':[]} # which columns to use for which tiers
        self.colorCodes = {}  # color codes
        self.metorder = {}            # metric order
        self.metlegends = {}          # metric legends
        
        tmpf = open("data/dashboard-columns.conf")
        for line in tmpf:
            if line[0] == '#':
                continue
            words = line.split()
            colName = words[0]
            url = webserver + '/dashboard/request.py/getplotdata?columnid=' + words[1] + '&batch=1&time=' + str(days*24)
            self.urls[colName] = url
            # which columns for which tiers
            tiers = words[2].split(',')
            for tier in tiers:
                if tier == '-':
                    continue
                self.criteria[tier].append(colName)
            # metric order
            if words[3] != '-':
                self.metorder[words[3]] = colName
            # legend
            self.metlegends[colName] = string.replace(words[4], '~', ' ')
            # colors
            self.colorCodes[colName] = {}
            colors = words[5].split(',')
            for pairStr in colors:
                pair = pairStr.split(':')
                if len(pair) != 2:
                    print 'ERROR! length not two'
                    sys.exit()
                self.colorCodes[colName].update({pair[0]:pair[1]}) # {index:color}
        
        tmpf.close()
        
        self.colors = {}
        tmpf = open("data/colors.conf")
        for line in tmpf:
            if line[0] == '#':
                continue
            words = line.split()
            label = words[0]
            if label == '_': # convention: underscore in config means a space
                label = ' '
            self.colors[label] = words[1]
        
        tmpf.close()
