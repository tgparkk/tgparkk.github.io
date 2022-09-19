---
layout: post
title:  "Effective c++ item48 - 템플릿 메타프로그래밍, 하지 않겠는가?"
summary: "Be aware of template metaprogramming."
author: tgparkk
date: '2022-09-19 22:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item48/
usemathjax: true
---

# 항목 48: 템플릿 메타프로그래밍, 하지 않겠는가?
Template metaprogramming (TMP) is the process of writing template based C++ programs that execute during compilation.  

a template metaprogram is a program written in C++ that executes inside the C++ compiler.  

C++ was not designed for template metaprogramming, but since TMP was discovered in the early 1990s.  

TMP has two great strengths. First, it makes some things easy that would otherwise be hard or impossible.  

Second, because template metaprograms execute during C++ compilation, they can shift work from runtime to compile-time.  

One consequence is that some kinds of errors that are usually detected at runtime can be found during compilation.  
Another is that C++ programs making use of TMP can be more efficient in just about every way: smaller executables, shorter runtimes, lesser memory requirements.