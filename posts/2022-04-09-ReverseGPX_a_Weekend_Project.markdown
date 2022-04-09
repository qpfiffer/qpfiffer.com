---
title: ReverseGPX, A Weekend Project
author: Quinlan Pfiffer
bg-img-src: https://google.com/
tags: programming, gentoo, c, software
---

For a while now, I've noticed that theres no good tool online to flip [GPX
files](https://en.wikipedia.org/wiki/GPS_Exchange_Format)
around. [gpx.studio](https://gpx.studio/) exists but it's big and clunky and
graphical, and does a lot more than what I want. There are also a handful of
weird java tools and random code in GitHub repos, but nothing simple and
concise. This need actually comes up a lot for me: Say I need to reverse a
bikepacking route, or create a route from a track that was done the wrong way,
or who knows. Theres not a simple, easy, fast way to do it.

So now that I'm unemployed and wandering the earth like a Wraith, I finally got
around to building [ReverseGPX.com](https://reversegpx.com/). The concept is
simple: You upload a file, wait for a second while it does it's thing, and you
get back the same file but the timestamps and trackpoint order is reversed. It's
simple and bespoke and _fast_. Theres no fucking around with a javascript
map or sliders or anything, it just does what it says. I figured I'd talk a
little bit about how it's built and dpeloyed, since it's done with my own
particular brand of brain-damage.

## The Code

I hacked it together in a rainy weekend at a hostel here in Pucón, Chile. The
frontend is written in Python3 using the [Sanic](https://sanic.dev/en/) framework 
because I'm familiar with it. It's mostly uninteresting. It serves up some HTML
and ingests files, making sure they're mostly benign. Theres some ugly vanilla
Javascript and inline CSS because I don't [need any frontend dependencies.](https://qp-nodeps.shithouse.tv/)

## The File Daemon

The interesting part is the bespoke C file-processing daemon, that reads more
like a script. You can [check it out for yourself here.](https://git.sr.ht/~qpfiffer/reversegpx/tree/master/item/reversed/main.c)
It's almost one file, but I needed to add in my vector library to handle
arbitrary lists. This one _does_ use dependencies, because I didn't want to mess
around with parsing XML. LibXML2 does that job, and was fun to try and figure
out. It's not a bad library, and more than enough for what I'm doing.

The daemon itself reverses two things: The node order, and the timestamps in
those nodes. So far I haven't found a GPX file that messes it up, but I'm sure
they exist. I haven't even bothered to really check it for memory leaks, since
it's short-lived and just called by inotify. It uses the filesystem for processing.

## Deployment

For now it's using the classic bombproof running-in-tmux deployment method,
which I've found to be one of the best ways to just get something going.
Eventually I'll get around to sticking it into my [private Overlay](/posts/2020-04-23-Personal_Gentoo_Overlay.html),
but for now it's just quietly chugging along in the backround and it's very easy
to keep an eye on it, so I'm not too worried.

If you do find a bug in it, please [email me here](mailto:qpfiffer@gmail.com).
I'm very interested in finding things that break it, since it's a very simple
and basic utility.
