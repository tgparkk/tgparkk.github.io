---
layout: post
title:  "Effective c++ item33 - 상속된 이름을 숨기는 일은 피하자"
summary: "Avoid hiding inherited names."
author: tgparkk
date: '2022-05-20 21:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item33/
usemathjax: true
---

# 항목 33: 상속된 이름을 숨기는 일은 피하자
The matter actually has nothing to do with inheritance. It has to do with scopes. We all know that in code like this.
```c++
int x;              // global variable
void someFunc()
{
    double x;       // local variable
    std::cin >> x;  // read a new value for local x
}
```
<img src="/assets/img/posts/item33_grobal_somefunc.png" width="300" height="150" title='item33_grobal_somefunc'>

When compilers are in someFunc’s scope and they encounter the name x, they look in the local scope to see if there is something with that name.  
Because there is, they never examine any other scope.