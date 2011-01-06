#!/bin/bash

SCRIPT=$(readlink -f $0)
BIN=`dirname $SCRIPT`
BASE=`dirname $BIN`
REQS=$BASE/requirements
DIST=$REQS/dist

pip install --no-index -f file://$DIST -r $REQS/base.txt
