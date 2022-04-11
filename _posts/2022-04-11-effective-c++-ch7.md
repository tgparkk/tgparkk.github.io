---
layout: post
title:  "Effective c++ ch7 - 다형성을 가진 기본 클래스에서는 소멸자를 반드시 가상 소멸자로 선언하자"
summary: "destructor, polymorphism, c++"
author: tgparkk
date: '2022-04-11 17:38:23 +0530'
category: C++
keywords: destructor, polymorphism, C++ 
permalink: /blog/effective-cpp-ch7/
usemathjax: true
---

# 항목 7: 다형성을 가진 기본 클래스에서는 소멸자를 반드시 가상 소멸자로 선언하자
시간 기록을 유지하는 방법은 활용에 따라 무궁무진합니다. 그래서인지 TimeKeeper 정도의 이름을 가진 클래스를 기본 클래스로 만들어 놓은 후에 적절한 용도에 따라 이것을 파생시키도록 설계하면 딱 알맞을 것 같습니다.
```c++
class TimeKeeper {
public:
    TimeKeeper();
    ~TimeKeeper();
    ...
};

class AtomicClock: public TimeKeeper {...};
class WaterClock: public TimeKeeper {...};
class WristWatch: public TimeKeeper {...};
```
이 클래스의 혜택을 받는 사용자들은 시간 정보에 접근하고 싶어 합니다. 시간 계산이 어떻게 되는지에 대해서는 신경 쓰고 싶지 않고요.  
사정이 이렇기 때문에, 어떤 시간기록 객체에 대한 포인터를 손에 넣는 용도로 팩토리 함수(factory function, 새로 생성된 파생 클래스 객체에 대한 기본 클래스 포인터를 반환하는 함수)를 만들어 두면 딱 좋을 것 같습니다.
```c++
TimeKeeper* getTimeKeeper();    // TimeKeeper에서 파생된 클래스를
                                // 통해 동적으로 할당된 객체의
                                // 포인터를 반환합니다.
```
팩토리 함수의 기존 규약을 그대로 따라간다면 getTimeKeeper 함수에서 반환되는 객체는 힙에 있게 되므로, 결국 메모리 및 기타 자원의 누출을 막기 위해 해당 객체를 적절히 삭제(delete)해야 합니다.
```c++
TimeKeeper* ptk = getTimeKeeper();  // TimeKeeper 클래스 계통으로부터
                                    // 동적으로 할당된 객체를 얻습니다.

...                                 // 이 객체를 사용합니다.

delete ptk                          // 자원 누출을 막기 위해 해제(삭제)합니다.
```