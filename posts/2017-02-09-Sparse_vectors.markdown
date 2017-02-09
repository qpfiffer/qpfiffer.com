---
title: Sparsehash spelunking pt. 1: Sparse Vectors
author: Quinlan Pfiffer
bg-image: ../static/img/1_1_2014.jpg
bg-img-src: https://www.flickr.com/photos/104820964@N07/15221633500/
---

This is a multi-part series (probably) on my exploration of Google's
[SparseHash](https://code.google.com/p/sparsehash/) hash-table,
and my subsequent [re-implementation in C.](https://github.com/qpfiffer/Simple-Sparsehash)

Sparse Vectors
===========

[Sparse vectors](https://en.wikipedia.org/wiki/Sparse_array), or sparse arrays,
are cool. They're a type of array that only requires enough memory to store the
actual elements in the array. This is completely different from your standard C
arrays, which require memory even for empty cells.

As a poorly-illustrated example, if you have a sparse array with a max of five
elements and an occupancy of two elements, like this:

    _____________________
    |   | X | X |   |   |

Your in-memory representation would look like this:

    _________
    | X | X |

Ergo, we only actually require memory enough to store the two elements. This is
really, really useful for a lot of things where super-fast writes aren't
required, but being able to store a ton of items in memory is.

So why are we looking at sparse vectors, if our goal is to understand
SparseHash? Well, SparseHash is really just a bunch of sparse vectors. To
understand the hash-table, you have to understand the underlying mechanisms
first.

How does it work?
=================

I'm sure for some people, reading through the [implementation notes](https://github.com/sparsehash/sparsehash/blob/master/doc/implementation.html)
will be enough to give you a great overview of how this whole thing works,
but I need to look at the code to really be able to understand. If you want to
follow along, we'll be looking through [src/sparsehash/sparsetable](https://github.com/sparsehash/sparsehash/blob/master/src/sparsehash/sparsetable)
in the official repository. It's C++, so put your boots on.

Before we really get into the code, let's talk about some jargon related to this
whole sparse vector concept, or at least as much as I've found necessary to
understand the SparseHash implementation. With SparseHash, you have three
logical ways to denote positions, each at different UX levels.

In the overall hash-table, you have what is known as the **location**. In your
standard hash-table, you have what are called **buckets** (see the [wikipedia
article on hash-tables](https://en.wikipedia.org/wiki/Hash_table) for a better
explanation of buckets/slots). The maximum number of buckets in your hash-table
is hereby denoted __T__. Getting back to **location**, the **location** of an
object is it's position `1 .. T` in the hash-table. So far so good?

Drilling down another level, we have the concept of `groups`. Each hash-table is
divided into some [semi-arbitrary number](https://github.com/sparsehash/sparsehash/blob/master/src/sparsehash/sparsetable#L275-279)
of groups. Each group is a sparse vector. This is how each hash-table is modeled
with a bunch of sparse vectors. Inside of each group, we have **position**. This
is the __i__, typically, you use when indexing into an array. As an example (in
C):

```
    char test[16];
    test[6] = 'H'; /* 6 here could be called the position. */
```

Finally, we have **offset**. **offset** is the __actual__ offset for
our in-memory representation of the vector. Assume `F` and `V` are just
random things we're sticking in the array. For another poorly-illustrated example:

    _____________________
    |   | F |   |   | V |

The **position** of `F` here is 1, and the **position** of `V` here is 4.

    _________
    | F | V |

Their **offsets** would be 0 and 1, respectively.

### Insertion

Insertion is pretty cool. We're going to get into [bit-shifting](https://en.wikipedia.org/wiki/Bitwise_operation),
a really cool bitmap thing and some weird ways of moving memory around. So let's
just dive in, here is the [whole relevant method](https://github.com/sparsehash/sparsehash/blob/master/src/sparsehash/sparsetable#L1110):

```

reference set(size_type i, const_reference val) {
    size_type offset = pos_to_offset(bitmap, i);  // where we'll find (or insert)
    if ( bmtest(i) ) {
      // Delete the old value, which we're replacing with the new one
      group[offset].~value_type();
    } else {
      typedef base::integral_constant<bool,
          (base::has_trivial_copy<value_type>::value &&
           base::has_trivial_destructor<value_type>::value &&
           base::is_same<
               allocator_type,
               libc_allocator_with_realloc<value_type> >::value)>
          realloc_and_memmove_ok; // we pretend mv(x,y) == "x.~T(); new(x) T(y)"
      set_aux(offset, realloc_and_memmove_ok());
      ++settings.num_buckets;
      bmset(i);
    }
    // This does the actual inserting.  Since we made the array using
    // malloc, we use "placement new" to just call the constructor.
    new(&group[offset]) value_type(val);
    return group[offset];
  }

```

Can't read C++? Well, no one else can either. Let's break it down:

```
    size_type offset = pos_to_offset(bitmap, i);  // where we'll find (or
```

This is actually pretty clear. Here we're mapping the position, `i`, to our
offset. `size_type` here is probably a `uint16_t`. It's not super important,
just know that it's an [unsigned integer](https://en.wikipedia.org/wiki/Signedness)
of some sort and you'll be fine.

```
    if ( bmtest(i) ) {
      // Delete the old value, which we're replacing with the new one
      group[offset].~value_type();
```

`bmtest(i)` is important, it's how we figure out whether or not a position in
the array is occupied. It's a pretty simple function:

```
    int bmtest(size_type i) const    { return bitmap[charbit(i)] & modbit(i); }
```

...which in turn references some not-so-immediately-understandable functions,
`charbit(i)` and `modbit(i)`:

```
  static size_type charbit(size_type i)  { return i >> 3; }
  static size_type modbit(size_type i)   { return 1 << (i&7); }
```

So this is where we really start to get involved in our bitmap. The bitmap in
SparseHash is the magic sauce that makes the whole thing work, and is defined
like this:

```
    unsigned char bitmap[(GROUP_SIZE-1)/8 + 1]; // fancy math is so we round up
```

This is the bitmap. This is how we store whether or not a position in the sparse
vector is occupied. It is the central concept to the function of this entire thing.
By default, `GROUP_SIZE` is defined as `48`, just because. I guess google did
some testing to figure that number out or something. Anyway, the number is `48`
which means that our bitmap works out to be `6` characters long. The fancy
little computation there figures out how many bytes are needed to hold the
amount of bits that we want.

So, getting back to `charbit()` and `modbit()`, take note of the operations
performed. Specifically `i >> 3` and `1 << (i & 7)`. These are basically inverse
operations.

`i >> 3` removes the three lower bits, which is in fact all of the bits required
to hold the numbers `0 - 7`. So what we end up with is all of the bits in the
number `i` that don't include the ones for `0 - 7`. This helps us understand the
meaning of the next statement, `1 << (i & 7)`.

`1 << (i & 7)` gets us all the bits that are set in `i` that are less than `7`.
Shifting `1` left by that number of bits gets us the left-most `1` bit in the
number. We use these two things to figure out where in the bitmap our value will
be placed.

`charbit`, being which char in the bitmap, and then `modbit`, being which
specific bit we need when we add in the `charbit`. The C version I wrote uses
two different numbers, `5` for `charbit` and `31` for `modbit` because it
functions on 32-bit unsigned integers, vs. the Google one which uses 16-bit
integers. The idea is the same, though.
