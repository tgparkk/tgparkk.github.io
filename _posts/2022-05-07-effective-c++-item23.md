---
layout: post
title:  "Effective c++ item23 - 멤버 함수보다는 비멤버 비프렌드 함수와 더 가까워지자"
summary: "Prefer non-member non-friend functions"
author: tgparkk
date: '2022-05-07 17:12:23 +0530'
category: C++
keywords: designs and declarations, c++
permalink: /blog/effective-cpp-item23/
usemathjax: true
---

# 항목 23: 멤버 함수보다는 비멤버 비프렌드 함수와 더 가까워지자.
Imagine a class for representing web browsers. Among the many functions such a class might offer are those to clear the cache of downloaded elements, clear the history of visited URLs, and remove all cookies from the system:
```c++
class WebBrowser {
public:
    ...
    void clearCache();
    void clearHistory();
    void removeCookies();
    ...
};
```
Many users will want to perform all these actions together, so WebBrowser might also offer a function to do just that:
```c++
class WebBrowser {
public:
    ...
    void clearEverything(); // calls clearCache, clearHistory,
                            // and removeCookies
    ...
};
```
Of course, this functionality could also be provided by a non-member
function that calls the appropriate member functions:
```c++
void clearBrowser(WebBrowser& wb)
{
    wb.clearCache();
    wb.clearHistory();
    wb.removeCookies();
}
```
멤버 버전인 clearEverything 와 비멤버 버전인 clearBrowser 중 어느것이 괜찮을까요?  

Counterintuitively, the member function ***clearEverything*** actually yields less encapsulation(***캡슐화***) than the non-member ***clearBrowser***.  
Furthermore, offering the non-member function allows for greater packaging flexibility for WebBrowser-related functionality, and that, in turn, yields fewer compilation dependencies and an increase in WebBrowser extensibility.  

The non-member approach is thus better than a member function in many ways. It’s important to understand why.  

We’ll begin with encapsulation. If something is encapsulated, it’s hidden from view. (***캡슐화 부터 시작할께요. 만약 어떤것이 캡슐화되어 있다면, 보이지 않게 됩니다.***)  

The fewer things can see it, the greater flexibility we have to change it,  
(***더 볼수 없게 된다면, 우리가 바꾸려고 할때 유연성이 더 커집니다.***)

because our changes directly affect only those things that can see what we change.(***우리가 볼수있는 것만 직접적으로 변경할 수 있기 때문예요.***)  

The second thing to note is that just because concerns about encapsulation dictate that a function be a non-member of one class doesn’t mean it can’t be a member of another class.(***주목할 점은 함수는 클래스의 비멤버가 되어야 한다는 말이 다른 클래스의 멤버가 될수 없다는 말은 아니다.***)