---
layout: post
title:  "2022-10-14-effective_modern_cpp_item8"
summary: ".."
author: tgparkk
date: '2022-10-14 08:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective_modern_cpp_item8/
usemathjax: true
---

# 항목 3: 0과 NULL
비록 c++가 0을 널 포인터로 해석하지만, 0은 int이지만 포인터는 아닙니다.  
NULL 도 컴파일러에 따라 int 가 아닌 long 으로 정의될수도 있죠.