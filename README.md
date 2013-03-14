python+bash scripts for training a transliterator using a list of transliteration pairs.  

dependencies:
- m2m-aligner
- python 2.7 (+ modules: argparser)
- cdec decoder

disclaimer:
- scripts are still under development and are not stable.

features:
- reranking
- many-to-many character alignments
- multiple reference support

for details about how it works, refer to (Ammar et al. 2012) http://www.cs.cmu.edu/~wammar/pubs/translit-acl12.pdf

todos:
- filter out long transliterations in crf training cuz it cuz memory consumption (which is too critical to mess with) is linear in number of observations. 
- write a ductape for training/tuning and another for decoding

