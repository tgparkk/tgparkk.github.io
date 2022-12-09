---
layout: post
title:  "c++ thread_pool"
summary: ".."
author: tgparkk
date: '2022-12-09 11:00:23 +0530'
category: C++
keywords: c++
permalink: /blog/Thread Pool/
usemathjax: true
---

# C++ 멀티스레드 프로그래밍 - Thread Pool
(여러 스레드가 공유 메모리를 동시에 읽거나 쓰지 않도록 디자인해야 합니다!!!)

## 동작 원리
- thread 를 생성해 놓고 thread pool (보통 queue 이지만 priority queue 도 사용) 이란 곳에 얺고 thread 를 재활용 해요.
```c++
std::vector<std::thread> thread_pool;
```
