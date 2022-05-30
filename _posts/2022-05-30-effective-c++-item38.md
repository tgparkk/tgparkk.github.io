---
layout: post
title:  "Effective c++ item38 - ""has-a" 혹은 "is-implemented-in-terms-of"를 모형화할 때는 객체 합성을 사용하자"
summary: "Model “has-a” or “is-implemented-in-terms of” through composition."
author: tgparkk
date: '2022-05-30 18:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item38/
usemathjax: true
---

# 항목 38: "has-a" 혹은 "is-implemented-in-terms-of"를 모형화할 때는 객체 합성을 사용하자
Composition is the relationship between types that arises when objects of one type contain objects of another type.
```c++
class Address { ... };          // where someone lives
class PhoneNumber { ... };
class Person {
public:
...
private:
    std::string name;           // composed object
    Address address;            // ditto
    PhoneNumber voiceNumber;    // ditto
    PhoneNumber faxNumber;      // ditto
};
```
In particular, you decide to have your nascent Set template inherit from list. That is, Set<T> will inherit from list<T>.  
After all, in your implementation, a Set object will in fact be a list object. You thus declare your Set template like this:
```c++
template<typename T> // the wrong way to use list for Set
class Set: public std::list<T> { ... };
```
Everything may seem fine at this point, but in fact there is something quite wrong.  
As Item 32 explains, if D ***is-a*** B, everything true of B is also true of D.  

However, a list object may contain duplicates, so if the value 3051 is inserted into a list<int> twice, that list will contain two copies of 3051.  
In contrast, a Set may not contain duplicates, so if the value 3051 is inserted into a Set<int> twice, the set contains only one copy of the value.  

The right way is to realize that a Set object can be implemented in terms of a list object:
```c++
template<class T>       // the right way to use list for Set
class Set {
public:
    bool member(const T& item) const;
    void insert(const T& item);
    void remove(const T& item);
    std::size_t size() const;
private:
    std::list<T> rep;   // representation for Set data 
};
```
- Composition has meanings completely different from that of public inheritance. 
- In the application domain, composition means has-a. In the implementation domain, it means is-implemented-in-terms-of