---
layout: post
title:  "Effective c++ item42 - "typename의 두 가지 의미를 제대로 파악하자"
summary: "Understand the two meanings of typename."
author: tgparkk
date: '2022-06-10 18:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item42/
usemathjax: true
---

# 항목 42: typename의 두 가지 의미를 제대로 파악하자
question: what is the difference between class and typename in the following template declarations?
```c++
template<class T> class Widget;     // uses “class”
template<typename T> class Widget;  // uses “typename”
```
Answer: nothing. When declaring a template type parameter, class and typename mean exactly the same thing.  

C++ doesn’t always view class and typename as equivalent, however.  
typename 을 써야만 할 때도 있습니다.