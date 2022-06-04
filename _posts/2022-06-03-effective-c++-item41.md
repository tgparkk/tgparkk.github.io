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
Now what can we say about w in doProcessing?
- The interface that w must support is determined by the operations performed on w in the template.  
In this example, it appears that w’s type (T) must support the size, normalize, and swap member functions;  
copy construction (to create temp); and comparison for inequality (for comparison with someNastyWidget).  
We’ll soon see that this isn’t quite accurate, but it’s true enough for now. What’s important is that the set of expressions that must be valid in order
for the template to compile is the ***implicit interface*** that T must support.
-  The calls to functions involving w such as operator> and operator!= may involve instantiating templates to make these calls succeed.  
Such instantiation occurs during compilation.  
Because instantiating function templates with different template parameters leads to different functions being called, this is known as ***compile-time polymorphism***.
