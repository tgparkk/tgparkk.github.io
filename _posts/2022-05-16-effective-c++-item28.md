---
layout: post
title:  "Effective c++ item28 - 내부에서 사용하는 객체에 대한 '핸들'을 반환하는 코드는 되도록 피하자"
summary: "Avoid returning “handles” to object internals."
author: tgparkk
date: '2022-05-16 23:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item28/
usemathjax: true
---

# 항목 28: 내부에서 사용하는 객체에 대한 '핸들'을 반환하는 코드는 되도록 피하자.
Suppose you’re working on an application involving rectangles.  
Each rectangle can be represented by its upper left corner and its lower
right corner.  

To keep a Rectangle object small,  
you might decide that the points defining its extent shouldn’t be stored in the Rectangle itself, but rather in an auxiliary struct that the Rectangle points to:
```c++
class Point {       // class for representing points
public:
    Point(int x, int y);
    ...
    void setX(int newVal);
    void setY(int newVal);
    ...
};

struct RectData {   // Point data for a Rectangle
Point ulhc;         // ulhc = “ upper left-hand corner”
Point lrhc;         // lrhc = “ lower right-hand corner”
};

class Rectangle {
    ...
    private:
    std::tr1::shared_ptr<RectData> pData;   // see Item 13 for info on
};                                          // tr1::shared_ptr
```

Point is a user-defined type, so, mindful of Item 20’s observation that passing user-defined types by reference is typically more efficient than passing them by value,  
these functions return references to the underlying Point objects:  

- 함수 앞에 const , 함수 뒤에 const
리턴값을 읽기 전용으로 사용하겠다는 의미
- https://pangtrue.tistory.com/16

```c++
class Rectangle {
public:
    ...
    Point& upperLeft() const { return pData->ulhc; }
    Point& lowerRight() const { return pData->lrhc; }
    ...
};
```
위에꺼는 아래처럼 해결가능해요
```c++
class Rectangle {
public:
    ...
    const Point& upperLeft() const { return pData->ulhc; }
    const Point& lowerRight() const { return pData->lrhc; }
    ...
};
```
Even so, upperLeft and lowerRight are still returning handles to an object’s internals, and that can be problematic in other ways.  

객체 내부의 핸들(handle, 다른 객체에 손을 댈 수 있게 하는 매개자) 은 어떤행위를 하든(포인터이든, 참조자이든, 반복자이든, const를 붙였든) 하더라도 조심해야해요.

- 함수 뒤에 const
* 해당 멤버 함수 내에서는 모든 멤버 변수를 상수화 시킨다.
(지역변수는 수정 가능)  

- 함수 앞에 const
* 함수의 리턴값을 상수화 시킨다.
```c++
class A
{
    int n;
    const int func1()
    {
        n = 1
        return n;
    }
}

int main()
{
    A a;
    int var = a.func1(); // error
}
```