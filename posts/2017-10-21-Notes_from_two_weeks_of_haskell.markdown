---
title: Notes from Two Weeks of Haskell
author: Quinlan Pfiffer
---

I've been writing Haskell at `$WORK` for about two weeks now, and it's been
pretty fun. I've also learned quite a bit. This is just a place to store some
common idioms/things I've learned, and mostly to have a place where I can put
some simple, explicit code samples.

## PostgreSQL.Simple

[PostgreSQL.Simple](https://hackage.haskell.org/package/postgresql-simple) is a great package started by Bryan O'Sullivan,
the guy that primarily wrote [Real World Haskell](http://book.realworldhaskell.org/read/). He also wrote the [Aeson](http://hackage.haskell.org/package/aeson)
library. They have similarities, and it's pretty obvious.

This section is mostly because I keep forgetting (ie. haven't practiced enough)
how to put things into queries, get things out of the database, serialize them
to records, that sort of thing.

### Updating a Record

Use `execute` for things that will modify database structures, like `UPDATE` or
`INSERT`. You'll notice that here we don't have to specify the types on `(name,
lat, lng, session_id)` because they exist in the function declaration and GHC
can infer them.

```
update_location_query = "UPDATE location AS loc \
    \SET name = ?, lat = ?, lng = ? \
    \FROM main_dropinclasssession AS sesh \
    \WHERE sesh.location_id = loc.id AND \
    \      sesh.id = ?;"

updateLocation :: T.Text -> T.Text -> Double -> Double -> ReaderT Connection IO Int64
updateLocation session_id name lat lng = do
    conn <- ask
    lift $ execute conn update_location_query (name, lat, lng, session_id)
```

## ReaderT

[ReaderT](https://hackage.haskell.org/package/transformers-0.5.5.0/docs/Control-Monad-Trans-Reader.html#t:ReaderT) is
really useful, and a great introduction (for me) on how to use a monad
transformer stack. I puzzled out a trivial example of using it with
`PostgreSQL.Simple` to pass database connections around.

These code samples are what I'm actually using. Here a `Connection` record is
embedded inside the `ReaderT` context so we can use it later on, without
explicitly passing around a `Connection` object. This doesn't have much benefit
now, but later on if we need to add extra functionality it will be trivial to
rewrite the sections of code using the `ReaderT`, rather than explicitly
redefining each and every type signature of each function that uses the
`Connection`.

```
main :: IO ()
main = do
    conn <- connectToDev
    args <- getArgs
    case parseArgs args of
        Just (session_id, address) ->
            flip runReaderT conn $ do
                 startGeocode (T.pack session_id) (T.pack address)
        ...
```

and an example of unwrapping the context of the `ReaderT`:

```
updateLocation :: T.Text -> T.Text -> Double -> Double -> ReaderT Connection IO Int64
updateLocation session_id name lat lng = do
    conn <- ask
    lift $ execute conn update_location_query (name, lat, lng, session_id)
```

Here you can see that we're getting the `Connection` out of the `ReaderT` by
`ask`ing for it. Neat! Also of note here, is that you have to `lift` the result
of the `execute` call back into the monad transformer stack. Fun fact here:
Because our transformer stack is only one level deep, you can use `lift` and
`liftIO` interchangably.
