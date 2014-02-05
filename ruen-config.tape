#!/usr/bin/env ducttape

global {

  # russian preprocessing 
  russian_patronymic_names=/russian-mt-blitz-2013/transliterator/ruen/guessed-patronymic-names.ru-en
  russian_mono="/usr1/home/wammar/monolingual/plain-ru/news.2008.ru.shuffled"

  # experiment specific configs
  ducttape_output="/usr2/home/wammar/ruen-translit/"
  transliterator_home="/usr0/home/wammar/russian-mt-blitz-2013/transliterator/"
  all_oovs="/home/wammar/russian-mt-blitz-2013/transliterator/all-oovs.ru.txt"
  char_lm="/home/wammar/russian-mt-blitz-2013/transliterator/mono.en.char.lm"
  nprocs=1
  transliteration_pairs="/home/wammar/russian-mt-blitz-2013/transliterator/ruen/guessed-names.ru-en.100"
  m2m_maxX=2
  m2m_maxY=3

  # machine specific paths
  wammar_utils_dir="/home/wammar/wammar-utils"
  m2m_aligner="/opt/tools/m2m-aligner-1.2/m2m-aligner"
  cdec_dir="/home/wammar/cdec"

}

task Preprocess 
    # replace the following two lines with custom variables you need for preprocessing
    :: russian_patronymic_names=@
    :: russian_mono=@

    # but always use these two variables:
    :: transliteration_pairs=@
    > all_translit
{
# if you don't want to do any preprocessing, you can use the following line (then you can also remove mono
cp $transliteration_pairs $all_translit

# instead, you can do all sorts of preprocessing here:
# patronymic names need special handling
#python remove-patronymic-names.py -in $russian_patronymic_names -out guessed-patronymic-names.ru-en.minus-middle
# merge patronymic with normal names
#cat guessed-patronymic-names.ru-en.minus-middle $transliteration_pairs > all-guessed-names.ru-en
# inflect russian names and split first/last names into separate examples
#python $translit_dir/../augment-parallel-names-with-russian-inflections.py -mono $mono -pnames all-guessed-names.ru-en -apnames augmented-all-guessed-names.ru-en
#cp augmented-all-guessed-names.ru-en $all_translit
}

