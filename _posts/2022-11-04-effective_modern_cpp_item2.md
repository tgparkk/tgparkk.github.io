---
layout: post
title:  "2022-11-04-effective_modern_cpp_item2"
summary: ".."
author: tgparkk
date: '2022-11-04 08:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective_modern_cpp_item2/
usemathjax: true
---

# 항목 2: auto 타입 규칙을 이해해라
항목1의 템플릿 형식 연역과 항목2에서 배울 auto의 형식연역은 대부분 같아요.  
다만, auto의 형식연역은 중괄호 초기치가 std::initializer_list 를 나타내는 부분이 다릅니다.

```c++
template<typename T>
void f(ParamType param);

f(expr); // call f with some expression
```
In the call to f, compilers use expr to deduce types for T and ParamType.
(f를 호출하면서, 컴파일러는 expr을 이용해서  T와 ParamType를 연역해요 )  

When a variable is declared using auto, auto plays the role of T in the template
(auto를 이용해서 변수를 선언할 때 auto는 템플릿의 T와 동일한 역할을 해요.)  

the type specifier for the variable acts as ParamType.
(변수의 타입지정자는 ParamType 역할을 하죠.)

```c++
auto x = 27;
 
// 여기서 x의 형식 지정자는 그냥 auto
// 자체이다. 반면, 다음 선언에서
 
const auto cx = x;
 
// 형식 지정자는 const auto이다.
// 그리고 다음 선언에서는
 
const auto& rx = x;
 
// 형식 지정자가 const auto&이다.
```
