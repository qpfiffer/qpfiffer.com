---
title: MulletCache
author: Quinlan Pfiffer
tags: software
---

# Introduction

Herein a novel idea for multi-nodal caching is proposed. The main problem solved
by this idea is thus: Home storage is cheap, cloud storage is expensive. The
project's name is MulletCache.

# What is it?

MulletCache consist of at least one remote node (the business node) and one
local node (the party node). The party node has a maximum cache size allowance,
which should be roughly the size of your on-disk availability. The business node
has no cache size, it just serves any file requested from it.

```
       Home                 Cloud
+----------------+      +------------+                         +--------------+
|                |      |            |    Request for Asset    |              |    HTTP Request
|   Party Node   |      |  Bzns Node | <---------------------+ | HTTP Service | <----------------+
|                |      |            |                         |              |
+----------------+      +------------+                         +--------------+
```

The party node will handle any incoming request for a file, check it's internal
LRU cache (and by proxy the local filesystem), and request any file it doesn't
have from the business node.

```
       Home                 Cloud
+----------------+  RX  +------------+                         +--------------+
|                <------+            |    Request for Asset    |              |    HTTP Request
|   Party Node   |      |  Bzns Node | <---------------------+ | HTTP Service | <----------------+
|                +------>            |                         |              |
+----------------+  TX  +------------+                         +--------------+
```

The Party node can be configured in either write-back or write-through
configurations, depending on speed vs. safety requirements. Heres example
pseudo-code for the party node's asset handler routine:

```
def fetch_file(requester, filename):
    if file_present_locally(filename):
        requester.send_file(file)
    else:
        new_file = await request_file_from_business_node()
        if cache_is_full():
            cache.evict_file()

        if config.write_through:
            new_file.write_to_disk()

        requester.send_file(file)

        if config.write_back and not config.write_through:
            new_file.write_to_disk()
```

# Caveats

* All communications channels between nodes must be encrypted.
* The business node must connect to the party node: The party is in the cloud,
  so the business must connect up to _it_. This keeps us from having to do any
  port shenanigans on the home router.
* The business node must be configurable to connect to multiple parties.
* Protocol between the whole mullet TBD: Probably checksum, filename and file
  contents.
* The interface to the party node must be through FUSE.
