---
layout: post
title:  "Effective c++ item9 - 객체 생성 및 소멸 과정 중에는 절대로 가상 함수를 호출하지 말자"
summary: "virtual function, destruction, c++"
author: tgparkk
date: '2022-04-19 22:38:23 +0530'
category: C++
keywords: virtual function, destruction, C++ 
permalink: /blog/effective-cpp-item9/
usemathjax: true
---

# 항목 9: 객체 생성 및 소멸 과정 중에는 절대로 가상 함수를 호출하지 말자
주식 거래를 본떠 만든 클래스 계통 구조가 있다고 가정합시다. 이를테면 매도 주문, 매수 주문 등등이 있겠죠.

```c++
class Transaction {     // base class for all
public:                 // transactions
    Transaction();
    virtual void logTransaction() const = 0; // make type-dependent
                                             // log entry
...
};


Transaction::Transaction() // implementation of
{                          // base class ctor (constructor)
    ...
    logTransaction();   // as final action, log this
}                       // transaction
class BuyTransaction: public Transaction { // derived(파생) class
public:
    virtual void logTransaction() const; // how to log trans-
                                         // actions of this type ...
                                         // 이 타입에 따른 거래내역 로깅을 구현
};
class SellTransaction: public Transaction { // derived class (파생 클래스)
public:
    virtual void logTransaction() const; // how to log trans-
                                         // actions of this type
...
}
```
Consider what happens when this code is executed
```c++
BuyTransaction b;
```

BuyTransaction 생성자가 호출되는 것은 어쨌든 맞습니다. 그러나 우선은 Transaction 생성자가 호출되어야 합니다. 파생 클래스 객체가 생성될 때 그 객체의 기본 클래스 부분이 파생 클래스 부분보다 먼저 호출되는 것이 정석이니까요.  

여기서 호출되는 logTransaction 함수는 BuyTransaction의 것이 *아니라* Transaction의 것이란 사실!  
**기본 클래스 생성 과정에서는 가상 함수가 먹히지 않는다고요**

아시다시피 기본 클래스 생성자는 파생 클래스 생성자보다 앞서서 실행되기 때문에, 기본 클래스 생성자가 돌아가고 있을 시점에 파생 클래스 데이터 멤버는 아직 초기화된 상태가 아니라는 것이 핵심입니다.  
이때 기본 클래스 생성자에서 어쩌다 호출된 가상 함수가 파생 클래스 쪽으로 내려간다면 어떻게 될까요? 파생 클래스 버전의 가상 함수는 파생 클래스만의 데이터 멤버를 건드릴 것이 뻔한데, 이들은 아직 초기화되지 않았단 말입니다. -> 미정의 동작   

```c++
파생 클래스 객체의 기본 클래스 부분이 생성되는 동안은, 그 객체의 타입은 바로 기본 클래스입니다.

마찬가지로, 객체가 소멸될(소멸자가 호출될) 때에도 똑같이 생각하면 됩니다.
파생 클래스의 소멸자가 일단 호출되고 나면 파생 클래스만의 데이터 멤버는 정의되지 않은 값으로 가정하기 때문입니다.
```

이러한 문제들을 해결하는 방법은 logTransaction을 Transaction 클래스의 비가상 멤버 함수로 바꾸는 것입니다. 그러고 나서 파생 클래스의 생성자들로 하여금 필요한 로그 정보를 Transaction의 생성자로 넘겨야 한다는 규칙을 만듭니다.  
logTransaction이 비가상 함수이기 때문에 Transaction의 생성자는 이 함수를 안전하게 호출할 수 있습니다.

```c++
class Transaction {
public:
    explicit Transaction(const std::string& logInfo);
    void logTransaction(const std::string& logInfo) const; // now a non-
                                                           // virtual func
                                                           // 이제 비가상 함수입니다.

                                                           // 함수뒤에 const 붙인건 함수 내에서 데이터 조작 방지하기 위함 ex)getter함수들
    ...
};

Transaction::Transaction(const std::string& logInfo)
{
    ...
    logTransaction(logInfo); // now a non-
}                            // virtual call
                             // 이제는 비가상 함수를 호출합니다.

class BuyTransaction: public Transaction {
public:
    BuyTransaction( parameters )
    : Transaction(createLogString( parameters )) // pass log info
    { ... }                                      // to base class
                                                 // constructor
    ...                                          
                                                 // 로그 정보를 기본 클래스 생성자로 넘깁니다.

private:
    static std::string createLogString( parameters );
};
```
createLogString 이라는 정적 함수가 사용되고 있는 부분에 대해 잠깐 이야기 하려고요. 이 함수는 기본 클래스 생성자 쪽으로 넘길 값을 생성하는 용도로 쓰이는 도우미 함수인데, 기본 클래스에 멤버 초기화 리스트가 긴 경우에 특히 훨씬 편리합니다.  

또한, 정적멤버로 되어 있기 때문에 생성이 채 끝나지 않은 BuyTransaction 객체의 미초기화된 데이터 멤버를 자칫 실수로 건드릴 위험도 없습니다.  

(static 멤버변수는 프로그램 시작때부터 차지하고 있으며 메모리에 내내 값이 유지된다.)

<img src="/assets/img/posts/item9_source_print.png" width="950" height="500" title='item9_source_print'>