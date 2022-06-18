---
layout: post
title:  "Effective c++ item43 - "템플릿으로 만들어진 기본 클래스 안의 이름에 접근하는 방법을 알아 두자"
summary: " Know how to access names in templatized base classes."
author: tgparkk
date: '2022-06-18 22:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item43/
usemathjax: true
---

# 항목 43: 템플릿으로 만들어진 기본 클래스 안의 이름에 접근하는 방법을 알아 두자
Suppose we need to write an application that can send messages to several different companies.  
```c++
class CompanyA {
public:
    ...
    void sendCleartext(const std::string& msg);
    void sendEncrypted(const std::string& msg);
    ...
};
class CompanyB {
public:
    ...
    void sendCleartext(const std::string& msg);
    void sendEncrypted(const std::string& msg);
    ...
};
...                                         // classes for other companies
class MsgInfo { ... };                      // class for holding information
                                            // used to create a message
template<typename Company>
class MsgSender {
public:
    ... // ctors, dtor, etc.
    void sendClear(const MsgInfo& info)
    {
        std::string msg;
        create msg from info;
        Company c;
        c.sendCleartext(msg);
    }
    void sendSecret(const MsgInfo& info)    // similar to sendClear, except
    { ... }                                 // calls c.sendEncrypted
};
```
This will work fine, but suppose we sometimes want to log some information each time we send a message.  
A derived class can easily add that capability, and this seems like a reasonable way to do it:
```c++
template<typename Company>
class LoggingMsgSender: public MsgSender<Company> {
public:
    ...                                         // ctors, dtor, etc.

    void sendClearMsg(const MsgInfo& info)
    {
        write "before sending" info to the log;
        sendClear(info);                        // call base class function;
                                                // this code will not compile!
        write "after sending" info to the log;
    }
    ...
};

```