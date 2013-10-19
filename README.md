qpfiffer.com
============

This is the Hakyll-powered code for the qpfiffer.com blog,

Installation
------------

Requirements: cabal > 1.18.0, Hakyll

```
cabal sandbox init
cabal install -j hakyll
cd qpfiffer.com
ghc --make site.hs
./site build
```
