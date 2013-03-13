import re
import time
import io
import sys
from collections import defaultdict

def computeAccAt1(refsList, oneBestList):
  if len(oneBestList) == 0:
    print '1-best list is empty'
    sys.exit(1)
  if len(refsList) != len(oneBestList):
    print 'references list and 1-best list have different sizes'
    sys.exit(1)
  correct, incorrect = 0, 0
  for i in range(0, len(refsList)):
#    print 'oneBest={0}'.format(oneBestList[i])
#    print 'refsList={0}'.format(' '.join(refsList[i]))
    if oneBestList[i] in refsList[i]:
      correct += 1
    else:
      incorrect += 1
  acc = correct * 1.0 / (incorrect + correct)
  return (correct, incorrect, acc)

