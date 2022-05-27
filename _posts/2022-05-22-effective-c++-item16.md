---
layout: post
title:  "Effective c++ item16 - new 및 delete를 사용할 때는 형태를 반드시 맞추자"
summary: "Use the same form in corresponding uses of new and delete."
author: tgparkk
date: '2022-05-22 19:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item16/
usemathjax: true
---

# 항목 16: new 및 delete를 사용할 때는 형태를 반드시 맞추자
```c++
std::string *stringArray = new std::string[100];
...
delete stringArray;
```
The program’s behavior is undefined.  
At the very least, 99 of the 100 string objects pointed to by stringArray are unlikely to be properly destroyed, because their destructors will probably never be called.  

When you employ a ***new*** expression, two things happen.  
First, memory is allocated (via a function named operator new)  
Second, one or more constructors are called for that memory.  

When you employ a ***delete*** expression (i.e., use delete), two other things happen:
one or more destructors are called for the memory, then the memory is deallocated (via a function named operator delete — see Item 51).  
The big question for delete is this: how many objects reside in the memory being deleted?  
The answer to that determines how many destructors must be called.

- new 와 delete 는 세트로
- 배열로 선언할시엔 delete[]
- typedef 로 정의된 배열로 된 타입은 new 로 할당하지 마세요
- 표준 c++ 라이브러리, 예를들어 vector 를 사용하면 됩니다.