---
layout: post
title:  "Effective c++ item36 - 상속받은 비가상 함수를 파생 클래스에서 재정의하는 것은 절대 금물!"
summary: "Never redefine an inherited non-virtual function."
author: tgparkk
date: '2022-05-28 23:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item36/
usemathjax: true
---

# 항목 36: 상속받은 비가상 함수를 파생 클래스에서 재정의하는 것은 절대 금물!
```c++
class B {
public:
    void mf();
    ...
};
class D: public B { ... };
```
```c++
// Even without knowing anything about B, D, or mf, given an object x of type D,
D x;        // x is an object of type D
// you would probably be quite surprised if this,
B *pB = &x; // get pointer to x
pB->mf();   // call mf through pointer
// behaved differently from this:
D *pD = &x; // get pointer to x
pD->mf();   // call mf through pointer
```
Right, it should. But it might not.  
In particular, it won’t if mf is non virtual and D has defined its own version of mf:
```c++
class D: public B {
public:
    void mf();  // hides B::mf; see Item 33
    ...
};
pB->mf();       // calls B::mf
pD->mf();       // calls D::mf
```