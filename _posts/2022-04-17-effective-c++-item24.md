---
layout: post
title:  "Effective c++ item24 - 타입 변환이 모든 매개변수에 대해 적용되어야 한다면 비멤버 함수를 선언하자"
summary: "Declare non-member functions when type conversions should apply to all parameters."
author: tgparkk
date: '2022-05-08 00:12:23 +0530'
category: C++
keywords: designs and declarations, c++
permalink: /blog/effective-cpp-item24/
usemathjax: true
---

# 항목 24: 타입 변환이 모든 매개변수에 대해 적용되어야 한다면 비멤버 함수를 선언하자.
클래스의 암시번 타입 변환을 지원하는 것은 일반적으로 못된 생각입니다.  
물론 예외도 있습니다. 바로, 숫자 타입을 만들 때입니다. 예를 들어 유리수를 나타내는 클래스를 만들고 싶다면, 정수에서 유리수로의 암시적 변환은 허용하는게 이상한것이 아니죠.
```c++
class Rational {
public:
    Rational(int numerator = 0, // ctor is deliberately(고의로) not explicit;
    int denominator = 1);       // allows implicit int-to-Rational
                                // conversions

    int numerator() const;      // accessors for numerator and
    int denominator() const;    // denominator — see Item 22
private:
...
};
```
유리수를 나타내는 클리스이니 사칙연산도 지원하고 싶겠죠.  
우선 멤버 함수로 지원하는 예시를 보죠.
```c++
class Rational {
public:
    ...
    const Rational operator*(const Rational& rhs) const;
};
```
아래와 같은 예시는 가능해요.
```c++
Rational oneEighth(1, 8);
Rational oneHalf(1, 2);
Rational result = oneHalf * oneEighth;  // fine
result = result * oneEighth;            // fine
```
하지만 아래와 같은 예시는...
```c++
result = oneHalf * 2; // fine
result = 2 * oneHalf; // error!
```
위 예시가 안되는 원인을 함수 형태로 바꾸어 보면...
```c++
result = oneHalf.operator*(2);  // fine
result = 2.operator*(oneHalf ); // error!
```
첫번째 줄에서  
The object oneHalf is an instance of a class that contains an operator*,
so compilers call that function.  
 However, the integer 2 has no associated class, hence no operator* member function.  
 컴파일러는 아래처럼 호출할 수 있는 비멤버 버전의 operator*(네임스페이스 혹은 전역 유효범위에 있는 operator*)도 찾아봅니다.
 ```c++
 result = operator*(2, oneHalf ); // error!
 ```


바로 operator*를 비멤버 함수로 만들어서, 컴파일러 쪽에서 ***모든*** 인자에 대해 암시적 타입 변환을 수행하도록 내버려 두는 것입니다.
```c++
class Rational {
    ...                                         // contains no operator*
};

const Rational operator*(const Rational& lhs,   // now a non-member
                        const Rational& rhs)    // function
{
    return Rational(lhs.numerator() * rhs.numerator(), lhs.denominator() * rhs.denominator());
}

Rational oneFourth(1, 4);
Rational result;

result = oneFourth * 2; // fine
result = 2 * oneFourth; // hooray, it works!
```
