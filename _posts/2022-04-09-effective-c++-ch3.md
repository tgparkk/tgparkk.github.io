---
layout: post
title:  "Effective c++ ch3 - 낌새만 보이면 const를 들이대 보자!"
summary: "const3"
author: tgparkk
date: '2022-04-09 12:38:23 +0530'
category: C++
keywords: C++, const, 
permalink: /blog/effective-cpp-ch3/
usemathjax: true
---

# 항목 3: 낌새만 보이면 const를 들이대 보자!

const 키워드는 클래스 바깥에서는 전역 혹은 네임스페이스 유효범위의 상수를 선언(정의)하는데 쓸 수 있습니다. (항목 2 참조).  
그뿐 아니라 파일, 함수, 블록 유효범위에서 static으로 선언한 객체에도 const를 붙일 수 있습니다.

```c++
char greeting[] = "Hello";
char *p = greeting;                 // 비상수 포인터
                                    // 비상수 데이터

const char *p = greeting;           // 비상수 포인터,
                                    // 상수 데이터

char * const p = greeting;          // 상수 포인터,
                                    // 비상수 데이터

const char * const p = greeting;    // 상수 포인터,
                                    // 상수 데이터

```
const 키워드가 *표의 왼쪽에 있으면 포인터가 가리키는 대상이 상수,
const가 *표의 오른쪽에 있는 경우엔 포인터 자체가 상수
즉, 아래 두개는 같다

```c++
void f1(const Widget *pw); // 상수 Widget 객체에 대한 포인터를 매개변수
void f2(Widget const *pw); // 위와 동일
```


```c++
const_iterator ~~~
```

### 상수 벰버 함수
멤버 함수에 붙는 const 키워드의 역할은 "해당 멤버 함수가 상수 객체에 대해 호출될 함수이다" 라는 사실을 알려 주는 것입니다.
중요한 이유로, 첫째는 클래스의 인터페이스를 이해하기 좋게 하기 위해서인데, 그 클래스로 만들어진 객체를 변경할 수 있는 함수는 무엇이고, 또 변경할 수 없는 함수는 무엇인가를 사용자 쪽에서 알고 있어야 하는 것입니다.  

둘째는 이 키워드를 통해 상수 객체를 사용할 수 있게 하자는 것인데, 코드의 효율을 위해 아주 중요한 부분이기도 합니다. 항목 20에서 이야기 하고 있듯이 C++ 프로그램의 실행 성능을 높이는 핵심 기법 중 하나가 객체 전달을 '상수 개체에 대한 참조자'로 진행하는 것이기 때문이죠.  
그런데 이 기법이 제대로 살아 움직이려면 상수 상태로 전달된 객체를 조잘할 수 있는 const 멤버 함수, 즉 상수 멤버 함수가 준비되어 한다는 것이 바로 포인트입니다.  

const 키워드가 있고 없고의 차이만 있는 멤버 함수둘은 오버로딩이 가능합니다.
```c++
class TextBlock{
public:

    const char& operator[] (std::size_t position) const // 상수 객체에 대한
    { return text[position]; }                          // operator[]

    char& operator[] (std::size_t position)             // 비상수 객체에 대한
    { return text[position]; }                          // operator[]

private:
    std::string text;
}
```
위처럼 선언된 TextBlock의 operator[]는 다음과 같이 쓸 수 있습니다.

```c++
TextBlock tb("Hello");
std::cout << tb[0];     // TextBlock::operator[] 의
                        // 비상수 멤버를 호출합니다.

const TextBlock ctb("World");
std::cout << ctb[0];    // TextBlock::operator[] 의
                        // 상수 멤버를 호출합니다.
```










