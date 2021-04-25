#!/bin/bash -e
./build.py
./parse_lifts.py
rsync -Pavz built/* 45.33.59.93:/var/www/qpfiffer.com/ &
rsync -Pavz static/lifts.csv 45.33.59.93:/var/www/qpfiffer.com/static/ &
rsync -Pavz static 45.33.59.93:/var/www/qpfiffer.com &
#rsync -Pavz static/robots.txt shithouse.tv:/var/www/qpfiffer.com/static/
#echo $1
if [[ "$1" ]]; then
    if [[ "$1" == "-p" ]]; then
        git commit -p
        git push
    fi
fi
