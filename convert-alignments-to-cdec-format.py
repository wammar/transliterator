import re
import time
import io
import sys
import xml.dom.minidom
from collections import defaultdict
from pygraph.classes.digraph import digraph

# this script does the following:
# - reads m2m alignments of transliteration pairs
# - encode the alignments in terms of src letters (input) and tgt sequences (labels)
# - writes a standard cdec training file with one name transliteration per line
# - writes a lattice cdec training file with all references of a src name in a lattice as a single training example
# - writes the rules (i.e. grammar or emission features) as required by cdec
# - for each of the feature templates (U01:U13, B51:B63), store all instantitations ovserved in the training pairs, and write them all (in addition to emission features) to the features file

alignments = io.open(sys.argv[1], encoding='utf8', mode='r')
train = io.open(sys.argv[2], encoding='utf8', mode='w')
if sys.argv[3] == 'false':
  trainLattice = false
else:
  trainLattice = io.open(sys.argv[3], encoding='utf8', mode='w')
labels = io.open(sys.argv[4], encoding='utf8', mode='w')
features = io.open(sys.argv[5], encoding='utf8', mode='w')

bugs = 0

def ListToLattice(labelSequenceList):
  global bugs
  # if there's only one sequences, don't create a lattice..
  if len(labelSequenceList) == 1:
    return labelSequenceList[0]

  # convert sequences from space separated labels into lists of labels
  for sequenceId in range(0, len(labelSequenceList)):
    labelSequenceList[sequenceId] = labelSequenceList[sequenceId].strip().split()
  labelGraph = digraph()

  # add nodes
  labelGraph.add_nodes([0, len(labelSequenceList[0])])
  for sequenceId in range(0, len(labelSequenceList)):
    for labelId in range(1, len(labelSequenceList[sequenceId])):
      labelGraph.add_nodes([(sequenceId,labelId)])

  # add edges
  for sequenceId in range(0, len(labelSequenceList)):
    sequence = labelSequenceList[sequenceId]
    for labelId in range(0, len(labelSequenceList[sequenceId])):
      if labelId == 0: 
        fromNode = 0
      else: 
        fromNode = (sequenceId,labelId)
      if labelId == len(sequence)-1: 
        toNode = len(sequence)
      else:
        toNode = (sequenceId,labelId+1)
      labelGraph.add_edge((fromNode,toNode))

  # topological order
  topologicalOrder = [0]
  for sequenceId in range(0, len(labelSequenceList)):
    sequence = labelSequenceList[sequenceId]
    for labelId in range(1, len(sequence)):
      topologicalOrder.append((sequenceId, labelId))
  topologicalOrder.append(len(labelSequenceList[0]))
  nodeToOrder = {}
  for order in range(0,len(topologicalOrder)):
    nodeToOrder[topologicalOrder[order]] = order

  # write the graph in python lattice format (plf)
  stringList = []
  for fromNode in topologicalOrder:
    nodeString = u'('
    for toNode in labelGraph.node_neighbors[fromNode]:
      if fromNode == 0 and toNode == len(labelSequenceList[0]):
        label = labelSequenceList[0][0]
        bugs += 1
      elif fromNode == 0:
        sequenceId = toNode[0]
        labelId = 0
        label = labelSequenceList[sequenceId][labelId]
      else:
        sequenceId = fromNode[0]
        labelId = fromNode[1]
        label = labelSequenceList[sequenceId][labelId]
      nodeString += u'(\'{0}\',0.0,{1}),'.format(label.replace('\'','\\\''), str(nodeToOrder[toNode] - nodeToOrder[fromNode]))
      if '\n' in nodeString:
        print fromNode
        print toNode
        print nodeToOrder
    nodeString += ')'
    if fromNode != len(labelSequenceList[0]):
      stringList.append(nodeString)

  # return lattice string in plf format
  return '(' + ''.join(stringList) + ')'

srcTokenToTgtLabels = defaultdict(set)

# label-unigrams
#F00|x[0]|y[0]
#U01|y[0]
u01 = set()
# src-unigrams, label-unigrams
#U02|x[0]|y[0]
u02 = set()
#U03|x[-1]|y[0]
u03 = set()
#U04|x[-2]|y[0]
u04 = set()
#U05|x[1]|y[0]
u05 = set()
#U06|x[2]|y[0]
u06 = set()
# src-bigrams, label-unigrams
#U07|x[-2]|x[-1]|y[0]
u07 = set()
#U08|x[-1]|x[0]|y[0]
u08 = set()
#U09|x[0]|x[1]|y[0]
u09 = set()
#U10|x[1]|x[2]|y[0]
u10 = set()
# src-trigrams, label-unigrams
#U11|x[-2]|x[-1]|x[0]|y[0]
u11 = set()
#U12|x[-1]|x[0]|x[1]|y[0]
u12 = set()
#U13|x[0]|x[1]|x[2]|y[0]
u13 = set()
#U14|yLen=#
#U15|yLen#=1
# label-bigrams
#B51|y[-1]|y[0]
b51 = set()
# src-unigrams, label-bigrams
#B52|x[0]|y[-1]|y[0]
b52 = set()
#B53|x[-1]|y[-1]|y[0]
b53 = set()
#B54|x[-2]|y[-1]|y[0]
b54 = set()
#B55|x[1]|y[-1]|y[0]
b55 = set()
#B56|x[2]|y[-1]|y[0]
b56 = set()
# src-bigrams, label-bigrams
#B57|x[-2]|x[-1]|y[-1]|y[0]
b57 = set()
#B58|x[-1]|x[0]|y[-1]|y[0]
b58 = set()
#B59|x[0]|x[1]|y[-1]|y[0]
b59 = set()
#B60|x[1]|x[2]|y[-1]|y[0]
b60 = set()
# src-trigrams, label-bigrams
#B61|x[-2]|x[-1]|x[0]|y[-1]|y[0]
b61 = set()
#B62|x[-1]|x[0]|x[1]|y[-1]|y[0]
b62 = set()
#B63|x[0]|x[1]|x[2]|y[-1]|y[0]
b63 = set()

prevSrc = u''
labelSequenceList = []
srcName = u''
for line in alignments:
  line = line.strip()
  [srcSegmentation,tgtSegmentation,flag,score] = line.split('\t')
  srcSequences = srcSegmentation.split('|')
  tgtSequences = tgtSegmentation.split('|')
  if len(srcSequences) != len(tgtSequences):
    print 'incorrect alignment output: {0}'.format(line)
    sys.exit(1)
  tgtName = u''
  srcToken = srcSegmentation.replace('|','').replace(':','').replace('<space>',' ')
  srcTokenIndex = -1
  yM1 = u'<s>'
  # write the previous src name, along with its many references
  if prevSrc == u'':
    prevSrc = srcToken
  if prevSrc != srcToken:
    if trainLattice:
      tgtLattice = ListToLattice(labelSequenceList)
      trainLattice.write(u'{0}||| {1}\n'.format(srcName, tgtLattice))
    labelSequenceList = []
    prevSrc = srcToken
  srcName = u''
  for i in range(0,len(srcSequences)-1):
    srcLetters = srcSequences[i].split(':')
    tgtLetters = tgtSequences[i]
    for j in range(0,len(srcLetters)):
      srcTokenIndex += 1
      # set x[0]
      if len(srcToken) > srcTokenIndex:
        x = srcToken[srcTokenIndex].replace(' ', '<space>')
      # set x[-1]
      if srcTokenIndex-1 < 0: xM1 = u'<s>'
      else: 
        if len(srcToken) > srcTokenIndex-1:
          xM1 = srcToken[srcTokenIndex - 1].replace(' ', '<space>')
      # set x[-2]
      if srcTokenIndex-2 < 0: xM2 = u'<s>'
      else: 
        if len(srcToken) > srcTokenIndex - 2:
          xM2 = srcToken[srcTokenIndex - 2].replace(' ', '<space>')
      # set x[1]
      if srcTokenIndex+1 >= len(srcToken): xP1 = u'</s>'
      else: xP1 = srcToken[srcTokenIndex + 1].replace(' ', '<space>')
      # set x[2]
      if srcTokenIndex+2 >= len(srcToken): xP2 = u'</s>'
      else: xP2 = srcToken[srcTokenIndex + 2].replace(' ', '<space>')

      # put src side in cdec training format
      srcName += u'{0} '.format(x)
      # set y[0]
      if j < len(srcLetters) - 1:
        y = u'<scan>'
      else:
        y = tgtLetters
      srcTokenToTgtLabels[srcLetters[j]].add(y)
      tgtName += u' {0}'.format(y)
      # collect features from this state in the transliteration pair
      u01.add(y)
      u02.add((x,y))
      u03.add((xM1,y))
      u04.add((xM2,y))
      u05.add((xP1,y))
      u06.add((xP2,y))
      u07.add((xM2,xM1,y))
      u08.add((xM1,x,y))
      u09.add((x,xP1,y))
      u10.add((xP1,xP2,y))
      u11.add((xM2,xM1,x,y))
      u12.add((xM1,x,xP1,y))
      u13.add((x,xP1,xP2,y))
      
      b51.add((yM1,y))
      b52.add((x,yM1,y))
      b53.add((xM1,yM1,y))
      b54.add((xM2,yM1,y))
      b55.add((xP1,yM1,y))
      b56.add((xP2,yM1,y))
      b57.add((xM2,xM1,yM1,y))
      b58.add((xM1,x,yM1,y))
      b59.add((x,xP1,yM1,y))
      b60.add((xP1,xP2,yM1,y))
      b61.add((xM2,xM1,x,yM1,y))
      b62.add((xM1,x,xP1,yM1,y))
      b63.add((x,xP1,xP2,yM1,y))

      # set yM1 for the next iteration
      yM1 = y
  # write the regular train file
  train.write(u'{0}|||{1}\n'.format(srcName, tgtName))

  # add this label sequence to the list of the current src
  labelSequenceList.append(tgtName.strip())

for token in srcTokenToTgtLabels.keys():
  for label in srcTokenToTgtLabels[token]:
    yLen = len(label.split(':'))
    if label == '_':
      yLen = 0
    elif label == '<scan>':
      yLen = 9
    labels.write(u'[X] ||| {0} ||| {1} ||| D00=1'.format(token, label))
    labels.write(u' F00|{0}|{1}=1'.format(token, label))
#    labels.write(u' U14|yLen={0}'.format(str(yLen)))
    labels.write(u' U15|yLen{0}=1'.format(str(yLen)))
    labels.write(u'\n')
                
    features.write(u'F00|{0}|{1} 0\n'.format(token, label))
  features.write(u'U14 0\n')
  features.write(u'U15 0\n')
labels.close()



#for feature in u01: features.write(u'U01|{0} 0\n'.format(feature))
#for feature in u02: features.write(u'U02|{0} 0\n'.format('|'.join(feature)))
#for feature in u03: features.write(u'U03|{0} 0\n'.format('|'.join(feature)))
#for feature in u04: features.write(u'U04|{0} 0\n'.format('|'.join(feature)))
#for feature in u05: features.write(u'U05|{0} 0\n'.format('|'.join(feature)))
#for feature in u06: features.write(u'U06|{0} 0\n'.format('|'.join(feature)))
#for feature in u07: features.write(u'U07|{0} 0\n'.format('|'.join(feature)))
for feature in u08: features.write(u'U08|{0} 0\n'.format('|'.join(feature)))
for feature in u09: features.write(u'U09|{0} 0\n'.format('|'.join(feature)))
#for feature in u10: features.write(u'U10|{0} 0\n'.format('|'.join(feature)))
for feature in u11: features.write(u'U11|{0} 0\n'.format('|'.join(feature)))
for feature in u12: features.write(u'U12|{0} 0\n'.format('|'.join(feature)))
for feature in u13: features.write(u'U13|{0} 0\n'.format('|'.join(feature)))

#for feature in b51: features.write(u'B51|{0} 0\n'.format('|'.join(feature)))
#for feature in b52: features.write(u'B52|{0} 0\n'.format('|'.join(feature)))
#for feature in b53: features.write(u'B53|{0} 0\n'.format('|'.join(feature)))
#for feature in b54: features.write(u'B54|{0} 0\n'.format('|'.join(feature)))
#for feature in b55: features.write(u'B55|{0} 0\n'.format('|'.join(feature)))
#for feature in b56: features.write(u'B56|{0} 0\n'.format('|'.join(feature)))
#for feature in b57: features.write(u'B57|{0} 0\n'.format('|'.join(feature)))
#for feature in b58: features.write(u'B58|{0} 0\n'.format('|'.join(feature)))
#for feature in b59: features.write(u'B59|{0} 0\n'.format('|'.join(feature)))
#for feature in b60: features.write(u'B60|{0} 0\n'.format('|'.join(feature)))
#for feature in b61: features.write(u'B61|{0} 0\n'.format('|'.join(feature)))
#for feature in b62: features.write(u'B62|{0} 0\n'.format('|'.join(feature)))
#for feature in b63: features.write(u'B63|{0} 0\n'.format('|'.join(feature)))

train.close()
trainLattice.close()
alignments.close()
features.close()
print 'bugs = {0}'.format(bugs)

