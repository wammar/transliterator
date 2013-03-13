import re
import time
import io
import sys
import math
from collections import defaultdict
import rerankBackend

cdecWeight = float(sys.argv[1])
charLmWeight = float(sys.argv[2])
classLmWeight = float(sys.argv[3])
lenWeight = float(sys.argv[4])

cdecKbestFile = io.open(sys.argv[5], encoding='utf8', mode='r')
charLmProbFile = io.open(sys.argv[6], encoding='utf8', mode='r')
classLmProbFile = io.open(sys.argv[7], encoding='utf8', mode='r')
lenProbFile = io.open(sys.argv[8], encoding='utf8', mode='r')

refFile = io.open(sys.argv[9], encoding='utf8', mode='r')

bestWeightsFile = io.open(sys.argv[10], encoding='utf8', mode='w')

rerankSize = int(sys.argv[11])

# initial weight vector
weights = [cdecWeight, charLmWeight, classLmWeight, lenWeight]

# read references into refsList
refsList = []
# each line represents  one input
for line in refFile:
  currentInputRefs = line.split()
  refsList.append(currentInputRefs)
refFile.close()

# read kbest list and component scores
inputScoreList = []
kbestsList = []
# each line represents one output
currentId = 0 #input id
kbestPerInput = []
cdecScorePerInput = []
charLmScorePerInput = []
classLmScorePerInput = []
lenScorePerInput = []
for line in cdecKbestFile:
  # interpret line
  [lineId, word, derivation, cdecScore] = line.split('|||')
  lineId = int(lineId.strip())
  cdecScore = (1.0) * float(cdecScore.strip())
  word = word.strip().replace(':','').replace('_','').replace('<scan>','').replace(' ','')

  # new input
  if currentId != lineId:
    kbestsList.append(kbestPerInput)
    inputScoreList.append([cdecScorePerInput, charLmScorePerInput, classLmScorePerInput, lenScorePerInput])
    currentId = lineId
    kbestPerInput = []
    cdecScorePerInput = []
    charLmScorePerInput = []
    classLmScorePerInput = []
    lenScorePerInput = []

  # calculate score
  charLmScore = float(charLmProbFile.readline().strip())
  classLmScore = float(classLmProbFile.readline().strip())
  lenScore = float(lenProbFile.readline().strip())
  
  # add this candidate's information
  if len(kbestPerInput) < rerankSize:
    kbestPerInput.append(word)
    cdecScorePerInput.append(cdecScore)
    charLmScorePerInput.append(charLmScore)
    classLmScorePerInput.append(classLmScore)
    lenScorePerInput.append(lenScore)

# process last input
kbestsList.append(kbestPerInput)
inputScoreList.append([cdecScorePerInput, charLmScorePerInput, classLmScorePerInput, lenScorePerInput])

# find best weights
optimalWeights = rerankBackend.findBestWeights(weights,kbestsList,inputScoreList,refsList)
print optimalWeights
for weight in optimalWeights:
  bestWeightsFile.write(u'{0} '.format(weight))
bestWeightsFile.close()

cdecKbestFile.close()
charLmProbFile.close()
classLmProbFile.close()
lenProbFile.close()
