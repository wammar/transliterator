import re
import time
import io
import sys
import math
from collections import defaultdict

cdecWeight = float(sys.argv[1])
charLmWeight = float(sys.argv[2])
classLmWeight = float(sys.argv[3])
lenWeight = float(sys.argv[4])

cdecKbestFile = io.open(sys.argv[5], encoding='utf8', mode='r')
charLmProbFile = io.open(sys.argv[6], encoding='utf8', mode='r')
classLmProbFile = io.open(sys.argv[7], encoding='utf8', mode='r')
lenProbFile = io.open(sys.argv[8], encoding='utf8', mode='r')

rerankedFile = io.open(sys.argv[9], encoding='utf8', mode='w')

rerankSize = int(sys.argv[10])

candidates = []

counter = 0
def rerankAndPrintCandidates():
  global counter
  global candidates
  global rerankedFile
  counter += 1
#  if counter % 50 == 0:
#    print counter
  candidates.sort()
  candidates.reverse()
  for candid in candidates:
    if candid == None:
      rerankedFile.write(u'\n')
    else:
      rerankedFile.write(u' {1} ||| {2} ||| score=f(cdec,charlm,classlm,len) ||| {0}=f({3},{4},{5},{6}) \n'.format(candid[0], candid[1], candid[2], candid[3], candid[4], candid[5], candid[6]))

currentId = 0
for line in cdecKbestFile:

  # no parses
  if line.strip() == '':
    currentId = -1
    rerankAndPrintCandidates()
    candidates = [None]
    continue

  # interpret line
  [lineId, word, derivation, cdecScore] = line.split('|||')
  lineId = int(lineId.strip())
  cdecScore = (1.0) * float(cdecScore.strip())
  word = word.strip()

  # new input
  if currentId != lineId:
    rerankAndPrintCandidates()
    currentId = lineId
    candidates = []

  # calculate score
  charLmScore = float(charLmProbFile.readline().strip())
  classLmScore = float(classLmProbFile.readline().strip())
  lenScore = float(lenProbFile.readline().strip())
  score = cdecScore * cdecWeight + charLmScore * charLmWeight + classLmScore * classLmWeight + lenScore * lenWeight
  if len(candidates) < rerankSize:
    candidates.append(tuple([score, currentId, word.strip(), cdecScore, charLmScore, classLmScore, lenScore]))

# process last input
rerankAndPrintCandidates()

rerankedFile.close()
cdecKbestFile.close()
charLmProbFile.close()
classLmProbFile.close()
lenProbFile.close()
