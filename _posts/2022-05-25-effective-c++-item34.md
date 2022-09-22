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

상속이라는 개념은 *인터페이스 상속*, *구현 상속* 으로 나뉩니다.
두 차이는 **함수 선언**, **함수 정의** 차이와 같습니다.
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

■ ***단순 가상 함수를 선언하는 목적은 파생 클래스로 하여금 함수의 인터페이스뿐만 아니라 그 함수의 기본 구현도 물려받게 하자는 것입니다.

```c++
class Airport { ... }; // represents airports
class Airplane {
public:
    virtual void fly(const Airport& destination);
    ...
};
void Airplane::fly(const Airport& destination)
{
    // default code for flying an airplane to the given destination
}
class ModelA: public Airplane { ... };
class ModelB: public Airplane { ... }
```

비행기 A와 B가 같은 동작 방식이면 문제 없는 코드.  
하지만 새로운 동작 C비행기가 추가 된다면.. 문제가 되죠.
```c++
class Airplane {
public:
    virtual void fly(const Airport& destination) = 0;
    ...
protected:
    void defaultFly(const Airport& destination);
};
void Airplane::defaultFly(const Airport& destination)
{
    // default code for flying an airplane to the given destination
}
```
위와 같이 fly를 순수 가상함수로 변경하고, 아래처럼 defaultFly 를 호출하도록 변경
```c++
class ModelA: public Airplane {
public:
    virtual void fly(const Airport& destination)
    { defaultFly(destination); }
    ...
};
class ModelB: public Airplane {
public:
    virtual void fly(const Airport& destination)
    { defaultFly(destination); }
    ...
};
```
비행기 C 는 직적 구현하는 코드를 작성하도록 하면 되죠.
```c++
class ModelC: public Airplane {
public:
    virtual void fly(const Airport& destination);
    ...
};
void ModelC::fly(const Airport& destination)
{
    //code for flying a ModelC airplane to the given destination
}

```

A,B 비행기의 fly 부분을 좀더 명확하게 구현하면
```c++
class Airplane {
public:
    virtual void fly(const Airport& destination) = 0;
    ...
};

void Airplane::fly(const Airport& destination)  // an implementation of
{                                               // a pure virtual function
    // default code for flying an airplane to the given destination
}
class ModelA: public Airplane {
public:
    virtual void fly(const Airport& destination)
    { Airplane::fly(destination); }
    ...
};
class ModelB: public Airplane {
public:
    virtual void fly(const Airport& destination)
    { Airplane::fly(destination); }
    ...
};
class ModelC: public Airplane {
public:
    virtual void fly(const Airport& destination);
    ...
};
void ModelC::fly(const Airport& destination)
{
    // code for flying a ModelC airplane to the given destination
}
```