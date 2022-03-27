---
layout: post
title:  "Effective c++ ch2 - #define을 쓰려거든 const, enum, inline을 떠올리자"
summary: "const, enum, inline"
author: tgparkk
date: '2022-03-27 23:38:23 +0530'
category: C++
keywords: C++, constructor, define
permalink: /blog/effective-c++-ch2/
usemathjax: true
---

# 항목 2: #define을 쓰려거든 const, enum, inline을 떠올리자

"가급적 선행 처리자보다 컴파일러를 더 까가이 하자"

```c++
#define ASPECT_RATIO 1.653
```
우리에겐 ASPECT_RATIO 가 기호식 이름(symbolic name)으로 보이지만 컴파일러에겐 전혀 보이지 않습니다.  
소스 코드가 어떻게든 컴파일러에게 넘어가기 전에 선행 처리자가 밀어버리고 숫자 상수로 바꾸어 버리기 때문입니다.  
그 결과로, ASPECT_RATIO 라는 이름은 컴파일러가 쓰는 기호 테이블에 들어가지 않지요.  

이 문제는 기호식 디버거(symbolic debugger)에서도 나타날 소지가 있습니다.  

이 문제의 해결법은 매크로 대신 상수를 쓰는 것입니다.
```c++
const double AspectRatio = 1.653; // 대문자로만 표기하는 이름은 대개 매크로에
                                  // 쓰는 것이어서, 이름 표기도 바꿉니다.
```
AspectRatio는 언어 차원에서 지원하는 상수 타입의 데이터이기  
 때문에 당연히 컴파일러의 눈에도 보이며 기호 테이블에도 당연히 들어갑니다.  
 게다가 상수가 부동소수점 실수 타입일 경우에는 컴파일을 거친 최종 코드의  
 크기가 #define을 썼을 때보다 작게 나올 수 있습니다.  
   
매크로를 쓰면 코드에 ASPECT_RATIO가 등장하기만 하면 선행 처리자에 의해 1.653으로  
모두 바뀌면서 결국 목적 코드 안에 1.653의 사본이 등장 횟수만큼 들어가게 되지만,  
상수 타입의 AspectRatio는 아무리 여러 번 쓰이더라도 사본은 딱 한 개만 생깁니다.

# #define을 상수로 교체하려는 분께는 딱 두 가지 경우만 특별히 조심
## 첫째는 상수 포인터(constant pointer)를 정의하는 경우입니다.
상수 정의는 대개 헤더 파일에 넣는 것이 상례이므로 포인터(pointer)는 꼭 const로 선언해 주어야 하고,  
이아 아울러 포인터가 가리키는 대상까지 const로 선언하는 것이 보통입니다.  
이를테면 헤더 파일 안에 char* 기반의 문자열 상수를 정의한다면 
```c++
const char* const authorName = "Scott Meyers";
```
와 같이 const를 두 번 써야 한다는 말입니다.  
참, 문자열 상수를 쓸 때 위와 같이 char* 기반의 구닥다리 문자열보다는 string 객체가  
대체적으로 사용하기 괜찮습니다.
```c++
const std::string authorName("Scott Meyers");
```