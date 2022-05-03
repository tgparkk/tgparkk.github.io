---
layout: post
title:  "Effective c++ item5 - C++가 은근슬쩍 만들어 호출해 버리는 함수들에 촉각을 세우자"
summary: "copy constructor, copy assignment operator, destructor"
author: tgparkk
date: '2022-04-10 22:38:23 +0530'
category: C++
keywords: C++, copy constructor, copy assignment operator, destructor, 
permalink: /blog/effective-cpp-item5/
usemathjax: true
---

# 항목 5: C++가 은근슬쩍 만들어 호출해 버리는 함수들에 촉각을 세우자
C++의 어떤 멤버 함수는 여러분이 클래스 안에 직접 선언해 넣지 않으면 컴파일러가 저절로 선언해 주도록 되어 있습니다.  

바로 생성자, 복사 생성자(copy constructor), 복사 대입 연산자(copy assignment operator), 그리고 소멸자(destructor) 선언해 놓습니다.  

이들은 모두 public 멤버이며 inline함수입니다. 그러니까, 여러분이 다음과 같이 썻다면
```c++
class Empty();
```
다음과 같이 쓴 것과 근복적으로 대동소이하다는 이야기입니다.
```c++
class Empty(){
public:
    Empty() {...}                               // 기본 생성자
    Empty(const Empty& rhs) {...}               // 복사 생성자
    ~Empty() {...}                              // 소멸자

    Empty& operator=(const Empty& rhs) {...}    // 복사 대입 연산자
}
```

```c++
Empty e1;       // 기본 생성자, 그리고
                // 소멸자
Empty e2(e1);   // 복사 생성자
e2 = e1;        // 복사 대입 연산자
```
기본 클래스 및 비정적 데이터 멤버의 생성자와 소멸자를 호출하는 코드가 여기서 생기는 거지요. 이때 소멸자는 이 클래스가 상속한 기본 클래스의 소멸자가 가상 소멸자로 되어 있지 않으면 역시 비가상 소멸자로 만들어진다는 점을 꼭 짚고 가야겠습니다.  

복사 생성자와 복사 대입 연산자 경우에는 어떨까요? 컴파일러가 몰래 만들어낸 복사 생성자/복사 대입 연산자가 하는 일은 아주 단순합니다.  

원본 객체의 비정적 데이터를 사본 객체 쪽으로 그냥 복사하는 것이 전부이지요.  
이해를 돕는 의미에서, 임의의 이름을 T 타입의 객체에 연결시켜 주는 NamedObject 라는 템플릿을 예제로 준비해 보았습니다.
```c++
template<typename T>
class NamedObject{
public:
    NamedObject(const char* name, const T& value);
    NamedObject(const std::string& name, const T& value);
    ...
private:
    std::string nameValue;
    T objectValue;
}
```
이 NamedObject 템플릿 안에는 생성자가 선언되어 있으므로, 컴파일러는 기본 생성자를 만들어내지 않을 것입니다. 이게 아주 중요합니다. 다시 말하면, 만약 생성자 인자가 꼭 필요한 클래스를 만드는 것이 여러분 결정이고 그렇게 했다면, 인자를 받지 않는 생성자를 컴파일러가 눈치 없이 만들지 않습니다.  

반면, 복사 생성자나 복사 대입 연산자는 NamedObject에 선언되어 있지 않기 때문에, 이 두 함수의 기본형이 컴파일러에 의해 만들어집니다(물론 필요하면요).  
```c++
NamedObject<int> no1("Smallest Prime Number", 2);
NamedObject<int> no2(no1); // 여기서 복사 생성자를 호출합니다.
```
컴파일러가 만들어주는 NamedObject<int> 의 복사 대입 연산자도 근본적으로는 동작 원리가 똑같습니다. 이 복사 대입 연산자의 동작이 설명한 대로 되려면 'legal', 'resonable' 해야 합니다. 둘 중 어느 검사도 통과하지 못하면 컴파일러는 operator= 의 자동생성을 거부해 버립니다.  

```c++
template<typename T>
class NamedObject {
public:
    // 이 생성자는 이제 상수 타입의 name을 취하지 않습니다. nameValue가
    // 비상수 string의 참조자가 되었기 때문입니다. 참조할 string을 가져야 하기
    // 때문에 char*는 없애 버렸습니다.
    NamedObject(std::string& name, const T& value);

private:
    std::string& nameValue; // 이제 이 멤버는 참조자입니다.
    const T objectValue;    // 이제 이 멤번느 상수입니다.
};
```
자, 그럼 여기서 어떤 일이 일어날지 생각해 봅시다.
```c++
std::string newDog("Persephone");
std::string oldDog("Satch");

NamedObject<int> p(newDog, 2);
NamedObject<int> s(oldDog, 36);

p = s;
```
대입 연산이 일어나기 전, p.nameValue 및 s.nameValue 는 string 객체를 참조하고 있습니다. 이때 대입 연산이 일어나면 p.nameValue 가 어떻게 되어야 할까요?  
s.nameValue가 참조하는 string을 가리켜야 할까요? 다시 말해, 참조자 자체가 바뀌어야 하는 걸까요? <- 컴파일러는 컴파일을 거부합니다.  
그렇기 때문에, 참조자를 데이터 멤버로 갖고 있는 클래스에 대입 연산을 지원하려면 직접 복사 대입 연산자를 정의해 주어야 합니다.