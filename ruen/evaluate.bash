#!/bin/bash

echo "==========================================================="
echo "DECODE"
echo "==========================================================="

source /usr0/tools/gcc-4.5.1/setup-env.malbec.sh

pushd /usr2/wammar/exp/translit/enhe/

/usr0/tools/cdec-latest/bin/cdec \
    -c /usr2/wammar/exp/translit/enhe/train.ini \
    -w /usr2/wammar/data/translit/cdec/enhe-weights-$1.gz \
    -i /usr2/wammar/data/translit/cdec/enhe-dev2.src \
    > /usr2/wammar/data/translit/cdec/enhe-dev2.tgt

#    -r 10 \

popd

echo "=========================================================="
echo "CHECK OUTPUT LENGTH"
echo "=========================================================="
wc -l /usr2/wammar/data/translit/cdec/enhe-dev2.src
wc -l /usr2/wammar/data/translit/cdec/enhe-dev2.ref
wc -l /usr2/wammar/data/translit/cdec/enhe-dev2.tgt

echo "======================================================="
echo "COMPUTE 1-BEST ACCURACY"
echo "======================================================="
python /usr2/wammar/exp/translit/acc.py \
    /usr2/wammar/data/translit/cdec/enhe-dev2.src \
    /usr2/wammar/data/translit/cdec/enhe-dev2.tgt \
    /usr2/wammar/data/translit/cdec/enhe-dev2.ref \
    /usr2/wammar/data/translit/cdec/enhe-dev2-$1.acc

echo "========================================================"
echo "DONE"
echo "========================================================"
