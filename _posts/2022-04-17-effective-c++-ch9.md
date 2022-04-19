---
layout: post
title:  "Effective c++ ch9 - 객체 생성 및 소멸 과정 중에는 절대로 가상 함수를 호출하지 말자"
summary: "virtual function, destruction, c++"
author: tgparkk
date: '2022-04-19 22:38:23 +0530'
category: C++
keywords: virtual function, destruction, C++ 
permalink: /blog/effective-cpp-ch9/
usemathjax: true
---

# 항목 9: 객체 생성 및 소멸 과정 중에는 절대로 가상 함수를 호출하지 말자
주식 거래를 본떠 만든 클래스 계통 구조가 있다고 가정합시다. 이를테면 매도 주문, 매수 주문 등등이 있겠죠.

```c++
class Transaction {     // base class for all
public:                 // transactions
    Transaction();
    virtual void logTransaction() const = 0; // make type-dependent
                                             // log entry
...
};


Transaction::Transaction() // implementation of
{                          // base class ctor (constructor)
    ...
    logTransaction();   // as final action, log this
}                       // transaction
class BuyTransaction: public Transaction { // derived(파생) class
public:
    virtual void logTransaction() const; // how to log trans-
                                         // actions of this type ...
                                         // 이 타입에 따른 거래내역 로깅을 구현
};
class SellTransaction: public Transaction { // derived class (파생 클래스)
public:
    virtual void logTransaction() const; // how to log trans-
                                         // actions of this type
...
}
```
Consider what happens when this code is executed
```c++
BuyTransaction b;
```