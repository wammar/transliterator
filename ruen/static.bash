#!/bin/bash

# prepare train/dev/test data
# patronymic names need special handling
python ruen/remove-patronymic-names.py -in ruen/guessed-patronymic-names.ru-en -out ruen/guessed-patronymic-names.ru-en.minus-middle
# merge patronymic with normal names
cat ruen/guessed-patronymic-names.ru-en.minus-middle ruen/guessed-names.ru-en > ruen/all-guessed-names.ru-en
# inflect russian names and split first/last names into separate examples
python augment-parallel-names-with-russian-inflections.py -mono /usr1/home/wammar/monolingual/plain-ru/news.2008.ru.shuffled -pnames ruen/all-guessed-names.ru-en -apnames ruen/augmented-all-guessed-names.ru-en
# lowercase
python /usr0/home/wammar/wammar-utils/lowercase.py ruen/augmented-all-guessed-names.ru-en ruen/ruen.all
# split into train/dev/test
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

# remove names of length 15+ characters from the training set (to speed up training and reduce memory usage)
python ~/wammar-utils/prune-long-lines.py -tokens 30 -in ruen/ruen.train.train -out ruen/ruen.train.train.short
cat ruen/ruen.train.train.short | grep -v "<scan> _ <scan>" >                    ruen/ruen.train.train.short.clean
cat ruen/ruen.train.train.short.clean | grep -v "<scan> _ _" >                   ruen/ruen.train.train.short.clean.clean
cat ruen/ruen.train.train.short.clean.clean | grep -v "_ _ _" >                  ruen/ruen.train.train.short.clean.clean.clean
cat ruen/ruen.train.train.short.clean.clean.clean | grep -v "_ _ <scan>" >       ruen/ruen.train.train.short.clean.clean.clean.clean
cat ruen/ruen.train.train.short.clean.clean.clean.clean | grep -v "_ <scan> _" > ruen/ruen.train.train.short.clean.clean.clean.clean.clean
cp ruen/ruen.train.train.short.clean.clean.clean.clean.clean ruen/ruen.train.train

