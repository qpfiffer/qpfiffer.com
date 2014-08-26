#!/bin/bash -e
.cabal-sandbox/bin/qpfiffer.com build
rsync -Pavz _site/* qpfiffer.com:/var/www/qpfiffer.com/
#rsync -Pavz static/robots.txt shithouse.tv:/var/www/qpfiffer.com/static/
git commit -p
git push

