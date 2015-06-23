---
title: Sparsehash spelunking pt. 1: Sparse Vectors
author: Quinlan Pfiffer
bg-image: ../static/img/1_1_2014.jpg
bg-img-src: https://www.flickr.com/photos/104820964@N07/15221633500/
---

This is a multi-part series (probably) on my exploration of Google's
[SparseHash](https://code.google.com/p/sparsehash/) hashtable,
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
understand the hashtable, you have to understand the underlying mechanisms
first.

How does it work?
=================

I'm sure for some people, reading through the [implementation notes](https://google-sparsehash.googlecode.com/svn/trunk/doc/implementation.html)
will be enough to give you a great overview of how this whole thing works,
but I need to look at the code to really be able to understand. If you want to
follow along, we'll be looking through [src/sparsehash/sparsetable](https://code.google.com/p/sparsehash/source/browse/trunk/src/sparsehash/sparsetable)
in the official repository. It's C++, so put your boots on.

Before we really get into the code, let's talk about some jargon related to this
whole sparse vector concept, or at least as much as I've found necessary to
understand the SparseHash implementation. With SparseHash, you have three
logical ways to denote positions, each at different UX levels.

In the overall hash-table, you have what is known as the **location**. In your
standard hasht-able, you have what are called **buckets** (see the [wikipedia
article on hashtables](https://en.wikipedia.org/wiki/Hash_table) for a better
explanation of buckets/slots). The maximum number of buckets in your hash-table
is hereby denoted __T__. Getting back to **location**, the **location** of an
object is it's position `1 .. T` in the hash-table. So far so good?

Drilling down another level, we have the concept of `groups`. Each hash-table is
divided into some [semi-arbitrary number](https://code.google.com/p/sparsehash/source/browse/trunk/src/sparsehash/sparsetable#275)
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

The **position** of __F__ here is 1, and the **position** of __V__ here is 4.

    _________
    | F | V |

Their **offsets** would be 0 and 1, respectively.

### Insertion

Insertion is pretty cool. We're going to get into [bit-shifting](https://en.wikipedia.org/wiki/Bitwise_operation),
a really cool bitmap thing and some weird ways of moving memory around. So let's
just dive in, here is the [whole relevant method](https://code.google.com/p/sparsehash/source/browse/trunk/src/sparsehash/sparsetable#1110):

```

reference set(size_type i, const_reference val) {
    size_type offset = pos_to_offset(bitmap, i);  // where we'll find (or
insert)
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
          realloc_and_memmove_ok; // we pretend mv(x,y) == "x.~T(); new(x)
T(y)"
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

    size_type offset = pos_to_offset(bitmap, i);  // where we'll find (or

This is actually pretty clear. Here we're mapping the position (__i__) to our
offset. `size_type` here is probably a `uint16_t`. It's not super important,
just know that it's an integer of some sort and you'll be fine.

### Deletion

### Search/Find
