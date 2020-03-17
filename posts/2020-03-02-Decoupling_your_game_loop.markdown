---
title: Decoupling your game loop
author: Quinlan Pfiffer
tags: software, how-to
---

In an effort to write more, I'm just doing whatever I want and lowering my
barrier to entry for posting here. One of the things that I've done a couple
times recently is decoupled my `update` and `draw` loops in a couple of
different applications. One was [Voidcrash](https://github.com/qpfiffer/Voidcrash/tree/master/the_black_cartograph) which 
I've been working on sporadically for a little while, and the other is a
[personal management tool](https://github.com/qpfiffer/mgm) I'm just
calling `mgm`.

The main idea is pretty simple: You want your state-update code to run as often
as possible (especially for physics simulations) or really just as close to
real-time as possible. You also want it to be agnostic of real-world time, so it
should keep working in less-than-ideal circumstances.

For example, you have a physics simulation that you want to run at 60
frames-per-second, but your computer is multi-tasking and chugging either doing
something else (like rendering that same physics sim) or just running a
web-browser. Your update loop should do it's best to compare real-world, elapsed
time with the number of steps that should have happened in it's simulation, so
it'll either compute many frames of simulation per function call, or not do
anything because not enough time has elapsed. It's a neat idea, and avoids
problems like [games running too fast.](https://www.howtogeek.com/171945/why-do-old-game-run-way-too-fast-on-modern-computers/)

Voidcrash is in Lua (and [LÖVE2D](https://love2d.org/)!), so let's look at it first 
since it's a bit easier to parse at first glance.

```Lua
TICKER_RATE = 1/60

function MapState:update(game_state, dt)
    self.dtotal = self.dtotal + dt
    if self.dtotal >= constants.TICKER_RATE then
        -- Do updates here.
    end
end
```

The only outside context you really need to know here is that `dt` (the
argument) is the delta-time (in seconds) from the last time this function
was called, which is very useful. We then take and add that delta to the `total`
delta we have (`self.dtotal` here). We then compare the number of seconds
that have passed with our `TICKER_RATE`, which in this case is 60 frames per
second. If this is greater than the ticker rate, we do our state-update. Simple!

For a little more complex example, heres the [mgm](https://github.com/qpfiffer/mgm) one with [ncurses](https://en.wikipedia.org/wiki/Ncurses) and C:

```C
#define TICKER_RATE (1.0f/60.0f) * 1000

void update(struct app_state_t *main_state) {
	/* Initial stuff for time display and dirty flagging */
	const uint64_t now_ms = get_ms_now();
    main_state->update_dt = now_ms - main_state->last_update_time;
    main_state->update_dtotal += main_state->update_dt;

	main_state->last_update_time = now_ms;

	if (main_state->update_dtotal >= TICKER_RATE) {
		main_state->update_dtotal -= TICKER_RATE;

		/* Do more updates here */
	}
}
```

A very similar concept, and not that different from the Lua implementation,
except that we have to get our own delta-time. This is the `update()` loop, but
I also have the draw loop specified this way since ncurses doesn't like being
rendered a lot (it flickers). One caveat with the C version is that you have to
make sure you're specifying your `TICKER_RATE` as floating point math: I forgot
that integer division truncates, so my loop was running REAL fast.

Anyway I just wanted to write this up because writing is useful. Hopefully
you've learned something here. Go forth and write some loops!
