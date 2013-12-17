---
title: Sane dnsmasq setup
author: Quinlan Pfiffer
bg-image: ../static/img/12_16_2013.jpg
bg-img-src: http://www.flickr.com/photos/104820964@N07/10920448963/
---

[Dnsmasq](http://www.thekelleys.org.uk/dnsmasq/doc.html) is a slick little piece
of software that acts as both a DHCP and DNS server. However, it's annoying to
setup if you don't know what you're going for.

My common use case is that I have an internal network behind dnsmasq and an
external network of computers all using the same domain. Ideally, what I'd like
to happen is that I can ping a computer and have it attempt to resolve first
locally and then as a subdomain on the external network.

This isn't as hard to do as it seems, and you can actually get it working under
windows as well.

1. First of all you need to setup your domain. I'll be using `shithouse.tv`
   because thats what I actually use. You're going to need to subdivide your
   physical locations into domains, I use `shithouse.tv`.
1. Assign your domain to the network you want to use it.
    domain=apartment.shithouse.tv
1. If you're using dnsmasq for DHCP, you'll want to set that up too
    dhcp-range=10.1.10.100,10.1.10.200,255.255.255.0,12h
   This will give 12 hour leases to people between 10.1.10.100-200.
1. If your dnsmasq server is not your router, you'll want to tell computers
   getting your leases from you that you aren't:
    dhcp-option=3,10.1.10.1
   10.1.10.1 is my gateway.
1. Set expand-hosts (this sets the 'search' option in `/etc/hosts`):
    expand-hosts
1. Set some external DNS, unless you have your own (I use google's):
    server=8.8.8.8
    server=8.8.4.4
1. Tell everyone this server is the best:
    dhcp-authoritative
1. Set domain-needed so that leasers know where they are:
    domain-needed

For the full configuration file:

````
domain-needed
domain=shithouse.com
server=8.8.8.8
server=8.8.4.4
expand-hosts
dhcp-range=10.1.10.100,10.1.10.200,255.255.255.0,12h
dhcp-option=3,10.1.10.1 # Set the default gateway to the actual router, not us
dhcp-authoritative
cache-size=0

````

Dropping this into `/etc/dnsmasq.conf` will allow me to ping external servers,
and to resolve local computers. I can ping test.shithouse.tv,
test.apartment.shithouse.tv and test and the all resolve to the same place.

I mostly figured this out while messing around, so optimizations welcome.
