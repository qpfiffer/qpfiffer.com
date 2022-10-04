---
title: Redis Predicate Matching
author: Quinlan Pfiffer
tags: software, redis
---

Okay, I just found something pretty cool and I didn't see a good tutorial
example anywhere, so maybe someone somewhere will find this useful later. Redis
has some really cool [built-in Lua](https://redis.io/commands/eval) stuff that
is useful if you want to do more with your data than just GET and SET it.

My specific problem is that we have some data in a Postgres DB, and some in a
Redis instance. There is a reason for this I won't get into, but basically the
Redis instance contains real-time information polled every 60 seconds or so, and
the user-facing component of our infrastructure needs to query this data in
certain circumstances. We have a bunch of hashmaps in Redis more or less like
the following:

```
localhost:16379> HGETALL x.12345.properties
 1) "property_a"
 2) "true"
 3) "property_b"
 4) "True"
 5) "property_c"
 6) "false"
...
```

I wanted to get all of the hashes matching the key `x.*.properties` for which
one of the properties (let's use `property_a` here) is "true". Enter Lua! I love Lua,
it's quirky and small and great. Heres how we could use it in our specific
case:

```Lua
local cursor = 0
local keys = {}
repeat
  local result = redis.call('SCAN', cursor, 'MATCH', 'x.*.properties', 'COUNT', ARGV[1])
  local keys = result[2]
  for _, key in ipairs(keys) do
    local hash_result = redis.call('HGET', key, ARGV[2])
    if hash_result == 'true' then
      table.insert(keys, key)
    end
  end
  cursor = tonumber(result[1])
  until cursor == 0
return keys
```

You could then call this script with `EVAL` like so:

```
EVAL "..." 0 1000 property_a
```

The 0 is important, so don't forget it. You can see the remaining `1000` and
`property_a` arguments are used by the script. The script itself will return all
keys in Redis matching `x.*.properties` for which `property_a` is `true`. It's
fast, non-blocking (Uses [SCAN](https://redis.io/commands/scan)) and pretty easy to grok. Neat!
