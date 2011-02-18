#!/bin/bash

filename="tcm_$1_"`eval date +%Y_%m_%d`".html"

lettuce -v 5 ./features/$1 > $filename