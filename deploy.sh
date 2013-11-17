#!/bin/bash -e
rsync -Pavz _site/* shithouse.tv:/var/www/qpfiffer.com/
#rsync -Pavz static/robots.txt shithouse.tv:/var/www/qpfiffer.com/static/
