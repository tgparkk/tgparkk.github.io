---
layout: post
title:  "Effective c++ item27 - 캐스팅은 절약, 또 절약 잊지 말자"
summary: " Minimize casting."
author: tgparkk
date: '2022-05-15 21:45:23 +0530'
category: C++
keywords: casting, c++
permalink: /blog/effective-cpp-item27/
usemathjax: true
---

# 항목 27: 캐스팅은 절약, 또 절약 잊지 말자.
The rules of C++ are designed to guarantee that type errors are impossible.  
In theory, if your program compiles cleanly, it’s not trying to perform any unsafe or nonsensical operations on any objects.  

Unfortunately, casts subvert the type system.

■ ***const_cast*** is typically used to cast away the constness of objects. It
is the only C++-style cast that can do this.  

■ ***dynamic_cast*** is primarily used to perform “safe downcasting,” i.e.,
to determine whether an object is of a particular type in an inheritance hierarchy. It is the only cast that cannot be performed using the old-style syntax.  

It is also the only cast that may have a significant runtime cost. (I’ll provide details on this a bit later.)  

■ ***reinterpret_cast*** is intended for low-level casts that yield implementation-dependent (i.e., unportable) results, e.g., casting a pointer
to an int.  
Such casts should be rare outside low-level code. I use it only once in this book, and that’s only when discussing how you might write a debugging allocator for raw memory (see Item 50).  

■ ***static_cast*** can be used to force implicit conversions (e.g., non-const object to const object (as in Item 3), int to double, etc.). It can also be used to perform the reverse of many such conversions (e.g., void* pointers to typed pointers, pointer-to-base to pointer-to-derived),
though it cannot cast from const to non-const objects. (Only const_cast can do that.)  

The old-style casts continue to be legal, but the new forms are preferable. First, they’re much easier to identify in code (both for humans
and for tools like grep), thus simplifying the process of finding places
in the code where the type system is being subverted. Second, the
more narrowly specified purpose of each cast makes it possible for
compilers to diagnose usage errors.