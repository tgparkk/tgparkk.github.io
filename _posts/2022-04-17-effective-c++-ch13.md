---
layout: post
title:  "Effective c++ item13 - 자원 관리에는 객체가 그만!"
summary: "copying functions"
author: tgparkk
date: '2022-04-26 20:52:23 +0530'
category: C++
keywords: copying functions, c++
permalink: /blog/effective-cpp-item13/
usemathjax: true
---

# 항목 13: 자원 관리에는 객체가 그만!
Suppose we’re working with a library for modeling investments (e.g.,
stocks, bonds, etc.), where the various investment types inherit from a
root class Investment:  
(투자를 모델링 해주는 라이브러리를 갖고 작업을 한다고 가정합시다.
 이 라이브러리는 Investment최상위 클래스로부터 파생되어 있습니다.)  
```c++
class Investment { ... };   // root class of hierarchy of
                            // investment types
                            // (투자 타입 계통의 최상의 클래스)
```
Further suppose that the way the library provides us with specific
Investment objects is through a factory function (see Item 7):
추가로 가정하면, 이 라이브러리가 우리에게 특정한 Investment 객체를 제공하는 방법은 factory fuction 를 통한다고요.
```c++
Investment* createInvestment(); // return ptr to dynamically allocated
                                // object in the Investment hierarchy;
                                // (포인터를 반환해라 동적으로 할당된 Investment 계층에 속한 객체에)
                                
                                // the caller must delete it
                                // (parameters omitted for simplicity)
```
As the comment indicates, callers of createInvestment are responsible
for deleting the object that function returns when they are done with
it. Consider, then, a function f written to fulfill this obligation: (함수 f는 쓰여졌다. 이 의무를 이행하기 위해)  
```c++
void f()
{
    Investment *pInv = createInvestment();  // call factory function

    ...                                     // use pInv

    delete pInv;                            // release object
}
```
This looks okay, but there are several ways f could fail to delete the
investment object it gets from createInvestment.  

To make sure that the resource returned by createInvestment is always
released,  
we need to put that resource inside an object whose destructor will automatically release the resource when control leaves f.  
(우리는 자원내부에 놓아야한다. 소멸자가 자원을 자동으로 해제할수있도록 제어가 f를 떠났을때)
```c++
void f()
{
    std::auto_ptr<Investment> pInv(createInvestment()); // call factory
                                                        // function
                                                        
    ...                                                 // use pInv as
                                                        // before
}
                                                        // automatically
                                                        // delete pInv via 
                                                        // auto_ptr’s dtor
```
아주 간단한 예제이지만, 자원 관리에 객체를 사용하는 방법의 중요한 두 가지 특징을 보여준다.



