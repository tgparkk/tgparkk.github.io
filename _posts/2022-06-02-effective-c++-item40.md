---
layout: post
title:  "Effective c++ item40 - 다중 상속은 심사숙고해서 사용하자"
summary: "Use multiple inheritance judiciously."
author: tgparkk
date: '2022-06-02 21:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item40/
usemathjax: true
---

# 항목 40: 다중 상속은 심사숙고해서 사용하자
When it comes to multiple inheritance (MI), the C++ community largely breaks into two basic camps.  

One of the first things to recognize is that when MI enters the designscape, it becomes possible to inherit the same name (e.g., function, typedef, etc.) from more than one base class.  
That leads to new opportunities for ambiguity. For example:
```c++
class BorrowableItem {      // something a library lets you borrow
public:
void checkOut();            // check the item out from the library
...
};
class ElectronicGadget {
private:
    bool checkOut() const;  // perform self-test, return whether
    ...                     // test succeeds
};
class MP3Player:            // note MI here
public BorrowableItem,      // (some libraries loan MP3 players)
public ElectronicGadget
{ ... };                    // class definition is unimportant

MP3Player mp;
mp.checkOut();              // ambiguous! which checkOut?
```
위 모호성을 해소하려면,
```c++
mp.BorrowableItem::checkOut(); // ah, that checkOut..
```
Multiple inheritance just means inheriting from more than one base class, but it is not uncommon for MI to be found in hierarchies that have higher-level base classes, too. That can lead to what is sometimes known as the “deadly MI diamond" :
```c++
class File { ... };

class InputFile: public File { ... };

class OutputFile: public File { ... };

class IOFile: public InputFile,
public OutputFile
{ ... };
```