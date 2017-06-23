#!/bin/bash
# Usage:
# ./experiments/scripts/faster_rcnn_end2end.sh GPU NET DATASET [options args to {train,test}_net.py]
# DATASET is either pascal_voc or coco.
#
# Example:
# ./experiments/scripts/faster_rcnn_end2end.sh 0 VGG_CNN_M_1024 pascal_voc \
#   --set EXP_DIR foobar RNG_SEED 42 TRAIN.SCALES "[400, 500, 600, 700]"

set -x
set -e

export PYTHONUNBUFFERED="True"

DEV=$1
DEV_ID=$2
NET=$3
DATASET=$4
LOG=$5

array=( $@ )
len=${#array[@]}
EXTRA_ARGS=${array[@]:4:$len}
EXTRA_ARGS_SLUG=${EXTRA_ARGS// /_}

BASEDIR=/group/pawsey0129/cwu/rgz-faster-rcnn
PY_PATH=/group/pawsey0129/software/dlpyws/bin/python

case $DATASET in
  rgz)
    TRAIN_IMDB="rgz_2017_train"
    TEST_IMDB="rgz_2017_test"
    PT_DIR="rgz"
    ITERS=50000
    ;;
  pascal_voc)
    TRAIN_IMDB="voc_2007_trainval"
    TEST_IMDB="voc_2007_test"
    PT_DIR="pascal_voc"
    ITERS=70000
    ;;
  coco)
    # This is a very long and slow training schedule
    # You can probably use fewer iterations and reduce the
    # time to the LR drop (set in the solver to 350,000 iterations).
    TRAIN_IMDB="coco_2014_train"
    TEST_IMDB="coco_2014_minival"
    PT_DIR="coco"
    ITERS=490000
    ;;
  *)
    echo "No dataset given"
    exit
    ;;
esac

set +x
NET_FINAL=`grep -B 1 "done solving" ${LOG} | grep "Wrote snapshot" | awk '{print $4}'`
set -x

time $PY_PATH ${BASEDIR}/tools/test_net.py --device ${DEV} --device_id ${DEV_ID} \
  --weights ${NET_FINAL} \
  --imdb ${TEST_IMDB} \
  --cfg ${BASEDIR}/experiments/cfgs/faster_rcnn_end2end.yml \
  --network VGGnet_test \
  ${EXTRA_ARGS}