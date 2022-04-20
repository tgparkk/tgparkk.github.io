---
layout: post
title:  "Effective c++ item10 - 대입 연산자는 *this의 참조자를 반환하게 하자"
summary: "*this, assignment operators , c++"
author: tgparkk
date: '2022-04-20 21:38:23 +0530'
category: C++
keywords: this, assignment operators , c++
permalink: /blog/effective-cpp-item10/
usemathjax: true
---

# 항목 10: 대입 연산자는 *this의 참조자를 반환하게 하자
```c++
int x, y, z;
x = y = z = 15; // chain of assignments
```
대입 연산은 우측 연관(right-associative) 연산

```c++
class Widget {
public:
    ...
    Widget& operator=(const Widget& rhs) // return type is a reference to
    {                                    // the current class
        ...
        return *this;                    // return the left-hand object
    }                                    // 좌변 객체(의 참조자)를 반환합니다.
    ...
};
```
모든 형태의 대입 연산자에서 지켜져야 합니다.
```c++
class Widget {
public:
    ...
    Widget& operator+=(const Widget& rhs) // the convention applies to
    {                                     // +=, -=, *=, etc.
        ...                               // 규약이 적용됩니다.
        return *this;
    }
    Widget& operator=(int rhs)  // it applies even if the
    {                           // operator’s parameter type
                                // is unconventional
        return *this;
    }
    ...
};
```