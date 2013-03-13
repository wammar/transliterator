import re
import time
import io
import sys
from collections import defaultdict

srcFile = io.open(sys.argv[1], encoding='utf8', mode='r')
tgtFile = io.open(sys.argv[2], encoding='utf8', mode='r')
srcIdFile = io.open(sys.argv[3], encoding='utf8', mode='r')
modelFile = io.open(sys.argv[4], encoding='utf8', mode='r')
probFile = io.open(sys.argv[5], encoding='utf8', mode='w')

srcLengths = []
for line in srcFile:
  srcLengths.append(len(line.split()))

lenProb = defaultdict(lambda:defaultdict(float))
for line in modelFile:
  [param, value] = line.split('=')
  param = param.replace('logp','').replace('(','').replace(')','')
  [tgtLen, srcLen] = param.split('|')
  [tgtLen, srcLen] = [int(tgtLen), int(srcLen)]
  value = float(value)
  lenProb[srcLen][tgtLen] = value

for tgt in tgtFile:
  srcId = int(srcIdFile.readline())
  srcLen = srcLengths[srcId]
  tgtLen = len(tgt.split())
  probFile.write(u'{0}\n'.format(lenProb[srcLen][tgtLen]))
  
srcFile.close()
tgtFile.close()
srcIdFile.close()
modelFile.close()
probFile.close()
