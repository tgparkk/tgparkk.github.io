---
layout: post
title:  "Effective c++ ch6 - 컴파일러가 만들어낸 함수가 필요 없으면 확실히 이들의 사용을 금해 버리자"
summary: "compiler, private, c++"
author: tgparkk
date: '2022-04-11 14:38:23 +0530'
category: C++
keywords: C++, compiler, private 
permalink: /blog/effective-cpp-ch6/
usemathjax: true
---

# 항목 6: 컴파일러가 만들어낸 함수가 필요 없으면 확실히 이들의 사용을 금해 버리자
집을 팔고 사며 밥을 먹는 부동산 중개업자의 주문으로, 프로그램을 만들며 밥을 먹는 개발자가 부동산 중개업 지원용 소프트웨어를 만들었습니다.  
이런 소프트웨어 시스템에는 모르긴해도 매물로 내놓은 가옥을 나타내는 클래스가 들어 있겠지요.  
```c++
class HomeForSale{...};
```
HomeForSale 객체는 사본(copy)을 만드는 것 자체가 이치에 맞지 않습니다.
```c++
HomeForSale h1;
HomeForSale h2;

HomeForSale h3(h1);     // h1을 복사하려 합니다.
                        // 컴파일되면 안 돼요!

h1 = h2;                // h2를 복사하려 합니다.
                        // 컴파일하지 말아 주세요!                        
```
주석으로나마 컴파일을 막고 싶은 바람이 어떻게든 정신적 위안은 되겠지만 안 되는 건 이미 아시죠? 세상이 그리 만만하지 않습니다.  

우리는 지금 복사를 막고 싶단 말입니다! 해결의 열쇠는 다음과 같습니다.  
바로 컴파일러가 생성하는 함수는 모두 공개된다는, 즉 public 멤버가 된다는 사실입니다. 복사 생성자와 복사 대입 연산자가 저절로 만들어지는 것을 막기 위해 여러분이 직접 선언해야 한다는 점은 맞지만, 이것들을 public 멤버로 선언해야 한다고 요구하는 곳은 아무 데도 없다는 점을 기억하셔야 하겠습니다.  

여기까지 90점입니다. 나머지 10점은 private 멤버 함수는 그 클래스의 멤버 함수 및 프렌드(friend) 함수가 호출할 수 있다는 점이 여전히 허점입니다. 이것까지 막으려면, 그러니까 '정의(define)'를 안 해 버리는 기지를 발휘해 보면 어떨까요?  

```c++
class HomeForSale{
public:
    ...
private:
    ...
    HomeForSale(const HomeForSale&); // 선언만 달랑 있습니다.
    HomeForSale& operator=(const HomeForSale&);
}
```
매개변수의 이름이 빠져 있는 게 살짝 거슬릴 수도 있겠습니다만, 선언 시 매개변수 이름은 필수사항이 아닙니다.  

HomeForSale 클래스는 이렇게 정의되었습니다. 사용자가 HomeForSale 객체의 복사를 시도하려고 하면 컴파일러가 강한 백태클을 걸 것이고, 여러분이 깜빡하고 멤버 함수 혹은 프렌드 함수 안에서 그렇게 하면 링커가 여러분을 싫어할 것입니다.  

한 가지 덧붙이면, 링크 시점 에러를 컴파일 시점 에러로 옮길 수도 있습니다.(이것이 좋습니다. 에러 탐지는 나중으로 미루는 것보다 미리 하는 것이 좋아요)  
복사 생성자와 복사 대입 연산자를 private로 선언하되, 이것을 HomeForSale 자체에 넣지 말고 별도의 기본 클래스에 넣고 이것으로부터 HomeForSale을 파생시키는 것입니다.
```c++
class Uncopyable{
protected: // 파생된 객체에 대해서
    Uncopyable() {}     // 생성과 소멸을
    ~Uncopyable() {}    // 허용합니다.
private:
    Uncopyable(const Uncopyable&);  // 하지만 복사는 방지합니다.
    Uncopyable& operator=(const Uncopyable&);
};
```
```c++
class HomeForSale:private Uncopyable{   // 복사 생성자도,
    ...                                 // 복사 대입 연산자도
};                                      // 이제는 선언되지 않습니다.
```
