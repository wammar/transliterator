#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import io
import argparse
from collections import defaultdict
import re

# parse/validate arguments
argParser = argparse.ArgumentParser()
argParser.add_argument("-mono", "--monolingual_filename", type=str)
argParser.add_argument("-pnames", "--parallel_names_filename", type=str)
argParser.add_argument("-apnames", "--augmented_parallel_names_filename", type=str)
args = argParser.parse_args()

# read the list of russian names in nominative (i.e. canonical) case, and the corresponding english name
sys.stderr.write('reading russian names...\n')
parallel_names = []
russian_name_set = set()
with io.open(args.parallel_names_filename, encoding='utf8', mode='r') as pnames:
  for line in pnames:
    src, tgt = line.strip().split('|||')
    src_names, tgt_names = src.strip().split(), tgt.strip().split()
    if len(src_names) != len(tgt_names):
      continue
    for src_name, tgt_name in zip(src_names, tgt_names):
      parallel_names.append( (src_name.strip(), tgt_name.strip()) )
      russian_name_set.add(src_name.strip())
sys.stderr.write('{0} unique names read\n'.format(len(russian_name_set)))
sys.stderr.write('{0} names read\n'.format(len(parallel_names)))

# create regular expressions that match inflections of a russian name
sys.stderr.write('creating regular expressions...\n')
russian_inflections = []
russian_vowels = set([u'a', u'e', u'ё', u'и', u'o', u'у', u'ы', u'э', u'ю', u'я'])
russian_case_markers = u'(а|у|ом|е|oй|ев|ым|ии|ю|я|ем|и|ы|ей|ью|ям|ам|ах|ях|ами|ями|ов)'
for russian_name, english_name in parallel_names:
  # this condition avoids creating several regular expressions for the same name when repeated in the data (e.g. a popular first name)
  if russian_name in russian_name_set:
    russian_name_set.remove(russian_name)
  else:
    continue
  # remove names that contain a dot
  if u'.' in russian_name:
    continue
  if russian_name[-1] not in russian_vowels:
    inflections = re.compile(u' {1}{2} '.format(r'\b', russian_name, russian_case_markers), re.IGNORECASE)
    russian_inflections.append( (russian_name, inflections) )
  else:
    # vowel endings may be removed before adding the suffix
    inflections = re.compile(u' {1}{2} | {3}{2} '.format(r'\b', russian_name, russian_case_markers, russian_name[:-1]), re.IGNORECASE)
    russian_inflections.append( (russian_name, inflections) )

#read corpus types
sys.stderr.write('reading russian types in mono...\n')
types = set()
with io.open(args.monolingual_filename, encoding='utf8', mode='r') as mono:
  for line in mono:
    types |= set(line.strip().split())
sys.stderr.write('{0} unique russian word read.\n'.format(len(types)))
corpus = ' '.join(types)

# find inflections of each russian name in the monolingual corpus
sys.stderr.write('matching each of {0} regexes against the corpus...\n'.format(len(russian_inflections)))
canonical_to_inflections = defaultdict(set)
names_processed = 0
for russian_name, inflections in russian_inflections:
  names_processed += 1
  if names_processed % 500 == 0:
    sys.stderr.write('{0} names processed\n'.format(names_processed))
  match = re.search(inflections, corpus)
  if match:
    inflection = match.group(0)
    if inflection not in canonical_to_inflections[russian_name]:
      #sys.stderr.write(u'{0} => {1}\n'.format(russian_name, inflection))
      canonical_to_inflections[russian_name].add(inflection.strip())

# now, write the original parallel names as well as the inflections found
russian_names_processed = set()
with io.open(args.augmented_parallel_names_filename, encoding='utf8', mode='w') as apnames:
  for (src_name, tgt_name) in parallel_names:
    if src_name in russian_names_processed:
      continue
    else:
      russian_names_processed.add(src_name)
    apnames.write(u'{0} ||| {1}\n'.format(src_name, tgt_name))
    for inflection in canonical_to_inflections[src_name]:
      apnames.write(u'{0} ||| {1}\n'.format(inflection, tgt_name))

