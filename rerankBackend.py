import re
import time
import io
import sys
import math
from collections import defaultdict
import accBackend
from scipy.optimize import fmin
from scipy.optimize import anneal

# weights = list of weights that multiply various scores
# scoreLists = list of the same size as weights. each element is a list of scores (to be multiplied with the corresponding weight in the weights list)
# kbest = list of target transliterations. this list must be of the same length as each element in scoreLists
# returns a list of sorted (score,candidate) tuples; i.e. the reranked kbest list
def rerank(weights,scoreLists,kbest):
  if len(weights) != len(scoreLists) or len(weights) == 0:
    print 'weights and scoreLists must be of the same size and not zero'
    sys.exit(1)
  for component in range(0, len(weights)):
    if len(scoreLists[component]) != len(kbest):
      print 'kbest and each list in scoreLists must be of equal size'
      sys.exit(1)
  scoreCandidateTuples = []
  for i in range(0, len(kbest)):
    candidateScore = 0
    for j in range(0, len(weights)):
      candidateScore += weights[j] * scoreLists[j][i]
    scoreCandidateTuples.append(tuple([candidateScore, kbest[i]]))
  scoreCandidateTuples.sort()
  scoreCandidateTuples.reverse()
  return scoreCandidateTuples

# len(inputScoreLists) == len(kbestLists)
# example of kbestLists of 2 inputs = [ ['1a', '1b', '1c'], ['2a', '2b'] ]

#                                                                <-cmp1->  <-cmp2>         <cm1>  <cm2>
# example of inputScoreLists of 2 inputs, and 2 components = [ [ [10,5,3], [4,5,6] ],    [ [4,2], [3,5] ] ]
#                                                              <-----1st input----->     <----2nd input->

# example output reranked-kbest-Lists = [ [(1,'1b'), (0.4,'1c'), (0.2,'1a')], [(5,'2a'), (2,'2b')] ]

def rerankAllKbests(weights,inputScoreLists,kbestLists):
  rerankedKbestTuples = []
  for i in range(0, len(kbestLists)):
    rerankedTuples = rerank(weights, inputScoreLists[i], kbestLists[i])
    rerankedKbestTuples.append(rerankedTuples)
  return rerankedKbestTuples

#input:  [ [(1,'a'), (0.4,'b')], [(5,'c'), (5,'d')]  ]
#output: [ ['a',     'b'],       ['c',     'd']      ]
def keep2ndEntryInTuples(oldList):
  if type(oldList) == tuple:
    return oldList[1]
  newList = []
  for entry in oldList:
    newEntry = keep2ndEntryInTuples(entry)
    newList.append(newEntry)
  return newList

# for use with accBackend functions
def getOneBestList(rerankedKbestTuples):
  oneBestList = []
  for i in range(0, len(rerankedKbestTuples)):
    if(len(rerankedKbestTuples[i]) == 0):
      oneBestList.append('ERROR')
      continue
    kbestForInputI = rerankedKbestTuples[i]
    bestTupleForInputI = kbestForInputI[0]
    oneBestList.append(bestTupleForInputI[1])
  return oneBestList

# returns -1 * acc@1 for a some weights
def minimizationObjectiveFunction(weights,kbestLists,inputScoreLists,refsList):
  # all weights must be from 0-1, otherwise give a high penalty
  totalFminWeights = 0
  negative = False
  for weight in weights:
    if weight < 0:
      negative = True
    totalFminWeights += weight
#  if negative or totalFminWeights > 1.0:
#    penalty = 10000
#    print '{0}\t{1}'.format(weights, penalty)
#    return penalty

  rerankedKbestTuples = rerankAllKbests(weights,inputScoreLists,kbestLists)
  oneBestList = getOneBestList(rerankedKbestTuples)
  (correct, incorrect, acc) = accBackend.computeAccAt1(refsList,oneBestList)
  minimizeThis = -1 * acc
  print 'correct:{0}'.format(correct)
  print 'incorrect:{0}'.format(incorrect)
  print '{0}\t{1}'.format(weights, minimizeThis)
  return minimizeThis

# run Nelder-Mead
def findBestWeights(initialWeights,kbestLists,inputScoreLists,refsList):
#  optimalParams = fmin(minimizationObjectiveFunction, initialWeights, args=(kbestLists,inputScoreLists,refsList), xtol=0.0001, ftol=0.1)
  (optimalParams, minimumFound, t, feval, iters, accept, retval) = anneal(minimizationObjectiveFunction, initialWeights, args=(kbestLists,inputScoreLists,refsList), lower=-1, upper=1, full_output=True)
  print 'optimalParams={0}\nminimumFound={1}\nfeval={2}'.format(optimalParams, minimumFound, feval)
  return optimalParams
