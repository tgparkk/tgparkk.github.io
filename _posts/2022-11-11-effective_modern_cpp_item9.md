---
layout: post
title:  "2022-11-11-effective_modern_cpp_item9"
summary: ".."
author: tgparkk
date: '2022-11-11 18:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective_modern_cpp_item9/
usemathjax: true
---

# 항목 9: typedef보다 별칭 선언을 선호하라

```c++
typedef
 std::unique_ptr<std::unordered_map<std::string, std::string>> UPtrMapSS;

using UPtrMapSS =
 std::unique_ptr<std::unordered_map<std::string, std::string>>;

```
Given that the typedef and the alias declaration do exactly the same thing, 
it’s reasonable to wonder whether there is a solid technical reason for preferring one over the other.  

There is, but before I get to it,  
I want to mention that many people find the alias declaration easier to swallow when dealing with types involving function pointers:
(함수 포인터가 관여하는 형식을 다룰때 using 을 사용하는 것이 이해하는 사람이 많아요.)  

```c++
// FP is a synonym(동의어) for a pointer to a function taking an int and
// a const std::string& and returning nothing
typedef void (*FP)(int, const std::string&); // typedef

// same meaning as above
using FP = void (*)(int, const std::string&); // alias
 // declaration
```
보다 강력한 이유는 typedef는 템플릿화 할 수 없지만 별칭 선언은 템플릿화 할 수 있어요.