import re
import time
import io
import sys
from collections import defaultdict

ratio = int(sys.argv[1])
alignments = io.open(sys.argv[2], encoding='utf8', mode='r')
train = io.open(sys.argv[3], encoding='utf8', mode='w')
test = io.open(sys.argv[4], encoding='utf8', mode='w')

counter = 0
group = u''
prevSrc = u''

for line in alignments:
  src = line.split('\t')[0]
  if prevSrc == u'':
    prevSrc = src
  if src == prevSrc:
    group += line
  else:
    prevSrc = u''
    counter += 1
    if counter < ratio + 1:
      train.write(group)
    else:
      test.write(group)
      counter = 0
      
    group = line

train.write(group)
train.close()
test.close()
alignments.close()
