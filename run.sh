#!/bin/bash
PYTHON=python

ROOTDIR="gans"
CONFERENCE="CVPR2020 ICCV2019 CVPR2019 CVPR2018 ECCV2018"
QUERIES="q.txt"


${PYTHON} batch.py \
    --root ${ROOTDIR} \
    --conference ${CONFERENCE} \
    --queries ${QUERIES} \
    --verbose
