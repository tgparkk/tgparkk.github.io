---
layout: post
title:  "Effective c++ item39 - "private 상속은 심사숙고해서 구사하자"
summary: "Use private inheritance judiciously."
author: tgparkk
date: '2022-06-01 12:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item39/
usemathjax: true
---

# 항목 39: private 상속은 심사숙고해서 구사하자
```c++
class Person { ... };
class Student: private Person { ... };  // inheritance is now private
void eat(const Person& p);              // anyone can eat
void study(const Student& s);           // only students study

Person p;                               // p is a Person
Student s;                              // s is a Student
eat(p);                                 // fine, p is a Person
eat(s);                                 // error! a Student isn’t a Person
```
Clearly, private inheritance doesn’t mean is-a.  

Private inheritance means is-implemented-in-terms-of.
