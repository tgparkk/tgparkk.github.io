---
layout: post
title:  "Effective c++ item15 - 자원 관리 클래스에서 관리되는 자원은 외부에서 접근할 수 있도록 하자"
summary: "shared_ptr"
author: tgparkk
date: '2022-04-30 16:52:23 +0530'
category: C++
keywords: resource-managing classes, shared_ptr, auto_ptr, c++
permalink: /blog/effective-cpp-item15/
usemathjax: true
---

# 항목 15: 자원 관리 클래스에서 관리되는 자원은 외부에서 접근할 수 있도록 하자
항목13에서 createInvestment 등의 팩토리 함수를 호출한 결과(포인터)를 담기 위해 
스마트 포인터를 사용하는 아이디어가 있었죠.
```c++
std::tr1::shared_ptr<Investment> pInv(createInvestment()); // from Item 13

int daysHeld(const Investment *pi); // return number of days
                                    // investment has been held
                                    // 투자금이 유입된 이후로 경과한 날수

// You’d like to call it like this,
int days = daysHeld(pInv);          // error!
```
이 코드는 컴파일이 안 됩니다. daysHeld 함수는 Investment* 타입의 실제 포인터를 원하는데, 여러분은 tr1::shared_ptr<Investment> 타입의 객체를 넘기고 있잖아요.  
실제 자원(그러니까 Investment*)으로 변환할 방법이 필요해집니다.  
명시적 변환(explicit conversion), 암시적 변환(implicit conversion)  

tr1::shared_ptr, auto_ptr은 명시적 변환을 수행하는 get 이라는 멤버 함수를 제공합니다.
```c++
int days = daysHeld(pInv.get());    // fine, passes the raw pointer
                                    // in pInv to daysHeld
                                    // pInv에 들어 있는 실제 포인터를
                                    // daysHeld 에 넘겨요.
```
<img src="/assets/img/posts/item15_source.png" width="1000" height="500" title='source'>


tr1::shared_ptr, auto_ptr은 포인터 역참조 연산자(operator-> 및 operator*)도 오버로딩하고 있습니다. 암시적 변환도 가능하죠
```c++
class Investment {                  // root class for a hierarchy
public:                             // of investment types
    bool isTaxFree() const;
    ...
};

Investment* createInvestment();     // factory function
std::tr1::shared_ptr<Investment> pi1(createInvestment());     
                                    // tr1::shared_ptr
                                    // manage a resource
                                    
bool taxable1 = !(pi1->isTaxFree()); // access resource
                                     // via operator->
...
std::auto_ptr<Investment> pi2(createInvestment());  // have auto_ptr
                                                    // manage a
                                                    // resource

bool taxable2 = !((*pi2).isTaxFree());  // access resource
                                        // via operator* ..
```