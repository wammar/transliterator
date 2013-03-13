import re
import time
import io
import sys
from collections import defaultdict
import accBackend

inFile = io.open(sys.argv[1], encoding='utf8', mode='r')
outFile = io.open(sys.argv[2], encoding='utf8', mode='r')
refFile = io.open(sys.argv[3], encoding='utf8', mode='r')
accFile = io.open(sys.argv[4], encoding='utf8', mode='w')

kBestFormat = False
if len(sys.argv) > 5:
  kBestFormat = sys.argv[5]

oneBestList = []
if kBestFormat:
  for line in outFile:
    splits = line.strip().split('|||')
    if len(oneBestList) == int(splits[0].strip()):
      oneBest = splits[1].strip().replace(' ', '').replace('<scan>', '').replace(':', '').replace('_', '')
#      print 'id={0},len={1},adding:{2}'.format(splits[0],len(oneBestList),oneBest)
      oneBestList.append(oneBest)
    elif len(oneBestList) > int(splits[0].strip()):
      continue
    elif len(oneBestList) < int(splits[0].strip()):
      while len(oneBestList) < int(splits[0].strip()):
        oneBestList.append('ERROR')
      oneBestList.append(splits[1].strip().replace(' ', '').replace('<scan>', '').replace(':', '').replace('_', ''))
else:
  for line in outFile:
    oneBestList.append(line.strip().replace(' ', '').replace('<scan>', '').replace(':', '').replace('_', ''))

refsList = []
for out in oneBestList:
  refLine = refFile.readline()
  inLine = inFile.readline()
  ref = set(refLine.strip().split())
  refsList.append(ref)
  if out in ref:
    accFile.write(u'^^^^\n')
  else:
    accFile.write(u'vvvv\n')
  accFile.write(u'\tin:{0}\n\tout:{1}\n\tref:{2}\n'.format(inLine.strip(), out, refLine.strip()))

(correct, incorrect, acc) = accBackend.computeAccAt1(refsList, oneBestList)
accFile.write(u'{0} correct\n{1} incorrect\n{2} ACC\n'.format(correct, incorrect, acc))

outFile.close()
refFile.close()
accFile.close()
inFile.close()
