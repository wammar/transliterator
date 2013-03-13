import re
import time
import io
import sys
import xml.dom.minidom
from collections import defaultdict

doc = xml.dom.minidom.parse(sys.argv[1])
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

if doc.childNodes[0].nodeName != 'TransliterationCorpus':
  print 'Surprising xml node!{0}'.format(doc.childNodes[0].nodeName)
  exit(1)
corpus = doc.childNodes[0]
#corpusId = corpus.attributes['CorpusID'].value

for namedEntity in corpus.getElementsByTagName('Name'):
  # find source name
  srcNode = namedEntity.getElementsByTagName('SourceName')[0]
  srcText = srcNode.childNodes[0].data
  srcText = textToM2m(srcText)
  # find each target name
  tgtNodes = namedEntity.getElementsByTagName('TargetName')
  for tgtNode in tgtNodes:
    tgtText = tgtNode.childNodes[0].data
    tgtText = textToM2m(tgtText)
    line = u'{0}\t{1}\n'.format(srcText, tgtText)
    out.write(line)

out.close()
