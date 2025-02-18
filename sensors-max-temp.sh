#!/bin/sh

sensors | grep -E 'temp[0-9]|Core|Package|Sensor|Composite' | sed 's/(.*//' | grep -Eo '\+[0-9]+\.[0-9]+°C' | sort -r | head -n 1
