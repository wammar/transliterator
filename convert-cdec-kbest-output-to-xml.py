import re
import time
import io
import sys
import xml.dom.minidom
#import xml.dom.ext
from collections import defaultdict

pretty_print = lambda f: u'\n'.join([line for line in xml.dom.minidom.parse(open(f)).toprettyxml(indent=u' '*2).split(u'\n') if line.strip()])

k = int(sys.argv[1])
src = sys.argv[2]
tgt = sys.argv[3]
groupId = sys.argv[4]
runId = sys.argv[5]
runType = sys.argv[6]
comments = sys.argv[7]
cdecIn = io.open(sys.argv[8], encoding='utf8', mode='r')
cdecOut = io.open(sys.argv[9], encoding='utf8', mode='r')
xmlOut = io.open(sys.argv[10], encoding='utf8', mode='w')
noParsesIn = io.open(sys.argv[11], encoding='utf8', mode='w')
noParsesId = io.open(sys.argv[12], encoding='utf8', mode='w')
OFFSET = int(sys.argv[13])

def decodeChar(encodedChar):
  if encodedChar == '_' or encodedChar == '<scan>':
    return ''
  if encodedChar == '<space>':
    return ' '
  return encodedChar

def labelsToText(labelsText):
  textParts = []
  for label in labelsText.split():
    for c in label.split(':'):
      textParts.append(decodeChar(c))
  text = ''.join(textParts).strip()
  if text == '':
    text = 'ERROR'
  return text

doc = xml.dom.minidom.Document()

results = doc.createElement('TransliterationTaskResults')
results.setAttribute('SourceLang', src)
results.setAttribute('TargetLang', tgt)
results.setAttribute('GroupID', groupId)
results.setAttribute('RunID', runId)
results.setAttribute('RunType', runType)
results.setAttribute('Comments', comments)
doc.appendChild(results)

tgtId = 0
nameId = OFFSET - 1
nameElement = False
#nameElement = doc.createElement('Name')
#nameElement.setAttribute('ID', str(nameId))
#results.appendChild(nameElement)
#srcName = labelsToText(cdecIn.readline().strip())
#srcNameElement = doc.createElement('SourceName')
#srcNameElement.appendChild(doc.createTextNode(srcName))
#nameElement.appendChild(srcNameElement)

counter = 0
for line in cdecOut:
  counter += 1
  if counter % 100 == 0:
    sys.stdout.write('.')
  if counter % 1000 == 0:
    sys.stdout.write('lines_read={0}\n'.format(counter))
    
  if line.strip() == '':

    # save previous input and its results
    if nameElement != False:
      results.appendChild(nameElement)

    # report the missing transliteration
    nameId += 1
    noParsesId.write(u'{0}\n'.format(nameId))
    inputLine = cdecIn.readline().strip()
    noParsesIn.write(u'{0}\n'.format(inputLine))

    # create an empty node in the results for the failed name
    tgtId = 1
    srcName = labelsToText(inputLine)
    srcNameElement = doc.createElement('SourceName')
    srcNameElement.appendChild(doc.createTextNode(srcName))
    tgtNameElement = doc.createElement('TargetName')
    tgtNameElement.setAttribute('ID', '1')
    tgtNameElement.appendChild(doc.createTextNode(srcName))
    nameElement = doc.createElement('Name')
    nameElement.setAttribute('ID', str(nameId))
    nameElement.appendChild(srcNameElement)
    nameElement.appendChild(tgtNameElement)
    results.appendChild(nameElement)

    continue
    
  [srcIdStr, trans, derivation, score] = line.split('|||')
  srcIdStr = srcIdStr.strip()
  trans = trans.strip()
  derivation = derivation.strip()
  score = score.strip()
  # if we moved to next input word, get ready for it
  if int(srcIdStr) + OFFSET == nameId + 1:

    # save previous input
    if nameElement != False:
      results.appendChild(nameElement)

    # ready for the new name
    tgtId = 0
    nameId += 1 # (nameId) and (srcIdStr + OFFSET) should always be in sync

    # create a new Name element and add a SourceName element to it
    srcName = labelsToText(cdecIn.readline().strip())
    srcNameElement = doc.createElement('SourceName')
    srcNameElement.appendChild(doc.createTextNode(srcName))
    nameElement = doc.createElement('Name')
    nameElement.setAttribute('ID', str(nameId))
    nameElement.appendChild(srcNameElement)

  elif int(srcIdStr) + OFFSET != nameId:
    print 'SOMETHING WENT WRONG'
    print 'srcIdStr={0}'.format(srcIdStr)
    print 'nameId={0}'.format(nameId)
    sys.exit(1)

  tgtId += 1
  if tgtId > k:
    continue
  trans = trans.strip()
  tgtName = labelsToText(trans)
  tgtNameElement = doc.createElement('TargetName')
  tgtNameElement.setAttribute('ID', str(tgtId))
  tgtNameElement.appendChild(doc.createTextNode(tgtName))
  nameElement.appendChild(tgtNameElement)

results.appendChild(nameElement)

uglyXml = doc.toprettyxml(indent=u'  ')
text_re = re.compile(u'>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)    
prettyXml = text_re.sub(u'>\g<1></', uglyXml)

xmlOut.write(prettyXml)
xmlOut.close()
cdecIn.close()
cdecOut.close()
noParsesIn.close()
noParsesId.close()
