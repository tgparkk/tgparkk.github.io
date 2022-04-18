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

delete ptk;                         // 자원 누출을 막기 위해 해제(삭제)합니다.
```

문제는 getTimeKeeper 함수가 반환하는 포인터가 파생 클래스(그러니까 AtomicClock) 객체에 대한 포인터라는 점과 이 포인터가 가리키는 객체가 삭제될 때는 기본 클래스 포인터(즉, TimeKeeper* 포인터)를 통해 삭제된다는 점, 그리고 결정적으로 기본 클래스(TimeKeeper)에 들어 있는 소멸자가 *비가상 소멸자(non-virtual destructor)*라는 점입니다.  
C++의 규정에 의하면, 기본 클래스 포인터를 통해 파생 클래스 객체가 삭제될 때, 그 기본 클래스에 비가상 소멸자가 들어 있으면 프로그램 동작은 미정의 사항이라고 되어 있습니다. 대개 그 객체의 파생 클래스 부분이 소멸되지 않게 되지요.  

정리하면, getTimeKeeper 함수에서 포인터를 통해 날아오는 AtomicClock 객체는 기본 클래스 포인터를 통해 삭제 될 때 AtomicClock 부분(그러니까 AtomicClock 클래스에서 정의된 데이터 멤버들)이 저세상으로 가지 못할 뿐만 아니라 AtomicClock의 소멸자도 실행되지 않습니다. 그러나 기본 클래스 부분(즉, TimeKeeper 부분)은 소멸 과정이 제대로 끝나므로 결국 반쪽짜리 '부분 소멸(partially destoryed)' 객체의 신세로 전략하는 거죠.  

이 문제는 없애는 방법은 기본클래스에게 가상 소멸자를 붙이면 됩니다.
```c++
class TimeKeeper {
public:
    TimeKeeper();
    virtual ~TimeKeeper();
    ...
};

TimeKeeper* ptk = getTimeKeeper();  
                                    

...                                 

delete ptk;     // 이제 제대로 동작합니다.

```

