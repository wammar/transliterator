import re
import time
import io
import sys
from collections import defaultdict
import math

m2mFile = io.open(sys.argv[1], encoding='utf8', mode='r')
modelFile = io.open(sys.argv[2], encoding='utf8', mode='w')

counts = defaultdict(lambda:defaultdict(int))
marginal = defaultdict(int)
for line in m2mFile:
  [src,tgt] = line.split('\t')
  counts[len(src.split())][len(tgt.split())] += 1
  marginal[len(src.split())] += 1

for srcLen in counts.keys():
  for tgtLen in counts[srcLen].keys():
    modelFile.write(u'logp({0}|{1})={2}\n'.format(tgtLen, srcLen, 1.0 * math.log(1.0 * counts[srcLen][tgtLen] / marginal[srcLen])))

m2mFile.close()
modelFile.close()
