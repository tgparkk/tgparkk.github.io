---
layout: post
title:  "Effective c++ ch8 - 예외가 소멸자를 떠나지 못하도록 붙들어 놓자"
summary: "destructor, exceptions, c++"
author: tgparkk
date: '2022-04-17 20:38:23 +0530'
category: C++
keywords: destructor, exceptions, C++ 
permalink: /blog/effective-cpp-ch8/
usemathjax: true
---

# 항목 8: 예외가 소멸자를 떠나지 못하도록 붙들어 놓자
C++는 소멸자가 예외를 내보내는 것을 막는 것은 아니지만, 실제 상황을 들춰보면 확실히 우리가 막을 수밖에 없는 것 같습니다.
```c++
class Widget{
public:
    ...
    ~Widget() {...} // 이 함수로부터 예외가 발생된다고 가정합니다.
};

void doSomething()
{
std::vector<Widget> v;
... // v는 여기서 자동으로 소멸됩니다.
}
```
v에 들어 있는 Widget이 열 개인데, 첫 번째 것을 소멸시키는 도중에 예외가 발생되었다고 가정합시다.  
 나머지 아홉 개는 여전히 소멸되어야 하므로, v는 이들에 대해 소멸자를 호출해야 할 것입니다.   
그런데 이 과정에서 문제가 떠 터졌다고 가정하면 프로그램 종료나 미정의 동작을 발생시킵니다.  
C++는 예외를 내보내는 소멸자를 좋아하지 않는단 말입니다.  

```c++
class DBConnection {
public:
...
    static DBConnection create(); // function to return
                                  // DBConnection objects; params
                                  // omitted for simplicity
    void close();                 // close connection; throw an
};
```
보다시피 사용자가 DBConnection 객체에 대해 cloase 를 직접 호출해야 하는 설계입니다.  
사용자의 망각을 사전에 차단하는 좋은 방법이라면 DBConnection 에 대한 자원 관리 클래스를 만들어서 그 클래스의 소멸자에서 close를 호출하게 만드는 것이겠지요... 이러한 내용은 3장에서...  


```c++
class DBConn { // class to manage DBConnection
public:        // objects ...
    ~DBConn() // make sure database connections
    {         // are always closed
        db.close();
    }
private:
    DBConnection db;
};
```
그러나 close 를 호출했는데 여기서 예외가 발생했다고 가정하면 또한 문제입니다.
아래 두 가지 방법이 있습니다.  

* close에서 예외가 발생하면 **프로그램을 바로 끝냅니다.** 대개 abort를 호출합니다.
```c++
DBConn::~DBConn()
{
    try { db.close(); }
    catch (...) {
        make log entry that the call to close failed;
        std::abort();
    }
}
```
객체 소멸이 진행되다가 에러가 발생한 후에 프로그램 실행을 계속할 수 없는 상황이라면 꽤 괜찮은 선택입니다.  
간단히 말해, abort를 호출해서 못 볼꼴을 미라 안 보여 주겠다는 의도죠.  

* close를 호출한 곳에서 일어난 **예외를 삼켜 버립니다**.
```c++
DBConn::~DBConn()
{
    try { db.close(); }
    catch (...) {
        make log entry that the call to close failed;
    }
}
```

~~  
둘 다 문제점이 있습니다.  

더 좋은 전략을 고민해 보도록 하죠. DBConn 인터페이스를 잘 설계해서, 발생할 소지가 있는 문제에 대처할 기회를 사용자가 가질 수 있도록 하면 어떨까요?

```c++
class DBConn {
public:
    ...
    void close() // new function for / 사용자 호출을 배려해서 새로 만든 함수
    {            // client use
        db.close();
        closed = true;
    }
    ~DBConn()
    {
        if (!closed) {
            try {           // close the connection / 사용자가 연결을 안 닫았으면 여기서 닫아 봅니다.
                db.close(); // if the client didn’t
            }
            catch (...) { // if closing fails,
            make log entry that call to close failed; // note that and ... // terminate or swallow

            // 연결을 닫다가 실패하면, 실패를 알린 후에 실행을 끝내거나 예외를 삼킵니다.
            }
        }
    }
private:
    DBConnection db;
    bool closed;
};
```

어떤 동작이 예외를 일으키면서 실패할 가능성이 있고 또 그 예외를 처리해야 할 필요가 있다면, 그 예외는 **소멸자가 아닌 다른 함수에서 비롯된 것이어야 한다** 는 것이 포인트 입니다.