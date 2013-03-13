import re
import time
import io
import sys
from collections import defaultdict


# usage python convert.py inputfile.bars outputfile.m2m {upper|lower}
namesFile = io.open(sys.argv[1], encoding='utf8', mode='r')
out = io.open(sys.argv[2], encoding='utf8', mode='w')
upper, lower = False, False
if len(sys.argv) > 3:
  if sys.argv[3] == 'upper':
    upper, lower = True, False
  elif sys.argv[3] == 'lower':
    upper, lower = False, True

def textToM2m(text):
  m2m = ''
  for c in text:
    m2m += ' '
    if c == ' ':
      m2m += '<space>'
    else:
      m2m += c
    m2m += ' '
  m2m = m2m.strip()
  if upper:
    m2m = m2m.uppercase()
  elif lower:
    m2m = m2m.lowercase()
  return m2m

for line in namesFile:
  (srcText,tgtText) = line.strip().split('|||')
  srcText = textToM2m(srcText.strip())
  tgtText = textToM2m(tgtText.strip())
  line = u'{0}\t{1}\n'.format(srcText, tgtText)
  out.write(line)

out.close()
namesFile.close()
