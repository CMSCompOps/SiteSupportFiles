import string

class ColumnInfo:
    def __init__(self):
        webserver="http://dashb-ssb.cern.ch" #"http://dashb-ssb-dev.cern.ch"
        
        self.urls = {}  # SSB URLs Matrix
        self.criteria = {'T0':[],'T1':[],'T2':[],'T3':[]} # which columns to use for which tiers
        self.colorCodes = {}  # color codes
        self.metorder = {}            # metric order
        self.metlegends = {}          # metric legends
        self.days = 0        # Number of days for which we'll retrieve information from SSB
        self.daysSC = 0      # Number of previous days on which the current day's readiness depends
        self.daysToShow = 0  # Number of days to show in html
        self.colors = {}
        self.creditTransfers = {} # method for transfering credit for metric values between sites (eg to account for disk/tape separation)
        
        tmpf = open("data/readiness.conf")
        for line in tmpf:
            if line[0] == '#':
                continue
            words = line.split()
            if line[0] == '^': # single parameters
                words[0] = words[0].replace('^','')
                if   words[0] == 'days':       self.days       = int(words[1])
                elif words[0] == 'daysSC':     self.daysSC     = int(words[1])
                elif words[0] == 'daysToShow': self.daysToShow = int(words[1])
                else:
                    print '\nERROR bad config file\n'
                    sys.exit()
                continue
            colName = words[0]
            if self.days == 0 or self.daysSC == 0 or self.daysToShow == 0:
                print 'ERROR need to set self.days in config'
                sys.exit()
            url = webserver + '/dashboard/request.py/getplotdata?columnid=' + words[1] + '&batch=1&time=' + str(self.days*24)
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

        tmpf = open("data/credit-transfers.conf")
        for line in tmpf:
            if line[0] == '#':
                continue
            words = line.split()
            receiver = words[0]
            action   = words[1]
            giver    = words[2]
            metrics = words[3].split(',')
            self.creditTransfers[receiver+'<---'+giver] = { action : metrics }
        
        tmpf.close()
