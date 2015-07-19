---
title: Simple image and audio wth FFMPEG
author: Quinlan Pfiffer
bg-image: ../static/img/07_18_2015.jpg
bg-img-src: https://www.flickr.com/photos/104820964@N07/16941897023/
---

I'm sick of forgetting how to do this too, so heres a one-liner:

```
avconv -loop 1 -i death_grips.jpg -i 666_million_ways_to_die.mp3 -shortest out.webm
```
