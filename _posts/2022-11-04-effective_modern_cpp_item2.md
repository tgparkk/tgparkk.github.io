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

위의 식에서 x, cx, rx 의 형식들은 연역(deduce)할 때, 컴파일러는 마치 선언마다 템플릿 함수 하나와 해당 초기화 표현식으로 그 템플릿 함수를 호출하는 구문이 존재하는 것처럼 행동해요.
```c++
template <typename T>               // x의 형식을 연역하기 위한
void func_for_x(T param);           // 개념적인 템플릿
 
func_for_x(27);                     // 개념적인 호출: param에 대해
                                    // 연역된 형식이 바로 x의 형식이다.
 
template <typename T>               // cx의 형식을 연역하기 위한
void func_for_cx(const T param);    // 개념적인 템플릿
 
func_for_cx(x);                     // 개념적인 호출: param에 대해
                                    // 연역된 형식이 곧 cx의 형식이다.
 
template <typename T>                // rx의 형식을 연역하기 위한
void func_for_rx(const T& param);    // 개념적인 템플릿
 
func_for_rx(x);                      // 개념적인 호출: param에 대해
                                     // 연역된 형식이 바로 rx의 형식이다.
```
(항목1 에서는 템플릿 형식 연역을 일반적인 함수 템플릿의 param의 형식 지정자인 ParamType의 특성에 따라 세 가지 경우로 얘기했었죠.)  

- 경우 1: 형식 지정자가 포인터나 참조 형식이지만 보편 참조(universal reference)는 아닌 경우.
- 경우 2: 형식 지정자가 보편 참조인 경우.
- 경우 3: 형식 지정자가 포인터도 아니고 참조도 아닌 경우.

---
type&& 이슈의 핵심은 때로는 rvalue reference를 의미하나, 때로는 rvalue 또는 lvalue reference로 해석된다는 것이다.
분명히 구문상 생긴 것은 rvalue reference인 것 같은데, 실제 의미는 lvalue reference일 수 있다는 것이다.
이렇게 특이한 유연성을 가지는 reference를 가리켜, universal reference라고 한다.
(http://egloos.zum.com/sweeper/v/3149089)
---
---

```c++
// 경우 1과 3의 예는 앞에서 봤죠. 
auto x = 27;               // 경우 3(x는 포인터도 아니고 참조도 아님)
 
const auto cx = x;         // 경우 3(cx 역시 둘 다 아님)
 
const auto& rx = x;        // 경우 1(rx는 보편 참조(universal reference)가 아닌 참조)
```

```c++
// 경우 2도 기대한 대로 작동한다
auto&& uref1 = x;        // x는 int이자 좌측값이므로
                         // uref1의 타입은 int&
 
auto&& uref2 = cx;       // cx는 const int이자 좌측값이므로
                         // uref2의 타입은 const int&
 
auto&& uref3 = 27;       // 27은 int이자 우측값이므로
                         // uref3의 타입은 int&&
```

```c++
// 마지막으로, 항목 1에서는 비참조 타입
// 지정자의 경우 배열과 함수 이름이
// 포인터로 붕괴(decay)하는 방식을 논의했다.
 
// auto 타입 추론에 대해서도 그러한
// 붕괴(decay)가 일어난다.
const char name[] =          // name의 타입은 const char [13]
    "R. N. Briggs";
 
auto arr1 = name;            // arr1의 타입은 const char*
 
auto& arr2 = name;           // arr2의 타입은 const char (&)[13]
 
 
void someFunc(int, double);  // someFunc는 함수;
                             // 그 타입은 void(int, double)
 
auto func1 = someFunc;       // func1의 타입은
                             // void (*)(int, double)
 
auto& func2 = someFunc;      // func2의 타입은
                             // void (&)(int, double)
```

### 이제 다른 점을 보죠.
```c++
// 우선, 27을 초기 값으로 해서
// int 변수를 선언하는 예를 살펴보자.
 
// C++98에서는 다음 두 가지 구문이
// 가능했다.
 
int x1 = 27;
int x2(27);
 
// 균일 초기화(uniform initialization)를
// 지원하는 C++11에서는 위의 두 구문과
// 더불어 다음과 같은 구문들을 사용할
// 수도 있다.
 
int x3 = { 27 };
int x4{ 27 };

// 위 4개를 auto를 사용하면
auto x1 = 27;
auto x2(27);
auto x3 = { 27 };
auto x4{ 27 };
// 처음 두 선언문은 실제로 타입이
// int이고 값이 27인 변수를 선언한다.
 
// 그러나 나머지 둘은 값이 27인 원소 하나를 담은
// std::initializer_list<int> 타입의 변수를 선언한다!

------------------------------------------------------
// auto로 선언된 변수의 초기치(initializer)가
// 중괄호 쌍으로 감싸인 형태이면, 추론된
// 타입은 std::initializer_list이다.
 
// 만일 그런 타입을 추론할 수 없으면
// (이를테면 중괄호 초기치의 값들의
// 타입이 서로 달라서) 컴파일이 거부된다.
 
auto x5 = { 1, 2, 3.0 };    // 오류! std::initializer_list<T>의
                            // T를 추론할 수 없음

```

```c++
template <typename T>       // x의 선언에 해당하는 매개변수
void f(T param);            // 선언을 가진 템플릿
 
f({ 11, 23, 9 });           // 오류! T에 대한 타입을 추론할 수 없음

// 하지만 param의 타입이 어떤 알려지지 않은 T에 대한
// std::initializer_list<T>인 템플릿에 그 중괄호 초기치를
// 전달하면 템플릿 타입 추론 규칙들에 의해 T의 타입이
// 제대로 추론된다.
 
template <typename T>
void f(std::initializer_list<T> initList);
 
f({ 11, 23, 9 });            // T는 int로 추론되며, initList의 타입은
                            // std::initializer_list<int>로 추론된다.
```