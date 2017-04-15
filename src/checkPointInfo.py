"""
These functions are mainly used to retrieve geographic point data
from Google Street View Metadata API. It retrieves data by small
batches of points in a file.
"""

import sys
from googleStreetView import GoogleStreetView
from config import CONFIG


def getPointInfo(startNum, batchSize):
    """
    Start to retrieve data from Google Street View Metadata API.
    :param startNum:
    :param batchSize:
    """
    # TODO: modify it to do the batch processing automatically so that data will not be loaded for many times.
    points = readPoints(CONFIG["shapefile"]["intersectoinPointFile"])
    outputFilename = CONFIG["shapefile"]["pointInfoFilename"]
    print "start=%d, delta=%d" % (startNum, batchSize)
    getPointInfoToFile(points[startNum:startNum + batchSize], outputFilename)


def readPoints(filename):
    points = []
    inputData = open(filename, 'r')
    for line in inputData.readlines():
        data = line.strip().split("|")
        points.append(data[0])
    inputData.close()
    return points


def getPointInfoToFile(points, filename):
    lines = []
    lineFormat = "%s==Actual Location:%s,%s|date:%s"

    counter = {}
    counter["no date"] = 0

    headingsZero = CONFIG["gmap"]["headings"][0]

    prog = 0
    for point in points:
        lngLat = [float(p) for p in point.split(",")]
        param = GoogleStreetView.makeParameterDict(lngLat[1], lngLat[0], headingsZero)
        info = GoogleStreetView.getMetadata(param)
        if info["status"] == GoogleStreetView.OK:
            if 'date' in info:
                data = lineFormat % (point, info['location']['lng'], info['location']['lat'], info['date'])
            else:
                counter['no date'] += 1
                data = lineFormat % (point, info['location']['lng'], info['location']['lat'], "0000-00")
            lines.append(data)
        else:
            print "Point err:", point

        prog += 1
        if prog % 10 == 0:
            sys.stdout.write("\r%d" % prog)

    print "\nnumber of points that have no date: %d" % counter['no date']

    lines = "\n".join(lines)
    lines += "\n"
    output = open(filename, 'a')
    output.writelines(lines)
    output.close()


def getYearMonth(filename):
    """
    Parse the year and month data from a file generated by "getPointInfo" function above.
    :param filename:
    :return: a list of [year, month] data.
    """
    f = open(filename, 'r')
    data = [line.strip("\n").split("==") for line in f.readlines()]
    f.close()
    yearMonth = [getYearMonthTuple(d) for d in data]
    return yearMonth


def getYearMonthTuple(date):
    ym = date[1].split("|")[1].split(":")[1].split("-")
    return int(ym[0]), int(ym[1])


def findYearMonthDist(yearMonth):
    counter = {}
    for ym in yearMonth:
        if ym not in counter:
            counter[ym] = 1
        else:
            counter[ym] += 1
    printDictByKeyOrder(counter)


def printDictByKeyOrder(counter):
    keys = counter.keys()
    keys.sort()
    for key in keys:
        print key, counter[key]


def findMaxMinYearMonth(yearMonth):
    ym = list(set(yearMonth))
    ym.sort()
    print "Min:", ym[0]
    print "max:", ym[-1]


def readTargetPoints(filename):
    f = open(filename, 'r')
    points = [p.split("==")[0] for p in f.readlines()]
    return points


def check():
    # check what data is processed
    inputFilename = "../validIntersectionPoints_nonduplicate.data"
    orgPoints = set(readPoints(inputFilename)[:10])
    targetPoints = set(readTargetPoints("../point_info.data"))

    i = 0
    for p in targetPoints:
        if p not in orgPoints:
            print p
            i += 1
    print "total diff = %d" % i


if __name__ == "__main__":
    startPoint = 0
    batchSize = 5000
    getPointInfo(startPoint, batchSize)
