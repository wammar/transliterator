import re
import time
import io
import sys
import xml.dom.minidom
from collections import defaultdict

doc = xml.dom.minidom.parse(sys.argv[1])
out = io.open(sys.argv[2], encoding='utf8', mode='w')
textFormat = False
if len(sys.argv) > 3:
  textFormat = sys.argv[3]

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
  if textFormat == 'upper':
    srcText = srcText.upper()
  elif textFormat == 'lower':
    srcText = srcText.lower()
  srcText = textToM2m(srcText)
  out.write(u'{0}\n'.format(srcText))

out.close()
