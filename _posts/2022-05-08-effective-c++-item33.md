---
layout: post
title:  "Effective c++ item33 - 상속된 이름을 숨기는 일은 피하자"
summary: "Avoid hiding inherited names."
author: tgparkk
date: '2022-05-20 21:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item33/
usemathjax: true
---

# 항목 33: 상속된 이름을 숨기는 일은 피하자
The matter actually has nothing to do with inheritance. It has to do with scopes. We all know that in code like this.
```c++
int x;              // global variable
void someFunc()
{
    double x;       // local variable
    std::cin >> x;  // read a new value for local x
}
```
<img src="/assets/img/posts/item33_grobal_somefunc.png" width="300" height="150" title='item33_grobal_somefunc'>

When compilers are in someFunc’s scope and they encounter the name x, they look in the local scope to see if there is something with that name.  
Because there is, they never examine any other scope.  

Enter inheritance. We know that when we’re inside a derived class member function and we refer to something in a base class (e.g., a member function, a typedef, or a data member), compilers can find what we’re referring to because derived classes inherit the things declared in base classes. The way that actually works is that the scope of a derived class is nested inside its base class’s scope. For example:  
(***상속으로 들어가보면, 파생 클래스 멤버 함수안에서 기본 클래스의 어떤 것을 참조한다면, 컴파일러는 찾을수 있어요. 우리가 참조하는게 무엇인지 파생 클래스가 기본 클래스에 선언된것들을 참조하기 때문예요.***  
***그 이유는 파생 클래스의 범위가 기본 클래스의 범위에 포함되기 때문이죠.*** )
```c++
class Base {
private:
    int x;
public:
    virtual void mf1() = 0;
    virtual void mf2();
    void mf3();
    ...
};
class Derived: public Base {
public:
    virtual void mf1();
    void mf4();
    ...
};
```

<img src="/assets/img/posts/item33_base_derived.png" width="300" height="250" title='item33_base_derived'>