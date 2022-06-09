---
layout: post
title:  "Effective c++ item20 - '값에 의한 전달'보다는 '상수객체 참조자에 의한 전달' 방식을 택하는 편이 대개 낫다."
summary: "reference to const"
author: tgparkk
date: '2022-05-04 20:12:23 +0530'
category: C++
keywords: reference to const, resource-managing, c++
permalink: /blog/effective-cpp-item20/
usemathjax: true
---

# 항목 20: '값에 의한 전달'보다는 '상수객체 참조자에 의한 전달' 방식을 택하는 편이 대개 낫다.
By default, C++ passes objects to and from functions by value (a characteristic it inherits from C)  

Unless you specify otherwise, function
parameters are initialized with copies of the actual arguments.
(함수 매개변수는 실제 인자의 '사본'을 통해 초기화되며,)  

and function callers get back a copy of the value returned by the function.
(함수호출자는 돌려받아요. 값의 복사를 그 함수에 의한)  

These copies are produced by the objects’ copy constructors.

```c++
class Person {
public:
    Person();           // parameters omitted for simplicity
    virtual ~Person();  // see Item 7 for why this is virtual
    ...
private:
    std::string name;
    std::string address;
};
class Student: public Person {
public:
    Student();          // parameters again omitted
    virtual ~Student();
    ...
private:
    std::string schoolName;
    std::string schoolAddress;
}
```
Now consider the following code, in which we call a function, validateStudent, that takes a Student argument (by value, 값으로) and returns
whether it has been validated:
```c++
bool validateStudent(Student s);            // function taking a Student
                                            // by value

Student plato;                              // Plato studied under Socrates

bool platoIsOK = validateStudent(plato);    // call the function
```
What happens when this function is called?  
확실한 거는, plato로부터 매개변수 s를 초기화시키기 위해 Student의 복사 생성자가 호출될 것입니다. 게다가 s는 validateStudent가 복귀할 때 소멸될 것이고요. 정리하면, 이 함수의 매개변수 전달 비용은 Student의 복사 생성자 호출 한 번, 그리고 Student의 소멸자 호출 한 번 입니다.  

But that’s not the whole story.  
A Student object has two string objects
within it, so every time you construct a Student object you must also
construct two string object.  
게다가, A Student object also inherits from a Person object, so every time you construct a Student object you must also construct a Person object.  

최종 결과는, 단지 Student 객체 하나를 값으로 전달했을 뿐인데 Student 복사 생성자 호출 한 번, Person 복사 생성자 호출 한 번에 추가로 String 복사 생성자 호출이 네 번 일어납니다.  
Student 객체의 사본이 소멸될 때도 암담하기는 마찬가지입니다.  

이러한 문제를 해결할 수 있는 방법이 **상수객체에 대한 참조자(reference-to-const)** 입니다.
```c++
bool validateStudent(const Student& s);
```
위 코드는 새로 만들어지는 객체가 없기 때문에, 생성자와 소멸자가 전혀 호출되지 않아요.


const참조는 매개변수가 int면 4와같은 상수 대입 가능하다


- 함수 객체 타입?


<img src="/assets/img/posts/item20_value.png" width="600" height="300" title='item20_value'>
복사생성자도 구현해야지..

<img src="/assets/img/posts/item20_const_reference.png" width="600" height="300" title='item20_const_reference'>

<img src="/assets/img/posts/item20_reference.png" width="600" height="300" title='item20_reference'>
