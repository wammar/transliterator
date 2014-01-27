#!/usr/bin/env ducttape

global {
  ducttape_experimental_submitters=enable
  ducttape_experimental_imports=enable
    
  # paths
  wammar_utils_dir="/home/wammar/wammar-utils"
  translit_dir="/home/wammar/russian-mt-blitz-2013/transliterator/ruen/"
  mono="/usr1/home/wammar/monolingual/plain-ru/news.2008.ru.shuffled"
  m2m_aligner="/opt/tools/m2m-aligner-1.2/m2m-aligner"
  cdec_dir="/home/wammar/cdec"
  all_oovs="/home/wammar/russian-mt-blitz-2013/transliterator/all_oovs.ru.txt"
  char_lm="/home/wammar/russian-mt-blitz-2013/transliterator/mono.en.char.lm"

  nprocs=10

  # autoencoder hyperparams
  #fire_precomputed_features_for_xip2=(FirePrecomputedFeaturesForXIP2: no="" yes=yes)
}

task Static
    :: translit_dir=@
    :: mono=@
    :: wammar_utils_dir=@
    :: m2m_aligner=@
    > ruen_train_train
    > ruen_test_src 
    > ruen_test_ref
    > ruen_dev_src
    > ruen_dev_ref
    > ruen_train_labels
    > ruen_train_features
{

# prepare train/dev/test data
# patronymic names need special handling
python $translit_dir/remove-patronymic-names.py -in $translit_dir/guessed-patronymic-names.ru-en -out guessed-patronymic-names.ru-en.minus-middle
# merge patronymic with normal names
cat guessed-patronymic-names.ru-en.minus-middle $translit_dir/guessed-names.ru-en > all-guessed-names.ru-en
# inflect russian names and split first/last names into separate examples
python $translit_dir/../augment-parallel-names-with-russian-inflections.py -mono $mono -pnames all-guessed-names.ru-en -apnames augmented-all-guessed-names.ru-en
# lowercase
python $wammar_utils_dir/lowercase.py -input augmented-all-guessed-names.ru-en -output ruen.all
# split into train/dev/test
python $wammar_utils_dir/vertical-split-corpus.py -r 100:1:1 -c ruen.all -t ruen.train -d ruen.dev -s ruen.test

# prepare all files before letter-alignments
python $translit_dir/../convert-bars-format-to-m2m-format.py ruen.all ruen.all.m2m
python $translit_dir/../convert-bars-format-to-m2m-format.py ruen.train ruen.train.m2m
python $translit_dir/../convert-bars-format-to-m2m-format.py ruen.dev ruen.dev.m2m
python $translit_dir/../convert-bars-format-to-m2m-format.py ruen.test ruen.test.m2m

# run alignments and split the alignments into train/test
$m2m_aligner \
    --alignerOut ruen-m2m.model \
    --pScore --maxFn conYX --delX --maxX 2 --maxY 3 \
    -i ruen.all.m2m \
    -o ruen.all.align
$m2m_aligner \
    --alignerIn ruen-m2m.model \
    --pScore --maxFn conYX --delX --maxX 2 --maxY 3 \
    -i ruen.train.m2m \
    -o ruen.train.align
$m2m_aligner \
    --alignerIn ruen-m2m.model \
    --pScore --maxFn conYX --delX --maxX 2 --maxY 3 \
    -i ruen.dev.m2m \
    -o ruen.dev.align
$m2m_aligner \
    --alignerIn ruen-m2m.model \
    --pScore --maxFn conYX --delX --maxX 2 --maxY 3 \
    -i ruen.test.m2m \
    -o ruen.test.align

# take the test portion of the alignments and create a src file for the decoder, a ref file for evaluation
python $translit_dir/../convert-alignments-to-testset.py \
    ruen.dev.align \
    $ruen_dev_src \
    $ruen_dev_ref
python $translit_dir/../convert-alignments-to-testset.py \
    ruen.test.align \
    $ruen_test_src \
    $ruen_test_ref

# take the training portion of the alignments, prepare files needed by cdec learn *.labels *.features *.train *.lattice
python $translit_dir/../convert-alignments-to-cdec-format.py \
    ruen.train.align \
    ruen.train.train \
    ruen.train.lattice \
    $ruen_train_labels \
    $ruen_train_features

# remove names of length 15+ characters from the training set (to speed up training and reduce memory usage)
python $wammar_utils_dir/prune-long-lines.py -tokens 30 -in ruen.train.train -out ruen.train.train.short
cat ruen.train.train.short | grep -v "<scan> _ <scan>" >                    ruen.train.train.short.clean
cat ruen.train.train.short.clean | grep -v "<scan> _ _" >                   ruen.train.train.short.clean.clean
cat ruen.train.train.short.clean.clean | grep -v "_ _ _" >                  ruen.train.train.short.clean.clean.clean
cat ruen.train.train.short.clean.clean.clean | grep -v "_ _ <scan>" >       ruen.train.train.short.clean.clean.clean.clean
cat ruen.train.train.short.clean.clean.clean.clean | grep -v "_ <scan> _" > ruen.train.train.short.clean.clean.clean.clean.clean
cp ruen.train.train.short.clean.clean.clean.clean.clean $ruen_train_train

}

task Dynamic
    :: translit_dir=@
    :: wammar_utils_dir=@
    :: nprocs=@
    :: all_oovs=@
    :: char_lm=@
    :: cdec_dir=@
    < ruen_train_train=$ruen_train_train@Static
    < ruen_dev_src=$ruen_dev_src@Static
    < ruen_test_src=$ruen_test_src@Static
    < ruen_train_labels=$ruen_train_labels@Static
    < ruen_train_featres=$ruen_train_features@Static
    > cdec_translit_grammar 
    > final_weights
    > ruen_dev_cdecout
    > ruen_dev_acc
{

echo "=============================================================="
echo "DID YOU REVIEW INI FILE AND CDEC PARAMETERS?"
echo "=============================================================="

echo "formalism=scfg" > train-fast.ini
echo "intersection_strategy=full" >> train-fast.ini
echo "grammar=$ruen_train_labels" >> train-fast.ini
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
    -d $ruen_train_train \
    -c train-fast.ini \
    -w $ruen_train_features \
    -T 100 -C 0.2 -I 600 -M 5

# then prune useless labels
gzip -d weights.final.gz
python $translit_dir/../filter-rules.py \
    -percent 0.1 -min_count 11 \
    -cdec_feature_weights weights.final \
    -cdec_labels $ruen_train_labels \
    -cdec_pruned_labels ruen.train.labels.pruned \
    -trashed_labels ruen.train.labels.trashed 

# then optimize the weights for the remaining rules/labels
gzip weights.final
mv weights.final.gz weights.initial.gz

echo "formalism=scfg" > train-fine.ini
echo "intersection_strategy=full" >> train-fine.ini
echo "grammar=ruen.train.labels.pruned" >> train-fine.ini
echo "scfg_max_span_limit=1" >> train-fine.ini
echo "feature_function=NgramFeatures -o 2 -U U01| -B B51| -S |" >> train-fine.ini
echo "feature_function=RuleContextFeatures -t U08|%x[-1]|%x[0]|%y[0]" >> train-fine.ini
echo "feature_function=RuleContextFeatures -t U09|%x[0]|%x[1]|%y[0]" >> train-fine.ini
echo "feature_function=RuleContextFeatures -t U11|%x[-2]|%x[-1]|%x[0]|%y[0]" >> train-fine.ini
echo "feature_function=RuleContextFeatures -t U12|%x[-1]|%x[0]|%x[1]|%y[0]" >> train-fine.ini
echo "feature_function=RuleContextFeatures -t U13|%x[0]|%x[1]|%x[2]|%y[0]" >> train-fine.ini

mpirun \
    -np $nprocs \
    $cdec_dir/training/crf/mpi_flex_optimize \
    -s 20 -i 4 \
    -d $ruen_train_train \
    -c train-fine.ini \
    -w weights.initial.gz \
    -T 25 -C 0.2 -I 100 -M 2 &> train-fine.log & 

cp weights.final.gz $final_weights

# given some russian oovs in all-oovs.ru.txt, split them into characters
python \<\<END
import io
with io.open('$all_oovs', encoding='utf8') as raw_file, io.open('all-oovs.ru.txt.split', encoding='utf8', mode='w') as split_file:
  for line in raw_file:
    chars = list(line.split()[0])
    split_file.write(' '.join(chars))
    split_file.write(u'\n')
END
# then use cdec to find the 100-best transliterations
$cdec_dir/decoder/cdec \
    -c decode-fine.ini \
    -w weights.final.gz \
    -i all-oovs.ru.txt.split \
    -k 100 \
    > all-oovs.ru.txt.100best

# then convert the labels into tokens
python $translit_dir/../create-kbest-grammar.py \
    -oov $all_oovs \
    -kbest all-oovs.ru.txt.100best \
    -clm $char_lm \
    -grammar $cdec_translit_grammar 

# decode a dev set
$cdec_dir/decoder/cdec \
    -c decode-fine.ini \
    -w weights.final.gz \
    -i $ruen_dev_src \
    > $ruen_dev_cdecout

# compute accuracy on the dev set
python $translit_dir/../acc.py \
    $ruen_dev_src \
    $ruen_dev_cdec-out \
    $ruen_dev_ref \
    $ruen_dev_acc
}

plan Full {
    reach Dynamic 
}
