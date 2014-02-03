scripts for training a transliterator using a list of transliteration pairs.  

## dependencies:
* m2m-aligner
* python v2.7 (+ modules: argparser)
* cdec decoder
* ducttape v2.1 https://github.com/jhclark/ducttape
* ken lm

## configurations:
an example configuration file is provided ``ruen-config.tape``. The following variables are mandatory:
* ``ducttape_output`` output directory
* ``transliterator_home`` root of the transliterator's repository
* ``all_oovs`` source-language words which needs to be transliterated (e.g. a test set)
* ``char_lm`` kenlm-compiled language model of target language characters. An English character language model is provided
* ``transliteration_pairs`` src-tgt transliterations, one per line, formatted as ``SOURCE LANGUAGE ||| CEURSE LAUNJE``
* ``m2m_maxX`` maximum source-language character sequence which corresponds to one character in target language
* ``m2m_maxY`` maximum target-language character sequence which corresponds to one character in source language
* ``nprocs`` number of processors to use for training
* ``wammar_utils_dir`` root of [this repository](https://github.com/wammar/wammar-utils)
* ``m2m_aligner`` path to [m2m aligner](https://code.google.com/p/m2m-aligner/)
* ``cdec_dir`` path to [cdec decoder](https://github.com/redpony/cdec)

example usage:
```ducttape translit.tape -C ruen-config.tape -p Full -y```

todos:
- filter out long transliterations in crf training to save memory consumption (linear in number of input length, quadratic in number of unique labels).

disclaimer:
- scripts are still under development and may be unstable. please do contact me if anything does not work.

if you use this software, consider citing our ACL 2012 workshop paper:
http://www.cs.cmu.edu/~wammar/pubs/translit-acl12.pdf
