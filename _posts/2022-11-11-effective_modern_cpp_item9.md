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
