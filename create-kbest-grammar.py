import argparse
import io
import sys
import kenlm
from math import exp, log

argParser = argparse.ArgumentParser()
argParser.add_argument("-oov", "--oov_filename", type=str, help="(input) a file which contains one OOV per line. The first token in the line is assumed to be an OOV. Other tokens on the same line are ignored.")
argParser.add_argument("-kbest", "--kbest_filename", type=str, help="(input) output of cdec -k KBEST")
argParser.add_argument("-clm", "--clm_filename", type=str, help="(input) ARPA char lm file")
argParser.add_argument("-grammar", "--grammar_filename", type=str, help="(output) an scfg cdec grammar")
argParser.add_argument("-ratio", "--avg_length_ratio", type=str, default=1.05, help="average length ratio between an english transliteration and a russian word")
args = argParser.parse_args()

# read the oovs and kbests
oovs, kbests = None, None
with io.open(args.oov_filename, encoding='utf8', mode='r') as oov_file, io.open(args.kbest_filename, encoding='utf8', mode='r') as kbest_file:
  oovs, kbests = oov_file.readlines(), kbest_file.readlines()
  for i in range(0, len(oovs)):
    oovs[i] = oovs[i].strip().split()[0]
assert(len(oovs) > 0 and len(kbests) > 0)

# load the language model
model = kenlm.LanguageModel(args.clm_filename)

# compute lm score of a sentence
def score(s):
    return sum(prob for prob, _ in model.full_scores(s))

# open the grammars file
with io.open(args.grammar_filename, encoding='utf8', mode='w') as grammar_file:
  kbest_index = 0
  rules_created = set()
  # for each oov
  for oov_index in range(0, len(oovs)):
    # skip oovs which don't have any entries in the kbest list
    if kbests[kbest_index].strip() == '':
      kbest_index += 1
      continue
    # check point
    assert(int(kbests[kbest_index].split('|||')[0].strip()) == oov_index)
    # logsum tt_nlogprob over the kbest list in order to normalize the probabilities
    temp = kbest_index
    marginal_prob = 0.0
    while kbest_index < len(kbests) and kbests[kbest_index].strip() != '' and int(kbests[kbest_index].split('|||')[0].strip()) == oov_index:
      marginal_prob += exp(-1.0 * float(kbests[kbest_index].split('|||')[3].strip()))
      kbest_index += 1
      assert(marginal_prob >= 0)
    kbest_index = temp
    # for all "compatible" kbest transliterations
    while kbest_index < len(kbests) and kbests[kbest_index].strip() != '' and int(kbests[kbest_index].split('|||')[0].strip()) == oov_index:
      labels = kbests[kbest_index].split('|||')[1].strip()
      labels = labels.split(' ')
      transliteration = []
      for label in labels:
        if label == u'_' or label == u'<scan>':
          continue
        elif len(label) == 1:
          transliteration.append(label)
        else:
          label = label.split(':')
          transliteration.extend(label)
      # now we have the transliteration
      transliteration_chars = ' '.join(transliteration)
      transliteration = ''.join(transliteration)
      # unnormalized crf -logprob
      nlogprob = float(kbests[kbest_index].split('|||')[3].strip())
      # normalized crf -logprob
      normalized_prob = exp(-1.0 * float(kbests[kbest_index].split('|||')[3].strip())) / marginal_prob
      normalized_nlogprob = -1.0 * log(normalized_prob)
      # lm_logprob
      lm_logprob = score(transliteration_chars)
      # advance the kbest_index
      kbest_index += 1
      # create a new grammar rule (if need be)
      new_rule = (oovs[oov_index], transliteration)
      if new_rule in rules_created:
        continue
      rules_created.add(new_rule)
      grammar_file.write(u'[X] ||| {0} ||| {1} ||| tt_score={2} lm_logprob={3} len_ratio_divergence={4} translit=1\n'.format(oovs[oov_index], 
                                                                                                                             transliteration, 
                                                                                                                             nlogprob, 
                                                                                                                             lm_logprob,
                                                                                                                             -1.0 * abs(1.0 * len(transliteration) / len(oovs[oov_index]) - args.avg_length_ratio)))
    # done processing all transliterations of this oov. move to the next one
  # done processing all oovs
# done writing the grammars file
