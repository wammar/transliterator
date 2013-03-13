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
argParser.add_argument("-in", "--inputFile", type=str, help="input file which includes a patronymic name as the middle name in each src named entity")
argParser.add_argument("-out", "--outputFile", type=str, help="output file which have the patronymic name removed")
args = argParser.parse_args()

inFile = io.open(args.inputFile, encoding='utf8')
outFile = io.open(args.outputFile, encoding='utf8', mode='w')

for inLine in inFile:
  srcName, tgtName = inLine.split('|||')
  (first, patronymic, last) = srcName.split()
  outLine = u'{0} {1} |||{2}'.format(first, last, tgtName)
  outFile.write(outLine)

inFile.close()
outFile.close()
