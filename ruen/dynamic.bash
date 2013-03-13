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
    -T 100 -C 0.2 -I 300 -M 5

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
mpirun \
    -np 3 \
    ~/cdec/training/crf/mpi_flex_optimize \
    -s 5 -i 4 \
    -d ruen/ruen.train.train \
    -c ruen/train-fine.ini \
    -w ruen/weights.final.gz \
    -T 100 -C 0.2 -I 300 -M 5

# evaluate
#/usr2/wammar/exp/translit/enhe/evaluate.bash 0

# save logs
#mkdir -p /usr2/wammar/exp/translit/enhe/logs-0
#cp /usr2/wammar/exp/translit/logs/enhe* \
#    /usr2/wammar/exp/translit/enhe/logs-0/
