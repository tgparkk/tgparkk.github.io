---
layout: post
title:  "Effective c++ item11 - operator= 에서는 자기대입에 대한 처리가 빠지지 않도록 하자"
summary: "self assignment operator= , c++"
author: tgparkk
date: '2022-04-20 22:38:23 +0530'
category: C++
keywords: this, self assignment operators= , c++
permalink: /blog/effective-cpp-item11/
usemathjax: true
---

# 항목 11: operator= 에서는 자기대입에 대한 처리가 빠지지 않도록 하자
자기대입(assignment to self)이란, 어떤 객체가 자기 자신에 대해 대입 연산자를 적용하는 것을 말합니다.
```c++
class Widget { ... };
Widget w;
...
w = w;                  // assignment to self
```
이 코드는 적법한(legal)한 코드입니다.

```c++
a[i] = a[j]; // potential assignment to self
is an assignment to self if i and j have the same value, and 

*px = *py; // potential assignment to self
```

```c++
class Base { ... };

class Derived: public Base { ... };

void doSomething(const Base& rb, // rb and *pd might actually be
                   Derived* pd); // the same object
```
항목 13 및 14에 나온 조언을 따른다면 여러분은 자원 관리 용도로 항상 객체를 만들어야 할 것이고, 바로 이때 조심해야 하는 것이 대입 연산자입니다.  

어쩌다 보면 자원을 사용하기 전에 덜컥 해제해 버릴 수도 있을지 모릅니다.