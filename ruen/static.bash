#!/bin/bash

# split data into train/dev/test
python ruen/remove-patronymic-names.py -in ruen/guessed-patronymic-names.ru-en -out ruen/guessed-patronymic-names.ru-en.minus-middle
cat ruen/guessed-patronymic-names.ru-en.minus-middle ruen/guessed-names.ru-en > ruen/all-guessed-names.ru-en
python /usr0/home/wammar/wammar-utils/lowercase.py ruen/all-guessed-names.ru-en ruen/ruen.all
python /usr0/home/wammar/wammar-utils/split-corpus.py -r 100:1:1 -c ruen/ruen.all -t ruen/ruen.train -d ruen/ruen.dev -s ruen/ruen.test

# prepare all files before letter-alignments
python convert-bars-format-to-m2m-format.py ruen/ruen.all ruen/ruen.all.m2m
python convert-bars-format-to-m2m-format.py ruen/ruen.train ruen/ruen.train.m2m
python convert-bars-format-to-m2m-format.py ruen/ruen.dev ruen/ruen.dev.m2m
python convert-bars-format-to-m2m-format.py ruen/ruen.test ruen/ruen.test.m2m

# run alignments and split the alignments into train/test
/opt/tools/m2m-aligner-1.2/m2m-aligner \
    --alignerOut ruen/ruen-m2m.model \
    --pScore --maxFn conYX --delX --maxX 2 --maxY 3 \
    -i ruen/ruen.all.m2m \
    -o ruen/ruen.all.align
/opt/tools/m2m-aligner-1.2/m2m-aligner \
    --alignerIn ruen/ruen-m2m.model \
    --pScore --maxFn conYX --delX --maxX 2 --maxY 3 \
    -i ruen/ruen.train.m2m \
    -o ruen/ruen.train.align
/opt/tools/m2m-aligner-1.2/m2m-aligner \
    --alignerIn ruen/ruen-m2m.model \
    --pScore --maxFn conYX --delX --maxX 2 --maxY 3 \
    -i ruen/ruen.dev.m2m \
    -o ruen/ruen.dev.align
/opt/tools/m2m-aligner-1.2/m2m-aligner \
    --alignerIn ruen/ruen-m2m.model \
    --pScore --maxFn conYX --delX --maxX 2 --maxY 3 \
    -i ruen/ruen.test.m2m \
    -o ruen/ruen.test.align

# take the test portion of the alignments and create a src file for the decoder, a ref file for evaluation
python convert-alignments-to-testset.py \
    ruen/ruen.dev.align \
    ruen/ruen.dev.src \
    ruen/ruen.dev.ref
python convert-alignments-to-testset.py \
    ruen/ruen.test.align \
    ruen/ruen.test.src \
    ruen/ruen.test.ref

# take the training portion of the alignments, prepare files needed by cdec learn *.labels *.features *.train *.lattice
python convert-alignments-to-cdec-format.py \
    ruen/ruen.train.align \
    ruen/ruen.train.train \
    ruen/ruen.train.lattice \
    ruen/ruen.train.labels \
    ruen/ruen.train.features
