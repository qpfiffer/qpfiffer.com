---
title: Bcache and LVM non-destructive setup
author: Quinlan Pfiffer
bg-image: ../static/img/12_09_2013.jpg
bg-img-src: http://www.flickr.com/photos/104820964@N07/11296545115/
---

The filesystem-caching tool [bcache](http://bcache.evilpiepirate.org/) was
recently added to the linux kernel in 3.10. What it allows you to do is cache
both reads and writes on an intermediate device for great system performance. I
figured now would be a good time to play with it since I managed to pick up a 
[lot of 4GB SSDs on ebay.](http://www.ebay.com/itm/Lot-of-5-InnoDisk-FiD-4GB-2-5-SSD-SATA-100000-Serial-ATA-II-Solid-State-Drive-/321259425108?ssPageName=ADME:B:EOIBSA:US:3160)

The [few](http://evilpiepirate.org/git/linux-bcache.git/tree/Documentation/bcache.txt?h=bcache-dev#n40) 
[tutorials](https://wiki.archlinux.org/index.php/Bcache) I've found  suggest
that the drives (mechanical and cache) need to be formatted before use. This
isn't really ideal for my setup. Into [blocks.](https://github.com/g2p/blocks)

Blocks is a Python 3.3 utility to convert existing block devices and LVMs to
bcache devices. It has a [pretty good readme](https://github.com/g2p/blocks/blob/master/README.md) which
I sugges you at least skim.

### Create Cache Device

First of all you're going to need that actual caching device to be setup first.

    make-bcache -C /dev/md1

My device is `/dev/md1`, because I threw two of the SSDs I recieved into a
mirrored raid. This command also has the side effect of creating a new bcache
set. The UUID for this set is spit out as the `Set UUID:` output. Mine happens
to be `c4f68165-bf87-4d29-8e8e-3f3338deb3f9`.

### Convert Existing Device

From here it's a rather trivial matter. Supposedly. I downloaded and installed
blocks, and then ran:

    blocks to-bcache --join=c4f68165-bf87-4d29-8e8e-3f3338deb3f9 /dev/volumegroup/logical_volume

which will do some wizardry and resize and convert the device to a bcache
backing device. Or it's supposed to. [Doesn't quite work
yet.](https://github.com/g2p/blocks/issues/6).

I'll finish this post once I either get it working or get a response back from
the blocks author.

**Update:** My specific issue was fixed as of [here.](https://github.com/g2p/blocks/issues/8)
After updating blocks and making sure everything was working perfectly I ran:

    python3.3 -m blocks to-bcache --join=c4f68165-bf87-4d29-8e8e-3f3338deb3f9 /dev/vg/lvm

which successfully completed. After that I had a `/dev/bcache0` to mount. Props
to [g2p](https://github.com/g2p).
