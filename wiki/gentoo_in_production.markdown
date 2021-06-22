---
title: Notes for Gentoo in Production
---

# Steps

1. Use an external [binhost](https://wiki.gentoo.org/wiki/Binary_package_guide)
1. Use your own overlay for packaging your binaries
1. Consider a hardened kernel with SELinux
1. Look into the `FEATURES="test"` flag - any package failing it's own unit
   tests will not be installed.

# Links

* [Gentoo Server How-To](https://github.com/rkruk/gentoo-server-setup)
* [Portage sets for building Package lists](https://wiki.gentoo.org/wiki//etc/portage/sets)
* [Random comment on embedding
  stuff](https://old.reddit.com/r/linux/comments/1iw5b6/til_google_chrome_os_core_is_a_gentoo/cb8pix8/)
