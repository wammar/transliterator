import re
import time
import io
import sys
import math
from collections import defaultdict

trainM2mFile = io.open(sys.argv[1], encoding='utf8', mode='r')
cdecKbestFile = io.open(sys.argv[2], encoding='utf8', mode='r')
probFile = io.open(sys.argv[3], encoding='utf8', mode='w')

def countCharsInLabel(label):
  chars = label.split(':')
  counter = 0
  for c in chars:
    if c == '_' or c == '<null>' or c == '<scan>':
      continue
    else:
      counter += 1
#  probFile.write(u'{0}={1}=of length {2}'.format(label, chars, counter))
  return counter

counts=defaultdict(lambda: defaultdict(int))

for line in trainM2mFile:
#  [x, y] = line.strip('\t').split()
  [x,y] = line.strip().split('\t')
  xLen, yLen = len(x.split()), len(y.split())
  counts[xLen][yLen] += 1

marginalCounts = defaultdict(int)
for xLen in counts.keys():
  for yLen in counts[xLen].keys():
    marginalCounts[xLen] += counts[xLen][yLen]

for line in cdecKbestFile:
  splits = line.split('|||')
  labels = splits[1].strip().split()
  xLen = len(labels)
  yLen = 0
  chars = []
  for label in labels:
    yLen += countCharsInLabel(label)
  if marginalCounts[xLen] == 0:
    marginalCounts[xLen] = 1
  probYLenGivenXLen = counts[xLen][yLen] * 1.0 / marginalCounts[xLen]
  if probYLenGivenXLen == 0:
    probYLenGivenXLen += 0.0000001
  logProbYLenGivenXLen = math.log(probYLenGivenXLen)

  probFile.write(u'{0}\n'.format(str(logProbYLenGivenXLen), yLen, xLen))

probFile.close()
cdecKbestFile.close()
trainM2mFile.close()
