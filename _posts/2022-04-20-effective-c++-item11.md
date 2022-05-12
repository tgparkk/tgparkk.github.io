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
If you follow the advice of Items 13 and 14, you’ll always use objects to
manage resources,  
and you’ll make sure that the resource-managing objects behave well when copied.  
When that’s the case, your assignment operators will probably be self-assignment-safe without your having to think about it.  

자원관래 겍체를 사용하지 않는 경우도 있으니 아래 예시를 보죠.

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

## ***this 는 함수가 호출된 객체를 가리키는 포인터 이다.***
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

In particular, if the “new Bitmap” expression yields an exception (either because there is insufficient memory for the allocation or because Bitmap’s copy constructor throws one),  

the Widget will end up holding a pointer to a deleted Bitmap.

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
A variation on this theme takes advantage of the facts that   
(1) a class’s copy assignment operator may be declared to take its argument by value and  
(2) passing something by value makes a copy of it (see Item 20):
```c++
Widget& Widget::operator=(Widget rhs)   // rhs is a copy of the object
{                                       // passed in — note pass by val
    swap(rhs);                          // swap *this’s data with
                                        // the copy’s
    return *this;
}
```
Personally, I worry that this approach sacrifices clarity at the altar of
cleverness,  
but by moving the copying operation from the body of the function to construction of the parameter,
it’s a fact that compilers can sometimes generate more efficient code(이유 모르겠음)