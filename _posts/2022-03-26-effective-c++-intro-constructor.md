---
layout: post
title:  "Effective c++ intro - constructor"
summary: "constructor"
author: tgparkk
date: '2022-03-26 23:38:23 +0530'
category: C++
keywords: C++, constructor
permalink: /blog/effective-c++-intro-constructor/
usemathjax: true
---

## constructor 생성자

복사 생성자(copy constructor)는 어떤 객체의 초기화를 위해 그와 같은 타입의 객체로부터 초기화할 때 호출되는 함수이고,  
복사 대입 연산자는 (copy assignment operator)는 같은 타입의 다른 객체에 어떤 객체의 값을 복사하는 용도로 쓰이는 함수입니다.

```c++
class Widget {
public:
    Widget();                               // 기본 생성자 
    Widget(const Widget& rhs);              // 복사 생성자
    Widget& operator=(const Widget& rhs);   // 복사 대입 연산자
};

Widget w1;                                  // 기본 생성자 호출
Widget w2(w1);                              // 복사 생성자 호출
w1 = w2;                                    // 복사 대입 연산자 호출

```

대입문처럼 보이는 '=' 문법은 복사 생성자를 호출하는 데도 쓰일 수 있습니다.
```c++
Widget w3 = w2;                             // 여기서는 복사 생성자 호출되는 것!
```

어떤 객체가 새로 정의될 때(이를테면 위 문장의 w3처럼)는 생성자가 불려야 합니다.
  
복사 생성자는 중요하다. 값에 의한 객체 전달을 정의해 주는 함수가 바로 복사 생성자이기 때문이다. 다음 예를 보십시오.
```c++
bool hasAccecptableQuality(Widget w);

Widget aWidget;
if(hasAccecptableQuality(aWidget)) ...
```
이 코드에서 매개변수 w는 hasAccecptableQuality 함수에  값으로 넘겨지도록 되어 있으므로,  

실제 호출에서 aWidget은 w로 복사됩니다. 이때 수행되는 복사에 Widget의 복사 생성자가 쓰이는 것입니다.  

'값에 의한 전달(pass-by-value)'은 '복사 생성자 호출' 이라고 이해하시면 되겠습니다.  

(하지만 사용자 정의 타입을 값으로 넘기는 발상은 일방적으로 좋지 않다고 알려져 있습니다.  그보다는 '상수 객체에 대한 참조로 넘기기' 가 더 좋답니다.)