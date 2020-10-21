#!/bin/bash
PYTHON=python

ROOTDIR="loss"
CONFERENCE="CVPR2020 ICCV2019 CVPR2019 CVPR2018 CVPR2017 ICCV2017 CVPR2016"
QUERIES="q.txt"


${PYTHON} batch.py \
    --root ${ROOTDIR} \
    --conference ${CONFERENCE} \
    --queries ${QUERIES} \
    --download-supp \
    --url-list-only \
    --verbose
