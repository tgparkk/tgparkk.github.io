---
layout: post
title:  "Effective c++ item21 - 함수에서 객체를 반환해야 할 경우에 참조자를 반환하려고 들지 말자"
summary: "reference"
author: tgparkk
date: '2022-05-05 00:12:23 +0530'
category: C++
keywords: reference, resource-managing, c++
permalink: /blog/effective-cpp-item21/
usemathjax: true
---

# 항목 21: '함수에서 객체를 반환해야 할 경우에 참조자를 반환하려고 들지 말자.
Consider a class for representing rational numbers, including a function for multiplying two rationals together:
```c++
class Rational {
public: 
    Rational(int numerator = 0,     // see Item 24 for why this
    int denominator = 1);           // ctor isn’t declared explicit
    ...
private:
    int n, d;                       // numerator and denominator
                                    // (분자 및 분모)
    friend  
    const Rational                  // see Item 3 for why the
    operator*(const Rational& lhs,  // return type is const
              const Rational& rhs);
                                    // (a*b)=c 와 같은 식이 에러가 아니게 됨
};
```
여기서 잠깐, 참조자에 대해 설명을 하겠습니다. 참조자는 그냥 이름입니다. **존재하는** 객체에 붙는 다른 이름이라고요.  
다시 operator*를 들여다 보세요. 이 함수가 참조자를 반환하도록 만들어졌다면, 이 함수가 반환하는 참조자는 반드시 이미 존재하는 Rational 객체의 참조자여야 합니다.  

There is certainly no reason to expect that such an object exists prior
to the call to operator*.  
(operator*를 호출하기 이전에 그러한 객체가 존재했다고 믿을 근거는 없어요.)
```c++
Rational a(1, 2);   // a = 1/2
Rational b(3, 5);   // b = 3/5
Rational c = a * b; // c should be 3/10
```
it seems unreasonable to expect that there already happens to exist a
rational number with the value three-tenths. No, if operator* is to
return a reference to such a number, it must create that number
object itself.  
(그러한 수의 참조를 반환하려고 한다면 반드시 그러한 수를 생성해야 해요.)  

A function can create a new object in only two ways: on the stack or
on the heap. Creation on the stack is accomplished by defining a local
variable.
```c++
const Rational& operator*(const Rational& lhs, const Rational& rhs) // warning! bad code!

{
    Rational result(lhs.n * rhs.n, lhs.d * rhs.d);
    return result;
}
```
위 방법도 문제가 있습니다. result 는 지역 객체예요. 즉, 함수가 끝날 때 덩달아 소멸되는 객체죠.

자 다음, 힙에 생성해 뒀다가 그 녀석의 참조자를 반환하는 것은 어떨까요?
```c++
const Rational& operator*(const Rational& lhs, const Rational& rhs) // warning! more bad code!                            
{
    Rational *result = new Rational(lhs.n * rhs.n, lhs.d * rhs.d);
    return *result;
}
```
위 코드는 누가 delete 해주죠..?  
위 코드로 연산을 해보면,
```c++
Rational w, x, y, z;
w = x * y * z;      // same as operator*(operator*(x, y), z)
```
여기서는 한 문장 안에서 operator* 호출이 두 번 일어나고 있기 때문에, new에 짝을 맞추어 delete를 호출하는 작업도 두 번이 필요합니다.  
이를 해결할 방법은 없는거 아시죠?  

최후의 수단인 정적 객체 또한 스레드 안정성 문제, 
```c++
const Rational& operator*(const Rational& lhs, const Rational& rhs)                            
{
    return Rational(lhs.n * rhs.n, lhs.d * rhs.d);
}
```
