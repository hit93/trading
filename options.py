#######################################
##                                   ##
## Options and Testing               ##
##                                   ##
#######################################
import sys, getopt
import csv
import glob

def withTime(line):
     return line[3]

class CallAndPullAccumulator(object):
    """docstring for CallAndPullAccumulator."""

    def __init__(self):
        super(CallAndPullAccumulator, self).__init__()

    def readCsvFile(self, fileName):
        # read csv content
        csvLines = [];
        with open(fileName) as csvfile:
            csvReader = csv.reader(csvfile, delimiter=',')

            for line in csvReader:
                csvLines.append(line);



        csvLines.sort(key=withTime)
        return csvLines

    """ Consolidate all the CSV with """
    def consolidateCallPut(self, timesVsCallPutAndOpenOrder, csvLines, callFlag=True):
        # random.sort(key=takeSecond)
        for csvLine in csvLines:
            # BANKNIFTY28500CE,2021/02/01,09:23,2800,2800,2800,2800,25,0
            date, time, openOrder = csvLine[1], csvLine[2], csvLine[8]
            key = date + "".join(time.split(":"))
            call = 0
            put = 0
            diff = 0
            sellOrBuy = None

            if (key not in timesVsCallPutAndOpenOrder):
                # timesVsCallPutAndOpenOrder[time] = ["time", "call", "put", "diff", "sellOrBuy"]
                timesVsCallPutAndOpenOrder[key] = [date, time, call, put, diff, sellOrBuy]
            else:
                date, timestamp, call, put, diff, sellOrBuy = timesVsCallPutAndOpenOrder[key]

            # print([time, call, put, diff, sellOrBuy])
            # call or put update
            if callFlag == True:
                call += int(openOrder)
            else:
                put += int(openOrder)
            diff = int(put - call)
            sellOrBuy = diff < 0 and "SELL" or "BUY"
            #TODO discard time other times
            timesVsCallPutAndOpenOrder[key] = [date, time, call, put, diff, sellOrBuy]

    def listFilesName(self, directory, stripPrice=0, upperLimit=0, lowerLimit=0):
        print(directory)
        fileNames = glob.glob(directory)

        if (stripPrice == 0):
            return fileNames

        filteredFileName = []
        if (upperLimit != 0 and upperLimit  != 0):
            for fileName in fileNames:
                stripFilePrice = int(fileName.split("/")[-1][9:-6])
                if stripFilePrice < (upperLimit) and stripFilePrice > (lowerLimit):
                    filteredFileName.append(fileName)

            return filteredFileName


        filteredFileName = []
        for fileName in fileNames:
            stripFilePrice = int(fileName.split("/")[-1][9:-6])
            diff = 100 * 20
            if stripFilePrice < (stripPrice + diff) and stripFilePrice > (stripPrice - diff):
                filteredFileName.append(fileName)

        return filteredFileName

    def readCsvFromDirectory(self, directory, stripPrice=0, upperLimit=0, lowerLimit=0, callFlag=False, timeDiffInMin=15):
        # list all .csv files and
        # timesVsCallPutAndOpenOrder = {"time": ["strike", "time", "call", "put", "diff", "sellOrBuy"]}
        timesVsCallPutAndOpenOrder = {"time": ["date","time", "call", "put", "diff", "sellOrBuy"]}
        print(timesVsCallPutAndOpenOrder)
        timesVsCallPutAndOpenOrder = {}
        fileNames = self.listFilesName(directory, stripPrice, upperLimit, lowerLimit)
        #
        for fileName in fileNames:
            # read files
            csvLines = self.readCsvFile(fileName)

            self.consolidateCallPut(timesVsCallPutAndOpenOrder, csvLines, callFlag=(fileName[-6:-4]) == "CE")
            # updated
        #
        for key in sorted(timesVsCallPutAndOpenOrder.keys()):

            #TODO discard time other times
            date, time, call, put, diff, sellOrBuy = timesVsCallPutAndOpenOrder[key]
            sellOrBuy = diff < 0 and "SELL" or "BUY"
            timesVsCallPutAndOpenOrder[key] = [date, time, call, put, diff, sellOrBuy]
            print(timesVsCallPutAndOpenOrder[key])

        ## Write output to csv files
        self.saveCSV(timesVsCallPutAndOpenOrder)


    def saveCSV(self, timesVsCallPutAndOpenOrder):
        # Store output to output file
        fieldnames = ["timestamp", "call", "put", "diff", "sellOrBuy"]
        print("Trying to store output in file: output_data.csv")
        with open("output_data.csv", 'w', newline="") as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            # writing the fields
            csvwriter.writerow(fieldnames)
            # writing the data rows
            for key in sorted(timesVsCallPutAndOpenOrder.keys()):
                csvwriter.writerow(timesVsCallPutAndOpenOrder[key])

        print("Successful")

def main(argv):
    inputDirecotry = ''
    stripPrice = 0
    upperLimit = 0
    lowerLimit = 0
    try:
        opts, args = getopt.getopt(argv,"hi::s::u::l::",["idir=", "strip=", "ulimit=", "llimt"])
    except getopt.GetoptError:
        print ('options.py -i <inputDirectoryForCSV> -s <stripPriceToLookFor>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('options.py -i <inputDirecotry>')
            sys.exit()
        elif opt in ("-i", "--idir"):
            inputDirecotry = arg
        elif opt in ("-s", "--strip"):
            stripPrice = int(arg)
        elif opt in ("-u", "--ulimit"):
            upperLimit = int(arg)
        elif opt in ("-l", "--llimit"):
            lowerLimit = int(arg)
    print('Input directory for csv is "', inputDirecotry, '"stripPrice=', '"', stripPrice, '"')
    print("Looking for CE and PE for range ", lowerLimit, " | ", stripPrice, " | ", upperLimit)

    # listFiles = option.listFilesName("/Users/gaurav.kumar/tmp/data1/*.csv");
    option = CallAndPullAccumulator()
    option.readCsvFromDirectory(inputDirecotry + "/*.csv", stripPrice, upperLimit, lowerLimit)

if __name__ == "__main__":
    main(sys.argv[1:])