---
layout: post
title:  "Effective c++ item37 - 어떤 함수에 대해서도 상속받은 기본 매개변수 값은 절대로 재정의 하지 말자"
summary: "Never redefine a function’s inherited default parameter value."
author: tgparkk
date: '2022-05-29 18:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item37/
usemathjax: true
---

# 항목 37: 어떤 함수에 대해서도 상속받은 기본 매개변수 값은 절대로 재정의 하지 말자
- c++에서 상속받을 수 있는 함수는 가상함수와 비가상함수
- 그중 item36에사 비가상 함수는 재정의 하지 말라고 했죠.
- 따라서 item37 에서는 '기본 매개변수 값을 가진 가상 함수를 상속하는 경우' 에서만 보시죠  

*virtual functions* are dynamically bound, but *default parameter values* are statically bound.  

For the record, static binding is also known as early binding, and dynamic binding is also known as late binding
```c++
// a class for geometric shapes
class Shape {
public:
enum ShapeColor { Red, Green, Blue };
    // all shapes must offer a function to draw themselves
    virtual void draw(ShapeColor color = Red) const = 0;
...
};

class Rectangle: public Shape {
public:
    // notice the different default parameter value — bad!
    virtual void draw(ShapeColor color = Green) const;
    ...
};
class Circle: public Shape {
public:
    virtual void draw(ShapeColor color) const;
    ...
};
```
Now consider these pointers:
```c++
Shape *ps;                  // static type = Shape*
Shape *pc = new Circle;     // static type = Shape*
Shape *pr = new Rectangle;  // static type = Shape*
```
ps, pc, and pr are all declared to be of type pointer-to Shape, so they all have that as their static type.  
Notice that it makes absolutely no difference what they’re really pointing to — their static type is Shape* regardless.(이들이 가리키는 대상이 달라지지는 않았어요. 그냥 정적 타입이 Shpae* 이예요.)  
An object’s dynamic type is determined by the type of the object to which it currently refers.  
That is, its dynamic type indicates how it will behave.  
In the example above, pc’s dynamic type is Circle*, and pr’s dynamic type is Rectangle*. As for ps, it doesn’t really have a dynamic type, because it doesn’t refer to any object (yet).