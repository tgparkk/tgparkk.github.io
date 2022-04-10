---
layout: post
title:  "Effective c++ ch5 - C++가 은근슬쩍 만들어 호출해 버리는 함수들에 촉각을 세우자"
summary: "copy constructor, copy assignment operator, destructor"
author: tgparkk
date: '2022-04-10 22:38:23 +0530'
category: C++
keywords: C++, copy constructor, copy assignment operator, destructor, 
permalink: /blog/effective-cpp-ch4/
usemathjax: true
---

# 항목 5: C++가 은근슬쩍 만들어 호출해 버리는 함수들에 촉각을 세우자
C++의 어떤 멤버 함수는 여러분이 클래스 안에 직접 선언해 넣지 않으면 컴파일러가 저절로 선언해 주도록 되어 있습니다.  

바로 생성자, 복사 생성자(copy constructor), 복사 대입 연산자(copy assignment operator), 그리고 소멸자(destructor) 선언해 놓습니다.  

이들은 모두 public 멤버이며 inline함수입니다. 그러니까, 여러분이 다음과 같이 썻다면
```c++
class Empty();
```
다음과 같이 쓴 것과 근복적으로 대동소이하다는 이야기입니다.
```c++
class Empty(){
public:
    Empty() {...}                               // 기본 생성자
    Empty(const Empty& rhs) {...}               // 복사 생성자
    ~Empty() {...}                              // 소멸자

    Empty& operator=(const Empty& rhs) {...}    // 복사 대입 연산자
}
```

```c++
Empty e1;       // 기본 생성자, 그리고
                // 소멸자
Empty e2(e1);   // 복사 생성자
e2 = e1;        // 복사 대입 연산자
```
기본 클래스 및 비정적 데이터 멤버의 생성자와 소멸자를 호출하는 코드가 여기서 생기는 거지요. 이때 소멸자는 이 클래스가 상속한 기본 클래스의 소멸자가 가상 소멸자로 되어 있지 않으면 역시 비가상 소멸자로 만들어진다는 점을 꼭 짚고 가야겠습니다.