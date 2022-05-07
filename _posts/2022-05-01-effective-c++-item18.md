---
layout: post
title:  "Effective c++ item18 - 인터페이스 설계는 제대로 쓰기엔 쉽게, 엉터리로 쓰기엔 어렵게 하자"
summary: "shared_ptr, interface"
author: tgparkk
date: '2022-05-01 01:12:23 +0530'
category: C++
keywords: interface, resource-managing classes, smart pointers, c++
permalink: /blog/effective-cpp-item18/
usemathjax: true
---

# 항목 18: 인터페이스 설계는 제대로 쓰기엔 쉽게, 엉터리로 쓰기엔 어렵게 하자
'제대로 쓰이게 쉽고 엉터리로 쓰기에 어려운' 인터페이스를 개발하려면 우선 사용자가 저지를 만한 실수의 종류를 머리에 넣어두고 있어야 합니다.
```c++
class Date {
public:
    Date(int month, int day, int year);
    ...
};


Date d(30, 3, 1995); // Oops! Should be “3, 30” , not “30, 3”
Date d(3, 40, 1995); // Oops! Should be “3, 30” , not “3, 40”

```
(This last example may look silly, but remember that on a keyboard,
4 is next to 3. Such “off by one” typing errors are not uncommon.)  
Many client errors can be prevented by the introduction of new types.
Indeed, the type system is your primary ally in preventing undesirable
code from compiling. In this case, we can introduce simple wrapper
types to distinguish days, months, and years, then use these types in
the Date constructor:
```c++
struct Day { 
    explicit Day(int d)
    : val(d) {}

    int val;
};

struct Month { 
    explicit Month(int m)
    : val(m) {}

    int val;
};

struct Year {
    explicit Year(int y)
    : val(y){}

    int val;
};


class Date {
public:
    Date(const Month& m, const Day& d, const Year& y);
    ...
};
Date d(30, 3, 1995);                    // error! wrong types
Date d(Day(30), Month(3), Year(1995));  // error! wrong types
Date d(Month(3), Day(30), Year(1995));  // okay, types are correct
```
물론, Day, Month, Year에 데이터를 이것저것 숨겨 넣어 제몫을 하는 온전한 클래스로 만들면 위의 단순한 구조체보다는 확실히 낫긴 하겠지만(항목22참조), 타입을 적절히 새로 준비해 두기만 해도 인터페이스 사용 에러를 막는 데에 약발이 통한다는 점을 보여주기에는 이 정도도 충분합니다.  

일단 적절한 타입만 제대로 준비되어 있다면, 각 타입의 값에 제약을 가하더라도 괜찮은 경우가 생기게 됩니다. 예를 들어 월(月)이 가질 수 있는 유효한 값을 12개뿐이므로 제약할수 있습니다.
```c++
class Month {
public:
    static Month Jan() { return Month(1); } // functions returning all valid
    static Month Feb() { return Month(2); } // Month values; see below for
    ...                                     // why these are functions, not
    static Month Dec() { return Month(12); }// objects

    ...                                     // other member functions 
private:
    explicit Month(int m);  // prevent creation of new
                            // Month values
    ...                     // month-specific data
};
Date d(Month::Mar(), Day(30), Year(1995));
```

사용자 쪽에서 뭔가를 외워야 제대로 쓸 수 있는 인터페이스는 잘못 쓰기 쉽습니다. 언제라도 잊어버릴 수 있으니까요. 항목 13에 나온 바 있는 팩토리 함수를 예로 들어 보겠습니다.  
이 함수는 Investment 클래스 계통에 속해 있는 어떤 객체를 동적 할당하고 그 객체의 포인터를 반환하는 함수입니다.
```c++
Investment* createInvestment(); // from Item 13; parameters omitted
                                // for simplicity
                                // 매개변수는 편의상 생략합니다.
```
그래서 항목 13의 이후를 더 읽어 보시면 createInvestment의 반환 값을 스마트 포인터에 저장한 후에 해당 포인터의 삭제 작업을 스마트 포인터에 떠넘기는 방법을 확인할 수 있을 것입니다.  
하지만 이 스마트 포인터를 사용해야 한다는 것을 잊으면요?  
애초부터 팩토리 함수가 스마트 포인터를 반환하게 만드는 것입니다.
```c++
std::tr1::shared_ptr<Investment> createInvestment();
```
```c++
std::tr1::shared_ptr<Investment> createInvestment()
{
    return std::tr1::shared_ptr<Investment>(new Stock);
}
```

<img src="/assets/img/posts/item18_print.png" width="500" height="500" title='item18_print'>

<img src="/assets/img/posts/item18_source.png" width="800" height="500" title='item18_source'>