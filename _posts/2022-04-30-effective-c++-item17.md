---
layout: post
title:  "Effective c++ item17 - new로 생성한 객체를 스마트 포인터에 저장하는 코드는 별도의 한 문장으로 만들자"
summary: "Store newed objects in smart pointers in standalone statements."
author: tgparkk
date: '2022-04-30 23:52:23 +0530'
category: C++
keywords: resource-managing classes, smart pointers, c++
permalink: /blog/effective-cpp-item17/
usemathjax: true
---

# 항목 17: new로 생성한 객체를 스마트 포인터에 저장하는 코드는 별도의 한 문장으로 만들자
처리 우선순위를 알려 주는 함수가 하나 있고, 동적으로 할당한 Widget 객체에 대해 어떤 우선순위에 따라 처리를 적용하는 함수가 하나 있다고 가정합시다.  
```c++
int priority();
void processWidget(std::tr1::shared_ptr<Widget> pw, int priority);
```
자원 관리에는 객체를 사용하는 것이 좋다는 겨례의 가르침을 코드에 되살려, process Widget 함수는 동적 할당된 Widget 객체에 대해 스마트포인터를 사용하도록 만들어졌습니다.  
```c++
processWidget(new Widget, priority()); // 컴파일이 안됩니다.
```
tr1::shared_ptr 의 생성자는 explicit로 선언되어 있기 때문에, 'new Widget' 표현식에 의해 만들어진 포인터가 tr1::shared_ptr 타입의 객체로 바꾸는 암시적인 변환이 있을 리가 없기 때문입니다.
```c++
processWidget(std::tr1::shared_ptr<Widget>(new Widget), priority()); // Ok
```
다만 위 식은 컴파일러에 따라  
■ Call priority.  
■ Execute “new Widget”.  
■ Call the tr1::shared_ptr constructor.  
순서가 다릅니다.  
경우에 따라 중간에 예외가 발생하면 포인터가 유실될 수 있습니다.
```c++
std::tr1::shared_ptr<Widget> pw(new Widget);    // store newed object
                                                // in a smart pointer in a
                                                // standalone statement

processWidget(pw, priority());                  // this call won’t leak
                                                // 이제는 자원 누출 걱정이 없습니다.
```

 Store newed objects in smart pointers in standalone statements.