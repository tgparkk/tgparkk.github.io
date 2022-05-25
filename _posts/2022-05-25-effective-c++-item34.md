---
layout: post
title:  "Effective c++ item34 - 인터페이스 상속과 구현 상속의 차이를 제대로 파악하고 구별하자"
summary: "Differentiate between inheritance of interface and inheritance of implementation."
author: tgparkk
date: '2022-05-25 19:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item34/
usemathjax: true
---

# 항목 34:  인터페이스 상속과 구현 상속의 차이를 제대로 파악하고 구별하자
The difference between these two kinds of inheritance *corresponds* exactly to the difference between function declarations and function definitions discussed in the Introduction to this book.
```c++
class Shape {
public:
    virtual void draw() const = 0;              // pure virtual function
    virtual void error(const std::string& msg);
    int objectID() const;
    ...
};
class Rectangle: public Shape { ... };
class Ellipse: public Shape { ... };
```
Three functions are declared in the Shape class. The first, draw, draws the current object on an implicit display.  
The second, error, is called when an error needs to be reported.  
The third, objectID, returns a unique integer identifier for the current object.  
Each function is declared in a different way: draw is a pure virtual function; error is a simple (impure?) virtual function; and objectID is a non-virtual function.  

■ ***The purpose of declaring a pure virtual function is to have derived classes inherit a function interface only.***