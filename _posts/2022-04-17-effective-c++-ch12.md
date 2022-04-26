---
layout: post
title:  "Effective c++ item12 - 객체의 모든 부분을 빠짐없이 복사하자"
summary: "self assignment operator= , c++"
author: tgparkk
date: '2022-04-26 18:52:23 +0530'
category: C++
keywords: this, self assignment operators= , c++
permalink: /blog/effective-cpp-item12/
usemathjax: true
---

# 항목 12: 객체의 모든 부분을 빠짐없이 복사하자
In well-designed object-oriented systems that encapsulate(캡슐화하다) the internal
parts of objects, only two functions copy objects: the aptly(적절히) named
copy constructor and copy assignment operator.  
We’ll call these the copying functions.
```c++
void logCall(const std::string& funcName);          // make a log entry
class Customer {
public:
    ...
    Customer(const Customer& rhs);
    Customer& operator=(const Customer& rhs);
    ...
private:
    std::string name;
};

Customer::Customer(const Customer& rhs)
    : name(rhs.name) // copy rhs’s data
{
    logCall("Customer copy constructor");
}

Customer& Customer::operator=(const Customer& rhs)
{
    logCall("Customer copy assignment operator");
    name = rhs.name;                                // copy rhs’s data
    return *this;                                   // see Item 10
}
```
Everything here looks fine, and in fact everything is fine — until
another data member is added to Customer:
```c++
class Date { ... };     // for dates in time (날짜 정보를 위한 클래스)
class Customer {
public:
    ...                 // as before (이전과 동일)
private:
    std::string name;
    Date lastTransaction;
};
```
At this point, the existing copying functions are performing a partial copy:  
they’re copying the customer’s name, but not its lastTransaction.  

The conclusion is obvious: if you add a data member to a class, you need to make
sure that you update the copying functions,  (You’ll also need to
update all the constructors (see Items 4 and 45) as well as any nonstandard forms of operator= in the class (Item 10 gives an example).
```c++
class PriorityCustomer: public Customer { // a derived class
public:
    ...
    PriorityCustomer(const PriorityCustomer& rhs);
    PriorityCustomer& operator=(const PriorityCustomer& rhs);
    ...
private:
    int priority;
};

PriorityCustomer::PriorityCustomer(const PriorityCustomer& rhs)
    : priority(rhs.priority)
{
    logCall("PriorityCustomer copy constructor");
}

PriorityCustomer&
PriorityCustomer::operator=(const PriorityCustomer& rhs)
{
    logCall("PriorityCustomer copy assignment operator");
    priority = rhs.priority;
    return *this;
}
```
위 내용은 아래와 같이 수정되어야 합니다.
```c++
PriorityCustomer::PriorityCustomer(const PriorityCustomer& rhs)
    : Customer(rhs), // invoke base class copy ctor(기본클래스의 복사생성자 호출)
    priority(rhs.priority)
{
    logCall("PriorityCustomer copy constructor");
}

PriorityCustomer&
PriorityCustomer::operator=(const PriorityCustomer& rhs)
{
    logCall("PriorityCustomer copy assignment operator");
    Customer::operator=(rhs); // assign base class parts(기본클래스 부분을 대입)
    priority = rhs.priority;
    return *this;
}

```