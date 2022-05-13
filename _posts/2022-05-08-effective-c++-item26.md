---
layout: post
title:  "Effective c++ item26 - 변수 정의는 늦출 수 있는 데까지 늦추는 근성을 발휘하자"
summary: "Consider support for a non-throwing swap."
author: tgparkk
date: '2022-05-14 00:45:23 +0530'
category: C++
keywords: designs and declarations, c++
permalink: /blog/effective-cpp-item26/
usemathjax: true
---

# 항목 26: 변수 정의는 늦출 수 있는 데까지 늦추는 근성을 발휘하자.
Consider the following function,  
which returns an encrypted version of a password,  
provided the password is long enough.  
If the password is too short, the function throws an exception of type logic_error, which is defined in the standard C++ library
```c++
// this function defines the variable "encrypted" too soon
std::string encryptPassword(const std::string& password)
{
    using namespace std;
    string encrypted;
    if (password.length() < MinimumPasswordLength) {
        throw logic_error("Password is too short");
    }
    ...     // do whatever is necessary to place an
            // encrypted version of password in encrypted
    return encrypted;
}
```
```c++
// this function postpones encrypted’s definition until it’s truly necessary
std::string encryptPassword(const std::string& password)
{
    using namespace std;
    if (password.length() < MinimumPasswordLength) {
        throw logic_error("Password is too short");
    }
    string encrypted;
    ...                 // do whatever is necessary to place an
                        // encrypted version of password in encrypted
    return encrypted;
}
```

```c++
// finally, the best way to define and initialize encrypted
std::string encryptPassword(const std::string& password)
{
    ...                         // import std and check length 
    string encrypted(password); // define and initialize via copy
                                // constructor
    encrypt(encrypted);
    return encrypted;
}
```