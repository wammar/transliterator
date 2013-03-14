#!/bin/bash

echo "=============================================================="
echo "DID YOU REVIEW INI FILE AND CDEC PARAMETERS?"
echo "=============================================================="
# quickly learn initial weights in order to prune useless labels
mpirun \
    -np 10 \
    ~/cdec/training/crf/mpi_flex_optimize \
    -s 5 -i 4 \
    -d ruen/ruen.train.train \
    -c ruen/train-fast.ini \
    -w ruen/ruen.train.features \
    -T 100 -C 0.2 -I 1000 -M 5

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
    -s 5 -i 4 \
    -d ruen/ruen.train.train \
    -c ruen/train-fine.ini \
    -w weights.initial.gz \
    -T 100 -C 0.2 -I 300 -M 5

# decode a dev set
~/cdec/decoder/cdec \
    -c ruen/train-fine.ini \
    -w weights.final.gz \
    -i ruen/ruen.dev.src \
    > ruen/ruen.dev.cdec-out

# compute accuracy on the dev set
python acc.py \
    ruen/ruen.dev.src \
    ruen/ruen.dev.cdec-out \
    ruen/ruen.dev.ref \
    ruen/ruen.dev.acc

