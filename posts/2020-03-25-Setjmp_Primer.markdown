---
title: Setjmp/Longjmp Exception Handling in C
author: Quinlan Pfiffer
tags: software, writing, c
---

With quarantine being a Real Thing in our lives now, I've been spending a lot
more time on personal projects than I have in a while. One of the things I
recently added to [Lair](https://git.sr.ht/~qpfiffer/lair) is a sort of runtime
exception. I needed these because without them, I wouldn't be able to properly
do unit testing on real code samples.

I'm always on the lookout for [fun](https://linux.die.net/man/2/writev) 
and [weird](https://linux.die.net/man/2/posix_fadvise) new syscalls, and
[setjmp(3)](https://linux.die.net/man/3/setjmp) has been in the
back of my mind for a while. Reading the [wikipedia page](https://en.wikipedia.org/wiki/Setjmp.h)
can be tremendously useful here.

The way I like to think about `setjmp` and `longjmp` is that they're like
contextualized gotos, with similarities to `fork()`. That is: you call
`setjmp()` and evaluate it's return value in a branch, just like you would with
fork, but you can actually re-enter that point from pretty much anywhere you
have access to the `jmp_buf` you defined when initially calling `setjmp()`.
Let's look at how it's used in Lair.

Lair has a very small `struct _lair_runtime` object associated with each running
program that currently only stores exception data. It's definition is
something like this:

```C
struct _lair_runtime {
	ERROR_TYPE exception_type;
	char *exception_msg;
	jmp_buf exception_buffer;
};
```

It'll probably change in the future, but for now it's sort of like a poor-man's
`perror()`: You have one exception, and it's information/message is stored in
that runtime object when it happens. The real interesting part to the runtime data is
the `jmp_buf exception_buffer;` though: That's where the contextual data for the
exception is stored. Here's how it gets setup in the `lair_execute()` function:

```C
int lair_execute(const char *program, const size_t len) {
	struct _lair_runtime *runtime = _lair_runtime_start();
	if (setjmp(runtime->exception_buffer)) {
		if (runtime->exception_msg) {
			print_error(runtime->exception_type, runtime->exception_msg);
		}
		goto error;
	}
    /* ... */
}
```

This is that conditional evaluation I was talking about before: the first time
you evaluate `setjmp()`, it'll return `0` but store it's current context into the
specified `jmp_buf`. This let's you do cool things later on, which we'll talk
about shortly. Since it returns `0` initially, we move on and execute whatever
[program](https://git.sr.ht/~qpfiffer/lair/tree/master/t/minus.den) we're trying to run.

Later on, when we encounter some [unforgiveable condition](https://github.com/munificent/vigil) like a syntax
error, parsing error, undefined function, etc. we can call this code:

```C
void throw_exception(
		struct _lair_runtime *r,
		const ERROR_TYPE err_type,
		const char *msg) {
	r->exception_type = err_type;
	r->exception_msg = strdup(msg);

	longjmp(r->exception_buffer, 1);
}
```

There is also a handy [helper function](https://git.sr.ht/~qpfiffer/lair/tree/master/src/error.c#L19-25)
for checking runtime constraints called `check()` in Lair that will wrap 
this in a simpler way, so we can do something like this (as an example):

```C
check(r, ast->indent_level > initial_indent_level, ERR_SYNTAX, "No 'True' condition to follow.");
```

Anyway, the important thing to notice here is the `longjmp()` call. `longjmp()`
takes a `jmp_buf` and a value as an argument. The `jmp_buf` is important because
it tells `longjmp()` where to go, and the value is important because it tells
`setjmp()` what to return: if you hand `longjmp()` a `1`, `setjmp()` will
return `1` waaaaay back in our initial conditional, which for review is here:

```C
	/* ... */
	if (setjmp(runtime->exception_buffer)) {
		if (runtime->exception_msg) {
			print_error(runtime->exception_type, runtime->exception_msg);
		}
		goto error;
	}
	/* ... */
```

The only caveat to this is that if you pass `longjmp()` a `0`, `setjmp()` will
behave as if it returned `1`. Basically `setjmp()` will resolve truthily
regardless of what number you pass to `longjmp()`: You just get to pick what
value of truthiness.

So now that we've called `longjmp()`, our [instruction pointer](https://en.wikipedia.org/wiki/Program_counter)
is now back at this `setjmp()` call, except it acts as though it's returning
whatever we handed to `longjmp()`, which in our case is `1`. This means we enter
the branch, check our `exception_msg`, print it out and die! Nice. This is much
better than just calling `exit(1)`, now we can run multiple unit tests as black
boxes and expect their results.

This isn't "real" exception handling yet, but is an excellent starting block.
Things to consider when moving forward are:

* Storing your current stack frame in your runtime object so you can bubble
  back up through the call stack
* Catching exceptions and handling them in your language
* Exception types
* Exception classes and catching them: eg. Should you be able to catch a runtime
  parsing error?
