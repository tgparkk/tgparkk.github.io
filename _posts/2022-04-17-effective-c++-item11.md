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

예를 들어 동적 할당된 비트맵을 가리키는 원시 포인터를 데이터 멤버로 갖는 클래스를 보시죠.
```c++
class Bitmap { ... };

class Widget {
    ...
private:
    Bitmap *pb; // ptr to a heap-allocated object
};              // 힙에 할당한 객체를 가리키는 포인터
```
Here’s an implementation of operator= that looks reasonable on the
surface but is unsafe in the presence of assignment to self.
```c++
Widget&
Widget::operator=(const Widget& rhs)    // unsafe impl. of operator=
{                                       // 안전하지 않게 구현된 operator=

    delete pb;                          // stop using current bitmap
    pb = new Bitmap(*rhs.pb);           // start using a copy of rhs’s bitmap
    return *this;                       // see Item 10

                                        // this 는 함수가 호출된 객체를 
                                        // 가리키는 포인터 이다.
}
```

# ***this 는 함수가 호출된 객체를 가리키는 포인터 이다.***


The self-assignment problem here is that inside operator=, *this (the
target of the assignment) and rhs could be the same object.  
이 둘이 같은 객체이면, delete 연산자가 *this 객체의 비트맵에만 적용되는 것이 아나라 rhs의 객체까지 적용됩니다.  

The traditional way to prevent this error is to check for assignment to
self via an identity test at the top of operator=
```c++
Widget& Widget::operator=(const Widget& rhs)
{
    if (this == &rhs) return *this; // identity test: if a self-assignment,
                                    // do nothing
    delete pb;
    pb = new Bitmap(*rhs.pb);
    return *this;
}
```
This works, but I mentioned above that the previous version of operator= wasn’t just self-assignment-unsafe, it was also exception-unsafe,
and this version continues to have exception trouble.  
In particular, if
the “new Bitmap” expression yields an exception (either because there
is insufficient memory for the allocation or because Bitmap’s copy constructor throws one), the Widget will end up holding a pointer to a
deleted Bitmap.

```c++
Widget& Widget::operator=(const Widget& rhs)
{
    Bitmap *pOrig = pb;         // remember original pb
    pb = new Bitmap(*rhs.pb);   // point pb to a copy of rhs’s bitmap
    delete pOrig;               // delete the original pb
    return *this;
}
```
예외 안전성과 자기대입 안전성을 동시에 가진 operator=을 구현하는 방법으로, 방금 본 예처럼 문장의 실행 순서를 수작업으로 조정하는 것 외에 다른 방법을 하나 더 알려드리겠습니다.
technique known as “copy and swap.”
```c++
class Widget {
    ...
    void swap(Widget& rhs); // exchange *this’s and rhs’s data; ... 
                            // see Item 29 for details
};
Widget& Widget::operator=(const Widget& rhs)
{
    Widget temp(rhs);   // make a copy of rhs’s data
    swap(temp);         // swap *this’s data with the copy’s
    return *this;
}
```