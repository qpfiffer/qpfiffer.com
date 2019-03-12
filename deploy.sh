#!/bin/bash -e
.cabal-sandbox/bin/qpfiffer.com build
./parse_lifts.py
rsync -Pavz _site/* shithouse.tv:/var/www/qpfiffer.com/ &
rsync -Pavz static/lifts.csv shithouse.tv:/var/www/qpfiffer.com/static/ &
rsync -Pavz static shithouse.tv:/var/www/qpfiffer.com/static &
#rsync -Pavz static/robots.txt shithouse.tv:/var/www/qpfiffer.com/static/
echo $1
if [[ "$1" ]]; then
    if [[ "$1" == "-p" ]]; then
        git commit -p
        git push
    fi
fi
