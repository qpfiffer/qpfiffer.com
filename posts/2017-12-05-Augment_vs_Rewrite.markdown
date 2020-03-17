---
title: Augment vs. Rewrite
author: Quinlan Pfiffer
tags: software, writing
---

I'm putting this here because I don't want to lose it.

# The Argument

I've been thinking about us doing a whole rewrite of the back end, and I'm
not sure it's the best idea. I feel that rewriting the whole thing just to
target a more GraphQL centered approach to the frontend is irresponsible, and
discards a lot of the real world things that we've learned about what this app
requires, and how people interact with it. In addition, it is [almost always a
bad idea.](https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/)

That said, I do believe there are some older/cruftier portions of the
backend that could use a good scrubbing, and I think those should be scrubbed.
What I don't think we should do is discard a medium-sized, unit and production 
tested codebase to start from scratch.

Handling support requests every day and interacting with the frontline
really puts the app into perspective. Continuing to support an existing app that
we know is going to be retired is fruitless, and takes away time from working on
the backend, even though there are really good ideas coming from the
host/support/user interactions that I either have to drop on the ground or
shoehorn into an app that isn't going anywhere.

A full rewrite, in addition to possibly suffering from [second-system syndrome](https://en.wikipedia.org/wiki/Second-system_effect) will open up the possiblity for [entirely new bugs.](http://state.shithouse.tv/)
There is a value in having a tested codebase, even partially so. 

Therefore what I think we should do instead of a full rewrite, is to augment
the backend, or at least take parts of the existing codebase and reuse them.

