import re
import time
import io
import gzip
import sys
import math
import argparse
from collections import defaultdict

# parse arguments
argParser = argparse.ArgumentParser()
argParser.add_argument("-percent", type=str, help="percentage of labels that needs to be pruned")
argParser.add_argument("-min_count", type=str, help="only prune labels which appear less than min_count")
argParser.add_argument("-cdec_feature_weights", type=str, help="(input) the output file of mpi_flex_optimize which contains the features used and their respective weights")
argParser.add_argument("-cdec_labels", type=str, help="(input) the labels file which is specified in cdec's .ini config file")
argParser.add_argument("-cdec_pruned_labels", type=str, help="(output) the pruned labels")
argParser.add_argument("-trashed_labels", type=str, help="(output) the trahsed labels")
argParser.add_argument("-bad_labels", type=str, help="(input) bad labels we should always exclude", default="")
args = argParser.parse_args()

PERCENTAGE = float(args.percent)
MIN_COUNT = int(args.min_count)
weightsFile = gzip.open(args.cdec_feature_weights, mode='r') if args.cdec_feature_weights.endswith('.gz') else open(args.cdec_feature_weights)
originalFile = io.open(args.cdec_labels, encoding='utf8', mode='r')
filteredFile = io.open(args.cdec_pruned_labels, encoding='utf8', mode='w')
garbageFile = io.open(args.trashed_labels, encoding='utf8', mode='w')
blackListFile = io.open(args.bad_labels, encoding='utf8', mode='r') if len(args.bad_labels) else None

# read the weighted rules
srcToWeightedRules = defaultdict(list)
weightsFile.readline()
for line in weightsFile:
  #print line
  line = line.decode('utf8')
  [rule,weight] = line.split()
  if rule[0:3] != 'F00':
    continue
  [ff,src,tgt] = rule.split('|')
  srcToWeightedRules[src].append((float(weight.strip()),tgt))
weightsFile.close()

for src in srcToWeightedRules.keys():
  tgts = []
  for tgt in srcToWeightedRules[src]:
    tgts += tgt[1]

# remove the least favorable x%
for src in srcToWeightedRules.keys():
  scarceSrc = len(srcToWeightedRules[src]) < MIN_COUNT
  srcToWeightedRules[src].sort()
  srcToWeightedRules[src].reverse()
  removeAt = int(math.ceil((1-PERCENTAGE) * len(srcToWeightedRules[src])))
  while removeAt < len(srcToWeightedRules[src]) and not scarceSrc:
    del srcToWeightedRules[src][removeAt]    
  # get rid of the weights
  for i in range(0,len(srcToWeightedRules[src])):
    srcToWeightedRules[src][i] = srcToWeightedRules[src][i][1]

# read the rules from the blacklist file (rules which should always be removed)
blackList = set()
if(blackListFile):
  for line in blackListFile:
    [x,src,tgt,f] = line.split('|||')
    blackList.add((src,tgt))
  blackListFile.close()

# read the rules from the original file and write only those which were not filtered out
for line in originalFile:
  [x,src,tgt,f] = line.split('|||')
  if tgt.strip() in srcToWeightedRules[src.strip()] and (src,tgt) not in blackList:
    filteredFile.write(line)
  else:
    garbageFile.write(line)
originalFile.close()
filteredFile.close()
garbageFile.close()
