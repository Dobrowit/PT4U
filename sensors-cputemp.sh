#!/bin/bash

echo $(LC_NUMERIC=C printf "%.${2:-0}f" $(sensors -A -j coretemp-isa-0000 | jq '.[]."Package id 0".temp1_input'))
