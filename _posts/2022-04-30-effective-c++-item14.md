---
layout: post
title:  "Effective c++ item14 - 자원 관리 클래스의 복사 동작에 대해 진지하게 고찰하자"
summary: "copying behavior in resource-managing classes."
author: tgparkk
date: '2022-04-30 15:52:23 +0530'
category: C++
keywords: resource-managing classes, shared_ptr, auto_ptr, c++
permalink: /blog/effective-cpp-item14/
usemathjax: true
---

# 항목 14: 자원 관리 클래스의 복사 동작에 대해 진지하게 고찰하자
Item 13 introduces the idea of Resource Acquisition Is Initialization
(RAII) as the backbone of resource-managing classes,  
(항목13 은 (자원획득 즉 초기화(RAII))의 아이디어를 자원관리 클래스의 주축으로 소개합니다.)
and it describes
how auto_ptr and tr1::shared_ptr are manifestations of this idea for
heap-based resources  
(auto_ptr and tr1::shared_ptr 이 힙기반자원에 대해 표현한 방법에 대해서도 설명합니다.)

사실, 힙에 생기지 않는 자원은 auto_ptr, tr1::shared_ptr 등의 스마트 포인터로 처리해 주기엔 맞지 않다는 것이 일반적인 견해이죠. 항상 그런 것은 아니지만, 자원 관리 클래스를 여러분 스스로 만들어야 할 필요를 느끼는 경우가 바로 이런 경우입니다.  

For example, suppose you’re using a C API to manipulate mutex
objects of type Mutex offering functions lock and unlock:
```c++
void lock(Mutex *pm);   // lock mutex pointed to by pm
void unlock(Mutex *pm); // unlock the mutex
```
To make sure that you never forget to unlock a Mutex you’ve locked,
you’d like to create a class to manage locks. The basic structure of
such a class is dictated by the RAII principle that resources are
acquired during construction and released during destruction:  
(Mutex 가 잠근것을 잊지않고 푸는 확실한 방법은 락을  관리하는 클래스를 만드는 것,  그러한 클래스 RAII 원리 : 자원을 생성중에 얻고 소멸중에 해제하는 것은~~~
)

```c++
class Lock {
public:
explicit Lock(Mutex *pm)
: mutexPtr(pm)
{ 
    lock(mutexPtr); }               // acquire resource
    ~Lock() { unlock(mutexPtr); }   // release resource
private:
    Mutex *mutexPtr;
};
```
### 사용자는 Lock을 사용할 때 RAII 방식에 맞추어 쓰면 됩니다.
```c++
Mutex m; // define the mutex you need to use
...
{                   // create block to define critical section

    Lock ml(&m);    // lock the mutex

    ...             // perform critical section operations

}                   // automatically unlock mutex at end
                    // of block
```
This is fine, but what should happen if a Lock object is copied?
```c++
Lock ml1(&m);   // lock m
Lock ml2(ml1);  // copy ml1 to ml2 — what should
                // happen here?
```
what should happen when an RAII object is copied?  
Most of the time, you’ll want to choose one of the following possibilities:  

**Frist, Prohibit copying.**
In many cases, it makes no sense to allow RAII objects to be copied.  
This is likely to be true for a class like Lock,
because it rarely makes sense to have “copies” of synchronization
primitives (동기화 객체에 대한 사본은 의미가 없어요.)  

복사를 막는 방법은 항목6을 참고하시면 되는데요. 골자만 말씀드리면 복사 연산(함수)을 private 멤버로 만드는 것입니다.
```c++
class Lock: private Uncopyable {    // prohibit copying — see
public:                             // Item 6

    ...                             // as before
};
```
**Second, Reference-count the underlying resource.**
자신의 RAII 클래스에 참조 카운팅 방식의 복사 동작, tr1::shared_ptr을 데이터 멤버로 넣으면 즉, Mutex* 에서 tr1::shared_ptr<Mutex> 로 바꾸라는 것입니다
tr1::shared_ptr은 참조 카운트가 0이 될 때 자신이 가리키고 있던 대상을 삭제해 버리도록 기본 동작이 만들어져 있어서, 우리의 바람과는 다소 어긋납니다.  
Mutex를 다 썼을 때 이것에 대해 잠금 해제만 하면 되지, 삭제까지 하고 싶진 않거든요.  

참으로 다행스러운 것은 tr1::shared_ptr이 '삭제자(deleter)' 지정을 허용한다는 사실입니다. 여기서 삭제자란, tr1::shared_ptr이 유지하는 참조 카운트가 0이 되었을 때 호출되는 함수 혹은 함수 객체를 일컫습니다.  
삭제자는 tr1::shared_ptr 생성자의 두 번째 매개변수로 선택적으로 넣어 줄 수 있습니다.

```c++
class Lock {
public:
explicit Lock(Mutex *pm)    // init shared_ptr with the Mutex
    : mutexPtr(pm, unlock)  // to point to and the unlock func
{                           // as the deleter
    lock(mutexPtr.get());   // see Item 15 for info on “get” 
}
private:
    std::tr1::shared_ptr<Mutex> mutexPtr;   // use shared_ptr
};                                          // instead of raw pointer
```
이 예제에서 Lock 클래스는 소멸자를 선언하지 않았습니다. 필요없어서요. 항목 5에 따르면 클래스의 소멸자(컴파일러가 만들었든 사용자가 정의했든)는 비정적 데이터 멤버의 소멸자를 자동으로 호출하게 되어 있습니다.  
이 '비정적 데이터 멤버'에 해당하는 것이 mutexPtr입니다.

**Third, Copy the underlying resource(관리하고 있는 자원을 진짜로 복사합니다.).**

**Fourth, Transfer ownership of the underlying resource.**
auto_ptr의 '복사' 동작이 예시죠.
