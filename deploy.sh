#!/bin/bash -e
.cabal-sandbox/bin/qpfiffer.com build
rsync -Pavz _site/* qpfiffer.com:/var/www/qpfiffer.com/
./parse_lifts.py
rsync -Pavz static/lifts.csv shithouse.tv:/var/www/qpfiffer.com/static/
rsync -Pavz static shithouse.tv:/var/www/qpfiffer.com/static
#rsync -Pavz static/robots.txt shithouse.tv:/var/www/qpfiffer.com/static/
git commit -p
git push

