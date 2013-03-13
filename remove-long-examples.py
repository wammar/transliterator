import re
import time
import io
import sys
import math
from collections import defaultdict

maxInput = int(sys.argv[1])
inTrainFile = io.open(sys.argv[2], encoding='utf8', mode='r')
outTrainFile = io.open(sys.argv[3], encoding='utf8', mode='w')

for line in inTrainFile:
  if len(line.split('|||')[0].strip().split()) < maxInput:
    outTrainFile.write(line)

inTrainFile.close()
outTrainFile.close()
