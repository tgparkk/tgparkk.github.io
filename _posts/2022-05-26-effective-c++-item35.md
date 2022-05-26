---
layout: post
title:  "Effective c++ item35 - 가상 함수 대신 쓸 것들도 생각해 두는 자세를 시시때때로 길러 두자"
summary: " Consider alternatives to virtual functions."
author: tgparkk
date: '2022-05-26 23:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item35/
usemathjax: true
---

# 항목 35: 가상 함수 대신 쓸 것들도 생각해 두는 자세를 시시때때로 길러 두자
Because different characters may calculate their health in different ways, declaring healthValue virtual seems the obvious way to design things:  
```c++
class GameCharacter {
public:
    virtual int healthValue() const;    // return character’s health rating;
    ...                                 // derived classes may redefine this
};
```
The fact that healthValue isn’t declared pure virtual suggests that there is a default algorithm for calculating health (see Item 34).  
This is, indeed, the obvious way to design things, and in some sense, that’s its weakness.  
In the interest of helping you escape the ruts in the road of object-oriented design, let’s consider some other ways to approach this problem
## The Template Method Pattern via the Non-Virtual Interface Idiom
We’ll begin with an interesting school of thought that argues that virtual functions should almost always be private.
```c++
class GameCharacter {
public:
    int healthValue() const             // derived classes do not redefine
    {                                   // this — see Item 36
        
        ...                             // do “before” stuff — see below
        int retVal = doHealthValue();   // do the real work 
        ...                             // do “after” stuff — see below
        return retVal;
    }
    ...
private:
    virtual int doHealthValue() const   // derived classes may redefine this
    { 
        ...                             // default algorithm for calculating
    }                                   // character’s health
};
```
This basic design — having clients call private virtual functions indirectly through public non-virtual member functions — is known as the non-virtual interface (NVI) idiom. It’s a particular manifestation of the more general design pattern called Template Method (a pattern that, unfortunately, has nothing to do with C++ templates). I call the non-virtual function (e.g., healthValue) the virtual function’s wrapper.
