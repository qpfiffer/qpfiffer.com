---
title: The Great Server Migration
author: Quinlan Pfiffer
tags: software, gentoo
---

It's time. My old Digital Ocean server, used for everything, was getting old,
crufty and scary.

```
142 packages can be updated.
109 updates are security updates.

$ cat /etc/os-release
NAME="Ubuntu"
VERSION="16.04.7 LTS (Xenial Xerus)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 16.04.7 LTS"
VERSION_ID="16.04"
HOME_URL="http://www.ubuntu.com/"
SUPPORT_URL="http://help.ubuntu.com/"
BUG_REPORT_URL="http://bugs.launchpad.net/ubuntu/"
VERSION_CODENAME=xenial
UBUNTU_CODENAME=xenial
```

Not great. Thats really old. Theres a TON of stuff on there though, but it's
time. So I spun up a Gentoo box on Linode and got to work. Heres more or less a
list of services that live (or will soon live) on the new box:

## Services

As much as possible, the ones that require daemons or servers will be
gentoo-ified. I'll explain that in a later page. Some have [already been
done.](https://git.sr.ht/~qpfiffer/overlay/tree/master/item/www-misc/wheypi)

Websites:
* [IFF Link Aggregator](https://infoforcefeed.shithouse.tv/)
* [PDX Burrito Review](https://burrito.shithouse.tv/)
* [shithouse.tv](https://shithouse.tv/) - includes all the [secret](https://things-we-feel-rather-strongly-about.shithouse.tv/) bumps, too
* [q.pfiffer.org](https://q.pfiffer.org/)
* [OlegDB Homepage](https://olegdb.org/)
* [WheyPI](https://wheypi.shithouse.tv/)
* [groading.com](https://groading.com/)
* TODO [logproj](https://logproj.shithouse.tv/) - The weird, DIY logging project.

Some older #IFF goodies:
* [infoforcefeed.org](http://infoforcefeed.org/)
* [Software Development for Arsonists](http://arson.infoforcefeed.org/)

Bots:
* TODO [scooper-bot](https://github.com/infoforcefeed/scooper-bot)
    * Also needs webhooks for automatic deploys.

Historicals:
* TODO [kyoto.io](https://kyoto.shithouse.tv/) - My defunct startup idea
* TODO [meta.infoforcefeed.org](https://meta.shithouse.tv/) - The old metaforcefeed
  calendar/idea tracker

Misc.
* IRC - autologins, IdleRPG setup
