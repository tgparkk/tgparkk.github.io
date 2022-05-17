---
layout: post
title:  "Effective c++ item29 - 예외 안전성이 확보되는 그날 위해 싸우고 또 싸우자!"
summary: " Strive for exception-safe code."
author: tgparkk
date: '2022-05-17 17:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item29/
usemathjax: true
---

# 항목 29: 예외 안전성이 확보되는 그날 위해 싸우고 또 싸우자!
Suppose we have a class for representing GUI menus with background images.  
The class is designed to be used in a threaded environment, so it has a mutex for concurrency control:
```c++
class PrettyMenu {
public:
    ...
    void changeBackground(std::istream& imgSrc);    // change background
    ...                                             // image

private:
    Mutex mutex;        // mutex for this object 

    Image *bgImage;     // current background image

    int imageChanges;   // # of times image has been changed
                        // 배경그림이 바뀐 횟수
};
```
Consider this possible implementation of PrettyMenu’s changeBackground function.
```c++
void PrettyMenu::changeBackground(std::istream& imgSrc)
{
    lock(&mutex);                   // acquire mutex (as in Item 14)
    
    delete bgImage;                 // get rid of old background
    ++imageChanges;                 // update image change count
    bgImage = new Image(imgSrc);    // install new background
    
    unlock(&mutex);                 // release mutex
}
```
There are two requirements for exception safety, and this satisfies neither.  
When an exception is thrown, exception-safe functions:  
**■ Leak no resources.**  
The code above fails this test, because if the “new Image(imgSrc)” expression yields an exception,  
the call to unlock never gets executed, and the mutex is held forever.  

**■ Don’t allow data structures to become corrupted.**  
If “new Image(imgSrc)” throws, bgImage is left pointing to a deleted object.  
In addition, imageChanges has been incremented,  
even though it’s not true that a new image has been installed.  
(On the other hand, the old image has definitely been eliminated, so I suppose you could argue that the image has been “changed.”)