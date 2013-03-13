#!/bin/bash


source /usr0/tools/gcc-4.5.1/setup-env.malbec.sh

pushd /usr2/wammar/exp/translit/enhe/

echo "==========================================================="
echo "PREPARE TEST FILE"
echo "==========================================================="
python \
    ../convert-test-xml-format-to-cdec-input-format.py \
    /usr2/wammar/data/translit/raw/NEWS12_test_EnHe_1100.xml \
    /usr2/wammar/data/translit/cdec/enhe-test.src

echo "==========================================================="
echo "DECODE"
echo "==========================================================="
/usr0/tools/cdec-latest/bin/cdec \
    -c /usr2/wammar/exp/translit/enhe/train.ini \
    -w /usr2/wammar/data/translit/cdec/enhe-weights-$1.gz \
    -i /usr2/wammar/data/translit/cdec/enhe-test.src \
    -k 10 \
    > /usr2/wammar/data/translit/cdec/enhe-test.tgt


echo "=========================================================="
echo "CHECK OUTPUT LENGTH"
echo "=========================================================="
wc -l /usr2/wammar/data/translit/cdec/enhe-test.src
wc -l /usr2/wammar/data/translit/cdec/enhe-test.tgt

echo "======================================================="
echo "PUT TGT IN XML FORMAT"
echo "======================================================="
python /usr2/wammar/exp/translit/convert-cdec-kbest-output-to-xml.py \
    10 \
    English \
    Hebrew \
    cmu-nlp-lab \
    1 \
    Standard \
    model-$1 \
    /usr2/wammar/data/translit/cdec/enhe-test.src \
    /usr2/wammar/data/translit/cdec/enhe-test.tgt \
    /usr2/wammar/data/translit/cdec/enhe-test.tgt.model-$1.xml \
    no-parses.src \
    no-parses.id \
    1

popd

echo "========================================================"
echo "DONE"
echo "========================================================"
