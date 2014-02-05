#!/usr/bin/env ducttape

global {

  # experiment specific configs
  ducttape_output="/usr2/home/wammar/hien-translit/"
  all_oovs="/usr1/home/wammar/transliteration/test/hien_oovs"
  char_lm="/home/wammar/transliterator/mono.en.char.lm"
  nprocs=1
  transliteration_pairs="/usr1/home/wammar/transliteration/wordpairs/acl12-hien-train"
  m2m_maxX=2
  m2m_maxY=2

  # machine specific paths
  transliterator_home="/usr0/home/wammar/transliterator/"
  wammar_utils_dir="/home/wammar/wammar-utils"
  m2m_aligner="/opt/tools/m2m-aligner-1.2/m2m-aligner"
  cdec_dir="/home/wammar/cdec"
}

task Preprocess 
    :: transliteration_pairs=@
    > all_translit
{
cat $transliteration_pairs | awk '{ if (length($0) > 23) { print $0}  }' > $all_translit
wc -l $transliteration_pairs $all_translit
}

plan Full {
    reach Dynamic via (DelX: no) * (DelY: no)
}

