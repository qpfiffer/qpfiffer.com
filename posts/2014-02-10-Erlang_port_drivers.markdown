---
title: Erlang port driver pitfalls
author: Quinlan Pfiffer
bg-image: ../static/img/02_10_2014.jpg
bg-img-src: http://www.flickr.com/photos/104820964@N07/12416309453/
tags: software, code
---

Starting back in january I've been working on a homespun database called
[OlegDB](https://olegdb.org/). It's written primarily in C with an Erlang
front-end.

The reason for this was primarily that C is fast but not good at concurrency,
while Erlang is not-so-fast yet amazing at concurrency. Erlang is also a pretty
common choice for this kind of thing, see [ActorDB](http://www.actordb.com/),
[Riak](http://basho.com/riak/) or [CouchDB](http://couchdb.apache.org/). I
imagine we're not really unique with our C backend either,
[Jon](https://twitter.com/jonromero) at [BugSense](https://www.bugsense.com/)
hinted at a very interesting side project called "Lethe". We're hardly out in
the sticks here.

Anyway, onto some code. Erlang has a lot of different ways to interface with C
libraries, [NIFs](http://www.erlang.org/doc/tutorial/nif.html), [C Nodes](http://www.erlang.org/doc/tutorial/cnode.html) 
and [Port Drivers](http://www.erlang.org/doc/tutorial/c_portdriver.html) being
the primary examples. I chose to go with writing my own port driver because I
needed some implicit state (the database object) and I didn't want to [hardcode
a connection uri](http://www.erlang.org/doc/man/erl_connect.html).

Port drivers are neat in that they allow you to load up a C library, provided it
has some interface code (the port driver). If you just want to jump straight to
the OlegDB code, [go read it here.](https://github.com/infoforcefeed/Project-Oleg/blob/master/src/port_driver.c)

The way Erlang knows what it's doing is primary the `ErlDrvEntry` struct and the
`DRIVER_INIT` function, as seen here:

````
ErlDrvEntry ol_driver_entry = {
    NULL,
    oleg_start,
    oleg_stop,
    oleg_output,
    NULL,
    NULL,
    "libolegserver",
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    ERL_DRV_EXTENDED_MARKER,
    ERL_DRV_EXTENDED_MAJOR_VERSION,
    ERL_DRV_EXTENDED_MINOR_VERSION,
    0,
    NULL,
    NULL,
    NULL
};

DRIVER_INIT(libolegserver) {
    return &ol_driver_entry;
}
````

I'm not even using most of the functionality, the meat of the interface happens
in the three functions defined at the top, `oleg_start`, `oleg_stop` and
`oleg_output`. The rest can just be nulled out, for the most part.

One pretty important caveat is the "libolegserver" string, this _must_ be the
same as what you pass to `erl_ddll:load_driver`! If they aren't, obviously
Erlang won't be able to load your library.

Every function you defined (start, stop, output) all take an `ErlDrvData`
argument, which allows you to pass around some state in between calls. For me,
this happens to be the database object I want to use. The start and stop calls
are responsible for allocating and freeing any memory you might use.

Your output function is where all the magic happens, and it takes a couple of
interesting arguments. You've got your `ErlDrvData`, a random string (cmd, in my
case) and an `ErlDrvSizeT` which shows you how long your `cmd` is. Before we can
get to that, though, we need to know what kind of data Erlang is giving us.

Enter the message passing side of things. When you run `erl_ddll:load_driver`,
I'm pretty sure whats happening is that you're linking the Erlang vm up with
your .so file, which allows you to later call `open_port`.

`open_port` is a function that takes a tuple and some arguments, in my case I
use the following `init()` function:

````
init() ->
    register(complex, self()),
    Port = open_port({spawn, ?SHAREDLIB}, [binary]),
    loop(Port).
````

This, in sequence, register the atom `complex` as the `init()` function, opens a
port, and then goes into the main loop. An important thing to note here is the
`[binary]` argument to `open_port`! Without it you won't get binary data back
from your port driver. In Erlang, binary = speed.

The rest of [`ol_database.erl`](https://github.com/infoforcefeed/Project-Oleg/blob/master/src/ol_database.erl)
is pretty simple. We have some exposed functions (`ol_jar`, `ol_unjar`) that
look nice and work pretty easily, and some encoding functions. The encoding
functions are apparently the standard way of communicating to the port_driver. I
map 1 to `ol_jar`, and 2 to `ol_unjar`.

Then, later on after I've done some message passing to the open_port (love dat
message passing) we are finally ready to start digging into `oleg_output`.

````
if (fn == 1) {
    /* ol_jar */
    ...
} else if (fn == 2) {
    /* ol_unjar */
    ...
} else {
    /* Don't know what to do. */
    ...
}
````

This is where we switch on that first byte. Here you'll map to whatever C
functions you need before finally assembling some data to send back. This is the
last thing that tripped me up. Handily, "ei.h" exports some awesome helper
functions that make encoding data trivial.

````
ei_x_buff to_send;
ei_x_new_with_version(&to_send);
ei_x_encode_tuple_header(&to_send, 2);
ei_x_encode_atom(&to_send, "ok");
ei_x_encode_binary(&to_send, data, strlen((char*)data));
driver_output(d->port, to_send.buff, to_send.index);
ei_x_free(&to_send);
````

`ei_x_buff` objects are magic, dynamic chunks of binary that Erlang understands
pretty well. I believe this mostly speaks for itself, I'm sending back an object
of `{ok, <<"random binary data here">>}` that I can pattern match on,
deconstruct ot whatever else I feel like. Then I send it back to Erlang. Easy!

The last thing I feel I should mention to any prospective googlers is that no,
driver_output, driver_alloc, driver_free are not defined anywhere. You cannot
link to them via libei or whatever. I believe that when erlang does a
'load_driver', those functions are defined inside of the Erlang VM itself, which
is frankly pretty awesome. This means that whenever you allocate memory or free
memory using those functions, you're actually getting memory on the Erlang VM's
heap. Crazy, yeah?

Anyway, that pretty much covers it. OlegDB is available
[here](https://olegdb.org), and all code is available in full
[here](https://github.com/infoforcefeed/Project-Oleg). Critiques welcome, email
me at qpfiffer@gmail.com or yell at me over
[Twitter](https://twitter.com/WAallLy).
