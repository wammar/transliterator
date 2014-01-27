#!/bin/bash

echo "=============================================================="
echo "DID YOU REVIEW INI FILE AND CDEC PARAMETERS?"
echo "=============================================================="
# quickly learn initial weights in order to prune useless labels
mpirun \
    -np 3 \
    ~/cdec/training/crf/mpi_flex_optimize \
    -s 5 -i 1 \
    -d ruen/ruen.train.train \
    -c ruen/train-fast.ini \
    -w ruen/ruen.train.features \
    -T 100 -C 0.2 -I 600 -M 5

# then prune useless labels
gzip -d weights.final.gz
python filter-rules.py \
    -percent 0.1 -min_count 11 \
    -cdec_feature_weights weights.final \
    -cdec_labels ruen/ruen.train.labels \
    -cdec_pruned_labels ruen/ruen.train.labels.pruned \
    -trashed_labels ruen/ruen.train.labels.trashed 

# then optimize the weights for the remaining rules/labels
gzip weights.final
mv weights.final.gz weights.initial.gz
mpirun \
    -np 3 \
    ~/cdec/training/crf/mpi_flex_optimize \
    -s 20 -i 4 \
    -d ruen/ruen.train.train \
    -c ruen/train-fine.ini \
    -w weights.initial.gz \
    -T 25 -C 0.2 -I 100 -M 2 &> ruen/train-fine.log & 

# given some russian oovs in all-oovs.ru.txt, split them into characters
python <<END
import io
with io.open('all-oovs.ru.txt', encoding='utf8') as raw_file, io.open('all-oovs.ru.txt.split', encoding='utf8', mode='w') as split_file:
  for line in raw_file:
    chars = list(line.split()[0])
    split_file.write(' '.join(chars))
    split_file.write(u'\n')
END
# then use cdec to find the 100-best transliterations
~/cdec/decoder/cdec \
    -c ruen/decode-fine.ini \
    -w weights.final-april-25-2013.gz \
    -i all-oovs.ru.txt.split \
    -k 100 \
    > all-oovs.ru.txt.100best
# then convert the labels into tokens
python create-kbest-grammar.py \
    -oov all-oovs.ru.txt \
    -kbest all-oovs.ru.txt.100best \
    -clm mono.en.char.lm \
    -grammar all-oovs.ru.txt.100best.grammar 

# decode a dev set
~/cdec/decoder/cdec \
    -c ruen/decode-fine.ini \
    -w weights.final.gz \
    -i ruen/ruen.dev.src \
    > ruen/ruen.dev.cdec-out

# compute accuracy on the dev set
python acc.py \
    ruen/ruen.dev.src \
    ruen/ruen.dev.cdec-out \
    ruen/ruen.dev.ref \
    ruen/ruen.dev.acc

