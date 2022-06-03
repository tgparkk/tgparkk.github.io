---
layout: post
title:  "Effective c++ item41 - "템플릿 프로그래밍의 천릿길도 암시적 인터페이스와 컴파일 타임 다형성부터"
summary: "Understand implicit interfaces and compiletime polymorphism."
author: tgparkk
date: '2022-06-03 18:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item41/
usemathjax: true
---

# 항목 41: 템플릿 프로그래밍의 천릿길도 암시적 인터페이스와 컴파일 타임 다형성부터
The world of object-oriented programming revolves around explicit interfaces and runtime polymorphism.(**객체 지향 프로그래밍의 세계는 명시적 인터페이스 및 런타임 다형성으로 돌아가요.**)
```c++
class Widget {
public:
    Widget();
    virtual ~Widget();
    virtual std::size_t size() const;
    virtual void normalize();
    void swap(Widget& other);           // see Item 25
...
};
```
and this (equally meaningless) function,
```c++
void doProcessing(Widget& w)
{
    if (w.size() > 10 && w != someNastyWidget) {
        Widget temp(w);
        temp.normalize();
        temp.swap(w);
    }
}
```
we can say this about w in doProcessing:
- Because w is declared to be of type Widget, w must support the Widget interface. We can look up this interface in the source code (e.g., the .h file for Widget) to see exactly what it looks like, so I call this an explicit interface — one explicitly visible in the source code.
- Because some of Widget’s member functions are virtual, w’s calls to those functions will exhibit runtime polymorphism: the specific function to call will be determined at runtime based on w’s dynamic type (see Item 37).  

The world of templates and generic programming is fundamentally different. In that world, explicit interfaces and runtime polymorphism continue to exist, but they’re less important. Instead, implicit interfaces and compile-time polymorphism move to the fore.
```c++
template<typename T>
void doProcessing(T& w)
{
    if (w.size() > 10 && w != someNastyWidget) {
        T temp(w);
        temp.normalize();
        temp.swap(w);
    }
}
```