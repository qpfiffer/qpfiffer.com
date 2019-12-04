---
title: Python 2 Threading Primitives: Locks and Events
author: Quinlan Pfiffer
bg-image: /static/img/bg-gradient.png
bg-img-src: https://google.com/
---

Recently I've had to deal with some inter-process communication in Python 2.7, in
which I had several threads sharing data. I figured doing a brain-dump of some
of this data would be useful for me in the future as well as anyone else
wandering by.

In this specific instance, I'm retrieving frames from a camera of some sort,
pulling them in over a websocket, then passing them on to an OpenCV processor.
Nothing crazy, but the websocket server couldn't be blocked by the OpenCV
processor, so threads were introduced. Really just two.

The primary things we care about here are [thread events](https://docs.python.org/2/library/threading.html#event-objects) and [thread
locks.](https://docs.python.org/2/library/thread.html#thread.allocate_lock). I wrote this when I was dealing with Python 2, but I don't see why
you couldn't do this stuff in 3+. In general, use `asyncio` in favor of threads
and locks and processes and whatever. Easier to think about.

Heres something similar to what I ended up writing:

```python
import thread, threading

class Server:
    def __init__(self, lock, event):
        self.lock = lock
        self.event = event

    # Assume this server is doing a bunch of server-y things, and this
    # method is the callback triggered when new data comes in:
    def msg_received(self, client, server, msg):
        with self.frame_lock:
            self.frame = msg
            self.event.set()

    def get_frame(self):
        return self.frame

class Processor:
    def __init__(self, lock, event):
        self.lock = lock
        self.event = event

    def process(self, server):
        while self.event.wait():
            with self.lock:
                frame = server.get_frame()
                self.event.clear()

                # Do fancy processing here
                ...

def main():
    frame_lock = thread.allocate_lock()
    frame_event = threading.Event()

    # Server receives frames from upstream:
    server = Server(frame_lock, frame_event, ip='localhost', port=8999)

    # Processor does fancy computation on frames:
    processor = Processor(frame_lock, frame_event)
    t = Threading.Thread(target=processor.process, args=(server,))
    t.start()

    server.run_forever()

if __name__ == '__main__':
    main()
```

This is more or less what I have. I haven't tested the above code, but the point
is you have a Server of some sort operating independently of a processor of
some other sort. Later on I might write another post detailing how you might do this
with a [UNIX pipe](http://man7.org/linux/man-pages/man2/pipe.2.html) instead of
this Locking/Event style, but we can talk about that when the time comes. Or
doesn't. Whatever.

The fancy (but still basic) thing here is the event, and the lock. You can use
the event to avoid spinlocking (eg. `while not frame: ...`), and instead only
wake up your expensive processing Thread when it has something to do. Remember,
`sleep()` is a sign that you're being lazy!

One thread will call `event.set()` when it is done operating on the shared
resource, then back off. The next thread will then wake up and wait to acquire
the lock, so it can operate on the shared resource, doing it's thing, and then
calling `event.clear()`. This ends up working really nicely because each thread
only works when it can, no one is stepping on anyone elses toes and it all just
works out.
