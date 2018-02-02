This is a list of things I hate about javascript, just so I have something to
say when people ask why.

* async/await breaks the use of the debugger. You can not step into function if
  you are using async/await.
* The javascript debugger is often completely unable to introspect outer scope
  when inside a closure.
* You can't evaluate promises in the Chrome debugger while it's paused
* The chrome debugger steals window focus every time a breakpoint is hit, which
  doesn't make any sense when you're not debugging a webapp
* The best way to figure out where your code is *throwing an exception* is to
  put a debugger statement at the top of the routine you suspect and just step
  over functions until your app explodes
* Bookshelf.js doesn't tell you that a field is null (like for instance, a
  foreign key) it just warns that `undefined bindings have been detected`
* The chrome debugger steals focus, autofucuses the source display window and
  let's you type into it, for some reason. This is annoying if, for instance,
  you're doing LITERALLY ANYTHING ELSE and chrome decides its MY TURN
* The node debugger doesn't have step up/step down, only step into/step out.
  This is terrible for trying to learn context of a function being executed.
* Bookshelf Model.count() returns a string representation of a number

Today:

* Bookshelf is failing to fetch() a related record on a model, even though it is
  clearly in the database with the correct ID. Whats going on? I have no idea,
  no error is thrown. It just returns nothing. I can't step into the function
  because I am awaiting it, so it just steps into the runtime's active hooks thing.
* Even with long stack traces enabled, stack traces are completely useless.
  Problem: Some SQL query somewhere is throwing and error. Problem: I have no
  idea where. The solution SHOULD be I just look at the stacktrace and see where
  the call originates, but javascript is nondeterministic or something and
  completely useless.
