import re
import time
import io
import sys
from collections import defaultdict

alignments = io.open(sys.argv[1], encoding='utf8', mode='r')
test = io.open(sys.argv[2], encoding='utf8', mode='w')
ref = io.open(sys.argv[3], encoding='utf8', mode='w')

prevSrc = u''
for line in alignments:
  line = line.strip()
  [srcSegmentation,tgtSegmentation,junk1,junk2] = line.split('\t')
  src = srcSegmentation.replace('|',' ').replace(':',' ')
  tgt = tgtSegmentation.replace('|','').replace(':','').replace('_','')
  if src != prevSrc and prevSrc != u'':
    ref.write(u'\n')
  ref.write(tgt + u' ')
  if src != prevSrc:
    prevSrc = src
    test.write(src + u'\n')
ref.write(u'\n')
test.close()
ref.close()
alignments.close()
