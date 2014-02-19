#!/usr/bin/env ducttape

global {
  ducttape_experimental_submitters=enable
  ducttape_experimental_imports=enable

  m2m_delX=(DelX: yes="--delX" no="")
  m2m_delY=(DelY: yes="--delY" no="")
  m2m_maxX=(MaxX: two="2" three="3" one="1")
  m2m_maxY=(MaxY: two="2" three="3" one="1") 
}

task BuildTargetCharLM
    :: wammar_utils_dir=@
    :: kenlm_dir=@
    :: tgt_mono_text=@
    > tgt_mono_charlm
{
  python $wammar_utils_dir/print-letters-of-unique-words.py $tgt_mono_text tgt_mono_char
  $kenlm_dir/bin/lmplz -o 3 --text tgt_mono_char  --arpa $tgt_mono_charlm --interpolate_unigrams --memory=10%
}

task Static
    :: wammar_utils_dir=@
    :: transliterator_home=@
    :: m2m_aligner=@
    :: m2m_maxX=@
    :: m2m_maxY=@
    :: m2m_delX=@
    :: m2m_delY=@
    #:: max_parallel_length=@
    < all_translit=$all_translit@Preprocess
    > train_train
    > test_src 
    > test_ref
    > dev_src
    > dev_ref
    > train_labels
    > train_features
{
# lowercase
python $wammar_utils_dir/lowercase.py -input $all_translit -output all
# split into train/dev/test
python $wammar_utils_dir/vertical-split-corpus.py -r 100:1:1 -c all -t train -d dev -s test

# prepare all files before letter-alignments
python $transliterator_home/convert-bars-format-to-m2m-format.py all all.m2m
python $transliterator_home/convert-bars-format-to-m2m-format.py train train.m2m
python $transliterator_home/convert-bars-format-to-m2m-format.py dev dev.m2m
python $transliterator_home/convert-bars-format-to-m2m-format.py test test.m2m

# run alignments and split the alignments into train/test
$m2m_aligner \
    --alignerOut m2m.model \
    --pScore --maxFn conYX $m2m_delX $m2m_delY --maxX $m2m_maxX --maxY $m2m_maxY \
    -i all.m2m \
    -o all.align
$m2m_aligner \
    --alignerIn m2m.model \
    --pScore --maxFn conYX $m2m_delX $m2m_delY --maxX $m2m_maxX --maxY $m2m_maxY \
    -i train.m2m \
    -o train.align
$m2m_aligner \
    --alignerIn m2m.model \
    --pScore --maxFn conYX $m2m_delX $m2m_delY --maxX $m2m_maxX --maxY $m2m_maxY \
    -i dev.m2m \
    -o dev.align
$m2m_aligner \
    --alignerIn m2m.model \
    --pScore --maxFn conYX $m2m_delX $m2m_delY --maxX $m2m_maxX --maxY $m2m_maxY \
    -i test.m2m \
    -o test.align

# take the test portion of the alignments and create a src file for the decoder, a ref file for evaluation
python $transliterator_home/convert-alignments-to-testset.py \
    dev.align \
    $dev_src \
    $dev_ref
python $transliterator_home/convert-alignments-to-testset.py \
    test.align \
    $test_src \
    $test_ref

# take the training portion of the alignments, prepare files needed by cdec learn *.labels *.features *.train *.lattice
python $transliterator_home/convert-alignments-to-cdec-format.py \
    train.align \
    train.train \
    train.lattice \
    $train_labels \
    $train_features

# remove names of length 15+ characters from the training set (to speed up training and reduce memory usage)
python $wammar_utils_dir/prune-long-lines.py -tokens 50 -in train.train -out short
cat short | grep -v "<scan> _ <scan>" >                    clean1
cat clean1 | grep -v "<scan> _ _" >                   clean2
cat clean2 | grep -v "_ _ _" >                  clean3
cat clean3 | grep -v "_ _ <scan>" >       clean4
cat clean4 | grep -v "_ <scan> _" > $train_train

}

task Dynamic
    :: wammar_utils_dir=@
    :: transliterator_home=@
    :: nprocs=@
    :: all_oovs=@
    :: cdec_dir=@
    < char_lm=$tgt_mono_charlm@BuildTargetCharLM
    < train_train=$train_train@Static
    < dev_src=$dev_src@Static
    < dev_ref=$dev_ref@Static
    < test_src=$test_src@Static
    < train_labels=$train_labels@Static
    < train_features=$train_features@Static
    > cdec_translit_grammar 
    > final_weights
    > dev_cdecout
    > dev_acc
{

echo "=============================================================="
echo "DID YOU REVIEW INI FILE AND CDEC PARAMETERS?"
echo "=============================================================="

echo "formalism=scfg" > train-fast.ini
echo "intersection_strategy=full" >> train-fast.ini
echo "grammar=$train_labels" >> train-fast.ini
echo "scfg_max_span_limit=1" >> train-fast.ini
echo "#feature_function=NgramFeatures -o 2 -U U01| -B B51| -S |" >> train-fast.ini
echo "feature_function=RuleContextFeatures -t U08|%x[-1]|%x[0]|%y[0]" >> train-fast.ini
echo "feature_function=RuleContextFeatures -t U09|%x[0]|%x[1]|%y[0]" >> train-fast.ini
echo "feature_function=RuleContextFeatures -t U11|%x[-2]|%x[-1]|%x[0]|%y[0]" >> train-fast.ini
echo "feature_function=RuleContextFeatures -t U12|%x[-1]|%x[0]|%x[1]|%y[0]" >> train-fast.ini
echo "feature_function=RuleContextFeatures -t U13|%x[0]|%x[1]|%x[2]|%y[0]" >> train-fast.ini

# quickly learn initial weights in order to prune useless labels
mpirun \
    -np $nprocs \
    $cdec_dir/training/crf/mpi_flex_optimize \
    -s 5 -i 1 \
    -d $train_train \
    -c train-fast.ini \
    -w $train_features \
    -T 100 -C 0.2 -I 600 -M 5

# then prune useless labels
gzip -d weights.final.gz
python $transliterator_home/filter-rules.py \
    -percent 0.1 -min_count 11 \
    -cdec_feature_weights weights.final \
    -cdec_labels $train_labels \
    -cdec_pruned_labels train.labels.pruned \
    -trashed_labels train.labels.trashed 

# then optimize the weights for the remaining rules/labels
gzip weights.final
mv weights.final.gz weights.initial.gz

echo "formalism=scfg" > train-fine.ini
echo "formalism=scfg" > decode-fine.ini
echo "intersection_strategy=full" >> train-fine.ini
echo "grammar=train.labels.pruned" >> train-fine.ini
echo "grammar=train.labels.pruned" >> decode-fine.ini
echo "scfg_max_span_limit=1" >> train-fine.ini
echo "scfg_max_span_limit=1" >> decode-fine.ini
echo "feature_function=NgramFeatures -o 2 -U U01| -B B51| -S |" >> train-fine.ini
echo "feature_function=NgramFeatures -o 2 -U U01| -B B51| -S |" >> decode-fine.ini
echo "feature_function=RuleContextFeatures -t U08|%x[-1]|%x[0]|%y[0]" >> train-fine.ini
echo "feature_function=RuleContextFeatures -t U08|%x[-1]|%x[0]|%y[0]" >> decode-fine.ini
echo "feature_function=RuleContextFeatures -t U09|%x[0]|%x[1]|%y[0]" >> train-fine.ini
echo "feature_function=RuleContextFeatures -t U09|%x[0]|%x[1]|%y[0]" >> decode-fine.ini
echo "feature_function=RuleContextFeatures -t U11|%x[-2]|%x[-1]|%x[0]|%y[0]" >> train-fine.ini
echo "feature_function=RuleContextFeatures -t U11|%x[-2]|%x[-1]|%x[0]|%y[0]" >> decode-fine.ini
echo "feature_function=RuleContextFeatures -t U12|%x[-1]|%x[0]|%x[1]|%y[0]" >> train-fine.ini
echo "feature_function=RuleContextFeatures -t U12|%x[-1]|%x[0]|%x[1]|%y[0]" >> decode-fine.ini
echo "feature_function=RuleContextFeatures -t U13|%x[0]|%x[1]|%x[2]|%y[0]" >> train-fine.ini
echo "feature_function=RuleContextFeatures -t U13|%x[0]|%x[1]|%x[2]|%y[0]" >> decode-fine.ini

mpirun \
    -np $nprocs \
    $cdec_dir/training/crf/mpi_flex_optimize \
    -s 20 -i 4 \
    -d $train_train \
    -c train-fine.ini \
    -w weights.initial.gz \
    -T 25 -C 0.2 -I 100 -M 2 &> train-fine.log 

ls -lha

cp weights.final.gz $final_weights

# given some russian oovs in all-oovs.ru.txt, split them into characters
python $transliterator_home/word-to-char.py $all_oovs all-oovs.ru.txt.split

# then use cdec to find the 100-best transliterations
$cdec_dir/decoder/cdec \
    -c decode-fine.ini \
    -w weights.final.gz \
    -i all-oovs.ru.txt.split \
    -k 100 \
    > all-oovs.ru.txt.100best \
    2> all-oovs.ru.txt.100best.stderr

# then convert the labels into tokens
python $transliterator_home/create-kbest-grammar.py \
    -oov $all_oovs \
    -kbest all-oovs.ru.txt.100best \
    -clm $char_lm \
    -grammar $cdec_translit_grammar 

# decode a dev set
$cdec_dir/decoder/cdec \
    -c decode-fine.ini \
    -w weights.final.gz \
    -i $dev_src \
    &> $dev_cdecout
   

# compute accuracy on the dev set
python $transliterator_home/acc.py \
    $dev_src \
    $dev_cdecout \
    $dev_ref \
    $dev_acc
}
