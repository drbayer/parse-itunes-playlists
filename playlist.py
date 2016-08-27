#!/usr/bin/env python3

import re, argparse
import sys
from matplotlib import pyplot
import plistlib
import numpy as np
import io

def getTracks(myFile):
    plist = plistlib.readPlist(myFile)
    myTracks = plist['Tracks']
    return myTracks

def findCommonTracks(fileNames):
    trackNameSets = []
    for fileName in fileNames:
        trackNames = set()
        tracks = getTracks(fileName)
        for trackId, track in tracks.items():
            try: 
                trackNames.add(track['Name'])
            except:
                pass
            trackNameSets.append(trackNames)
        
        commonTracks = set.intersection(*trackNameSets)
        if len(commonTracks) > 0:
            f = io.open("common.txt", 'w', encoding='utf8')
            for val in commonTracks:
                s = "%s\n" % val
                f.write(s)
            f.close()
            print("%d common tracks found. "
                  "Track names written to common.txt." % len(commonTracks))
        else:
            print("No common tracks!")

def plotStats(fileName):
    tracks = getTracks(fileName)
    ratings = []
    durations = []
    
    for trackId, track in tracks.items():
        try:
            ratings.append(track['Album Rating'])
            durations.append(track['Total Time'])
        except:
            pass

    if ratings == [] or durations == []:
        print("No valid Album Rating/Total Time data in %2." % fileName)
        return

    x = np.array(durations, np.int32)
    x = x/60000.0   # convert to minutes
    y = np.array(ratings, np.int32)
    pyplot.subplot(2, 1, 1)
    pyplot.plot(x, y, 'o')
    pyplot.axis([0, 1.05*np.max(x), -1, 110])
    pyplot.xlabel('Track duration')
    pyplot.ylabel('Track rating')

    pyplot.subplot(2, 1, 2)
    pyplot.hist(x, bins=20)
    pyplot.xlabel('Track duration')
    pyplot.ylabel('Count')

    pyplot.show()

def findDuplicates(fileName):
    print('Finding duplicate tracks in %s...' % fileName)

    tracks = getTracks(fileName)
    trackNames = {}
    for trackId, track in tracks.items():
        try:
            name = track['Name']
            duration = track['Total Time']
            if name in trackNames:
                if duration//1000 == trackNames[name][0]//1000:
                    count = trackNames[name][1]
                    trackNames[name] = (duration, count+1)
            else:
                trackNames[name] == (duration, 1)
        except:
            pass

    dups = []
    for k, v in trackNames.items():
        if v[1] > 1:
            dups.append((v[1], k))
    if len(dups) > 0:
        print("Found %d duplicates. Track names saved to dup.txt" % len(dups))
    else:
        print("No duplicate tracks found!")
    f = open("dups.txt", 'w')
    for val in dups:
        f.write("[%d] %s\n" % (val[0], val[1]))
    f.close()


def main():
    descStr = """
    This program analyzes playlist files (.xml) exported from iTunes.
    """
    parser = argparse.ArgumentParser(description=descStr)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--common', nargs='*', dest='plFiles', required=False)
    group.add_argument('--stats', dest='plFile', required=False)
    group.add_argument('--dup', dest='plFileD', required=False)

    args = parser.parse_args()
    if args.plFiles:
        findCommonTracks(args.plFiles)
    elif args.plFile:
        plotStats(args.plFile)
    elif args.plFileD:
        findDuplicates(args.plFileD)
    else:
        print("These are not the tracks you are looking for.")

if __name__ == '__main__':
    main()


