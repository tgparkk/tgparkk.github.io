---
layout: post
title:  "Effective c++ item25 - 예외를 던지지 않는 swap에 대한 지원도 생각해 보자"
summary: "Consider support for a non-throwing swap."
author: tgparkk
date: '2022-05-11 19:12:23 +0530'
category: C++
keywords: designs and declarations, c++
permalink: /blog/effective-cpp-item25/
usemathjax: true
---

# 항목 25: 예외를 던지지 않는 swap에 대한 지원도 생각해 보자.
To swap the values of two objects is to give each the other’s value. By
default, swapping is accomplished via the standard swap algorithm.
Its typical implementation is exactly what you’d expect
```c++
namespace std {
    template<typename T>    // typical implementation of std::swap;
    void swap(T& a, T& b)   // swaps a’s and b’s values
    {
        T temp(a);
        a = b;
        b = temp;
    }
}
```
As long as your types support copying (via copy constructor and copy
assignment operator), the default swap implementation will let objects
of your types be swapped without your having to do any special work
to support it.  
(***너의 타입이 복사를 지원한다면(복사 생성자 또는 복새대입연산자를 통해) 기본 *swap* 은 너의 타입 객체가 교환되게 해준다. 너의 별다른 작업 없이도***)

```c++
class WidgetImpl {          // class for Widget data;
public:                     // details are unimportant
    ...
private:
    int a, b, c;            // possibly lots of data —
    std::vector<double> v;  // expensive to copy!
    ...
};

class Widget {                              // class using the pimpl idiom
public:
    Widget(const Widget& rhs);
    Widget& operator=(const Widget& rhs)    // to copy a Widget, copy its
    {                                       // WidgetImpl object. For
                                            // details on implementing
        *pImpl = *(rhs.pImpl);              // operator= in general, 
                                            // see Items 10, 11, and 12. 
    }
    ...
private:
    WidgetImpl *pImpl;                      // ptr to object with this 
};                                          // Widget’s data
```
To swap the value of two Widget objects, all we really need to do is
swap their pImpl pointers, but the default swap algorithm has no way
to know that. Instead, it would copy not only three Widgets, but also
three WidgetImpl objects. Very inefficient. Not a thrill.  

따라서 std::swap 에다가 알려주는거죠. Widget 객체를 맞바꿀 때는 일방적인 방법을 쓰지 말고 내부의 pImpl 포인터만 맞바꾸라고 말입니다.  
std::swap을 Widget에 대해 특수화 하는 것인데, 일단 기본 아이디어만 간단히 코드로 보죠
```c++
namespace std {
template<>                      // this is a specialized version
void swap<Widget>(Widget& a,    // of std::swap for when T is
                    Widget& b)  // Widget
{
    swap(a.pImpl, b.pImpl);     // to swap Widgets, swap their
}                               // pImpl pointers; 
                                //this won’t compile
}
```
함수 시작 부분 'template<>' 부분이 std::swap의 완전 템플릿 특수화(total template specialization) 함수라는 것을 컴파일러에게 알려주는 부분 입니다.  
그리고 뒤에 '<Widget>'은 T가 Widget일 경우에 대한 특수화라는 사실을 알려 주는 부분입니다.

일반적으로는 std 네임스페이스의 구성요소는 변경할 수 없지만, 직접만든타입(Widget)
에 대해 표준 템플릿(swap)을 완전 특수화를 허용해요.  

방법으로는, Widget 안에 swap 이라는 public 멤버 함수를 선언하고 그 함수가 실제 맞바꾸기를 수행하도록 한 후에, std::swap의 특수화 함수에게 그 멤버 함수를 호출하는 일을 맡깁니다.
```c++
class Widget {                  // same as above, except for the
public:                         // addition of the swap mem func
...
void swap(Widget& other)
{
    using std::swap;            // the need for this declaration
                                // is explained later in this Item
    swap(pImpl, other.pImpl);   // to swap Widgets, swap their
}                               // pImpl pointers
...
};
namespace std {
template<>                      // revised specialization of
void swap<Widget>(Widget& a,    // std::swap
                    Widget& b)
{
    a.swap(b);                  // to swap Widgets, call their
}                               // swap member function

}

템플릿 클래스에 2부