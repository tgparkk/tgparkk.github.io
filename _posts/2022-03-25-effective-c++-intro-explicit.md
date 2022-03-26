---
layout: post
title:  "Effective c++ intro - explicit"
summary: "explicit"
author: tgparkk
date: '2022-03-25 21:58:23 +0530'
category: C++
thumbnail: /assets/img/posts/code.jpg
keywords: C++
permalink: /blog/effective-c++-intro-explicit/
usemathjax: true
---

## explicit 생성자

```c++
class A {
public:
    A(); // 기본 생성자 : 
};

class B {
public:
    explicit B(int x=0, bool b = true); // 기본 생성자 : 
};

class C {
public:
    explicit C(int x); // 기본 생성자가 아닙니다. // 인수 값 미정
};

```

explicit 으로 선언된 생성자는 암시적인 타입 변환을 수행하는데 쓰이지 않게 됩니다.

```c++
void doSomething(B bObject); // B 타입의 객체를 하나 받는 함수

B bObj1;                     // B 타입의 객체

doSomething(bObj1);          // B 객체를 doSomething 에 넘깁니다.

B bObj2(28);                 // int 인자 28로부터 B를 하나 만듭니다.

doSomething(28);             // 에러! doSomething 은 B를 취해야 합니다.
                             // 그냥 int 가 들어가면 안됩니다.
                             // 게다가 int에서 B로 바뀌는 암시적 변환이 없습니다.

doSomething(B(28));          // B클래스의 생성자를 써서 int에서 B로 명시적으로 변환(즉, 캐스팅)

```

프로그래머가 예상하지도 못했던 타입 변환을 막아준다.  

암시적 타입 변환에 생성자가 사용될 여지를 남겨둘 뚜렷한 이유가 없는 한  
, 생성자는 explicit 선언을 우선적으로 합니다. (적극 추천)