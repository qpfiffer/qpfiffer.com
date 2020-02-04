#!/bin/bash -e
./build.py
./parse_lifts.py
rsync -Pavz built/* shithouse.tv:/var/www/qpfiffer.com/ &
rsync -Pavz static/lifts.csv shithouse.tv:/var/www/qpfiffer.com/static/ &
rsync -Pavz static shithouse.tv:/var/www/qpfiffer.com &
#rsync -Pavz static/robots.txt shithouse.tv:/var/www/qpfiffer.com/static/
#echo $1
if [[ "$1" ]]; then
    if [[ "$1" == "-p" ]]; then
        git commit -p
        git push
    fi
fi
