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

타입 정보를 꺼내는작업을 런타임에 하려고한 코드
```c++
template<typename IterT, typename DistT>
void advance(IterT& iter, DistT d)
{
    if (typeid(typename std::iterator_traits<IterT>::iterator_category) ==
typeid(std::random_access_iterator_tag)) {
        iter += d;                          // use iterator arithmetic
    }                                       // for random access iters
    else {
        if (d >= 0) { while (d--) ++iter; } // use iterative calls to
        else { while (d++) --iter; }        // ++ or -- for other
    }                                       // iterator categories
}
```
1. 타입점검이 런타임에~
2. 타입점검 코드가 실행파일에 들어가 있음

```c++
std::list<int>::iterator iter;
...
advance(iter, 10);  // move iter 10 elements forward;
                    // won’t compile with above impl.
```
위 코드를 컴파일 했을때 아래와 같은 advance가 만들어질지 생각해보면,
```c++
void advance(std::list<int>::iterator& iter, int d)
{
    if (typeid(std::iterator_traits<std::list<int>::iterator>::iterator_category) ==
                                            typeid(std::random_access_iterator_tag)) {
        iter += d; // error! won’t compile
    }
    else {
        if (d >= 0) { while (d--) ++iter; }
        else { while (d++) --iter; }
    }
}
```
std::list<int>::iterator는 양방향 반복이기 때문에 += 연산을 지원 못하죠.  
+= 는 임의 접근 반복자에섬나 가능하니깐요.  

하지만, 위 코드는 if에서부터 실패하죠 (typeid 점검 실패)