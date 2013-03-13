import re
import time
import io
import sys
import argparse
from collections import defaultdict

# usage:
# corpus is assumed to consist of independent lines in a single file. lines are split deterministically into three files: train, test and dev, using the ratio specified as an argument. 

# parse/validate arguments
argParser = argparse.ArgumentParser()
argParser.add_argument("-m2m", "--m2mFilename", type=str, help="filename that contains transliterations in the input m2m format")
args = argParser.parse_args()

m2mFile = io.open(args.m2mFilename, encoding='utf8')

totalSrcWords, totalTgtWords = 0, 0
totalSrcChars, totalTgtChars = 0, 0
linesCount = 0
for line in m2mFile:
  linesCount+= 1
  (src, tgt) = line.split('\t')
  srcChars, tgtChars = src.split(), tgt.split()
  totalSrcWords += 1
  totalTgtWords += 1
  for srcChar in srcChars:
    totalSrcChars += 1
    if srcChar == u'<space>':
      totalSrcWords += 1
  for tgtChar in tgtChars:
    totalTgtChars += 1
    if tgtChar == u'<space>':
      totalTgtWords += 1

print 'avg src words per named entity = {0}'.format(1.0 * totalSrcWords / linesCount)
print 'avg tgt words per named entity = {0}'.format(1.0 * totalTgtWords / linesCount)
print ''
print 'avg src chars per named entity = {0}'.format(1.0 * totalSrcChars / linesCount)
print 'avg tgt chars per named entity = {0}'.format(1.0 * totalTgtChars / linesCount)
print ''

m2mFile.close()
