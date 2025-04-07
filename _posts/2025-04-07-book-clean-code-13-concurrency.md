---
layout: post
title: "클린코드 13장: 동시성"
date: 2025-04-07
categories: book
tags: [clean code, cpp, concurrency, multi thread]
excerpt: "그동안 컴퓨터 책을 참 많이도 샀습니다. 마침 회사에서 클린코드 13장을 정리해야했고, 앞으로 클린코드 뿐만 아니라 많이도 산 책들을 조금씩 정리해보려고 합니다."
---

그동안 컴퓨터 책을 참 많이도 샀습니다. 마침 회사에서 클린코드 13장을 정리해야했고, 앞으로 클린코드 뿐만 아니라 많이도 산 책들을 조금씩 정리해보려고 합니다.

# 클린코드 13장: 동시성 종합 정리

## 개요
- 동시성과 깔끔한 코드는 양립하기 어렵다
- 이 장에서는:
  - 여러 스레드를 동시에 돌리는 이유
  - 여러 스레드를 동시에 돌리는 어려움
  - 동시성을 테스트하는 방법과 문제점

## 동시성이 필요한 이유
- 동시성은 결합을 없애는 전략으로, 무엇(what)과 언제(when)를 분리
  - 스레드가 하나인 프로그램은 무엇과 언제가 서로 밀접하게 결합
  - 무엇과 언제를 분리하면 애플리케이션 구조와 효율이 극적으로 개선
  - 예: 웹 애플리케이션이 표준으로 사용하는 서블릿 모델
- 동시성은 구조적 개선만이 아닌 응답시간과 작업 처리량 개선이 필요할 때도 사용

## 동시성에 관한 미신과 오해
- 미신: "동시성은 항상 성능을 높인다"
  - 실제로는 다소 부하를 유발할 수 있음
- 미신: "동시성을 구현해도 설계는 변하지 않는다"
  - 실제로는 동시성을 구현하려면 근본적인 설계 전략을 재고해야 함
- 동시성은 복잡성이 증가하고, 버그는 재현이 어려움

## 동시성 오류가 발생하는 이유

동시성 오류는 주로 공유 자원에 대한 경쟁 상태(race condition)에서 발생합니다. 간단한 증가 연산도 어셈블리 수준에서는 여러 단계로 이루어집니다:

```cpp
#include <iostream>
#include <thread>
#include <vector>
#include <mutex>

int counter = 0;

void incrementCounter(int iterations) {
    for (int i = 0; i < iterations; i++) {
        // counter++ 연산은 실제로 다음과 같은 단계로 이루어짐:
        // 1. 메모리에서 counter 값을 레지스터로 로드
        // 2. 레지스터에서 값을 1 증가
        // 3. 증가된 값을 메모리에 다시 저장
        counter++;
    }
}

int main() {
    const int NUM_THREADS = 4;
    const int ITERATIONS = 100000;
    
    // 여러 스레드가 동시에 counter 증가
    std::vector<std::thread> threads;
    for (int i = 0; i < NUM_THREADS; i++) {
        threads.push_back(std::thread(incrementCounter, ITERATIONS));
    }
    
    // 모든 스레드 종료 대기
    for (auto& t : threads) {
        t.join();
    }
    
    // 예상: NUM_THREADS * ITERATIONS = 400000
    // 실제: 경쟁 상태로 인해 이보다 작은 값이 출력됨
    std::cout << "Counter 값: " << counter << std::endl;
    std::cout << "예상 값: " << NUM_THREADS * ITERATIONS << std::endl;
    
    return 0;
}
```

## 동시성 방어 원칙

### 단일 책임 원칙(SRP)
- 주어진 메서드/클래스/컴포넌트를 변경할 이유가 하나여야 한다는 원칙
- 동시성 관련 코드는 다른 코드와 분리해야 함

```cpp
// 잘못된 예: 비즈니스 로직과 동시성 코드가 혼합
class OrderProcessor {
public:
    void processOrder(Order& order) {
        std::lock_guard<std::mutex> lock(mutex);
        validateOrder(order);
        calculateTotal(order);
        saveToDatabase(order);
    }
    
private:
    std::mutex mutex;
    void validateOrder(Order& order) { /* ... */ }
    void calculateTotal(Order& order) { /* ... */ }
    void saveToDatabase(Order& order) { /* ... */ }
};

// 개선된 예: 동시성 관리는 별도 클래스로
class OrderProcessor {
public:
    void processOrder(Order& order) {
        validateOrder(order);
        calculateTotal(order);
        saveToDatabase(order);
    }
    
private:
    void validateOrder(Order& order) { /* ... */ }
    void calculateTotal(Order& order) { /* ... */ }
    void saveToDatabase(Order& order) { /* ... */ }
};

class ConcurrentOrderProcessor {
public:
    ConcurrentOrderProcessor(OrderProcessor& processor) : processor(processor) {}
    
    void processOrderConcurrently(Order& order) {
        std::lock_guard<std::mutex> lock(mutex);
        processor.processOrder(order);
    }
    
private:
    OrderProcessor& processor;
    std::mutex mutex;
};
```

### 자료 범위 제한
- 공유 객체를 사용하는 코드 내 임계영역을 최소화
- 공유 자원에 대한 접근을 캡슐화

```cpp
// 잘못된 예: 공유 자원(account)이 외부에 노출됨
class BankService {
public:
    Account* getAccount(const std::string& id) {
        // 계좌 검색 및 반환
        return &accounts[id];
    }
    
private:
    std::map<std::string, Account> accounts;
};

// 클라이언트 코드
// 여러 스레드에서 account 객체에 직접 접근 가능
Account* account = bankService.getAccount("12345");
account->withdraw(100.0);

// 개선된 예: 공유 자원 접근을 캡슐화
class BankService {
public:
    void transfer(const std::string& fromId, const std::string& toId, double amount) {
        std::lock_guard<std::mutex> lock(mutex);
        Account& from = accounts[fromId];
        Account& to = accounts[toId];
        from.debit(amount);
        to.credit(amount);
    }
    
private:
    std::map<std::string, Account> accounts;
    std::mutex mutex;
};
```

### 스레드는 가능한 독립적으로 구현
- 다른 스레드와 자원을 공유하지 않는 스레드 사용 (TLS: Thread Local Storage)
- 스레드 간 통신을 최소화

```cpp
#include <thread>
#include <iostream>

// 스레드 로컬 변수 사용 예
thread_local int userID = 0;

void processRequest(int requestUserID) {
    // 각 스레드마다 독립적인 userID 설정
    userID = requestUserID;
    
    // 처리 로직
    std::cout << "스레드 ID: " << std::this_thread::get_id() 
              << ", 사용자 ID: " << userID << std::endl;
}

int main() {
    // 여러 스레드에서 동시에 다른 사용자 요청 처리
    std::thread t1(processRequest, 1001);
    std::thread t2(processRequest, 1002);
    std::thread t3(processRequest, 1003);
    
    t1.join();
    t2.join();
    t3.join();
    
    return 0;
}
```

## 실행 모델 이해하기

### 주요 용어
- **한정된 자원**: 크기나 숫자가 제한된 자원 (데이터베이스 연결, 읽기/쓰기 버퍼 등)
- **상호 배제**: 한 번에 한 스레드만 공유 자원에 접근 가능하도록 하는 기법
- **기아**: 스레드가 필요한 자원을 계속 얻지 못하는 상태
- **데드락**: 여러 스레드가 서로가 가진 자원을 기다리며 진행하지 못하는 상태
- **라이브락**: 스레드가 계속 동작하지만 진전은 없는 상태

### 모델1: 생산자-소비자
생산자 스레드는 작업을 생성하여 대기열에 추가하고, 소비자 스레드는 대기열에서 작업을 가져와 처리합니다.

```cpp
#include <iostream>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>

template<typename T>
class ThreadSafeQueue {
private:
    std::queue<T> queue;
    std::mutex mutex;
    std::condition_variable cv;  // 하나의 조건 변수만 사용
    size_t max_size;

public:
    ThreadSafeQueue(size_t max_size = 10) : max_size(max_size) {}
    
    // 아이템 추가
    void push(T item) {
        {
            std::unique_lock<std::mutex> lock(mutex);
            // 큐가 가득 찼으면 대기
            cv.wait(lock, [this] { return queue.size() < max_size; });
            
            // 아이템 추가
            queue.push(item);
            std::cout << "생산: " << item << std::endl;
        }
        // 다른 스레드에게 큐 상태가 변경됐음을 알림
        cv.notify_one();
    }
    
    // 아이템 가져오기
    T pop() {
        T item;
        {
            std::unique_lock<std::mutex> lock(mutex);
            // 큐가 비어있으면 대기
            cv.wait(lock, [this] { return !queue.empty(); });
            
            // 아이템 가져오기
            item = queue.front();
            queue.pop();
            std::cout << "소비: " << item << std::endl;
        }
        // 다른 스레드에게 큐 상태가 변경됐음을 알림
        cv.notify_one();
        return item;
    }
};

int main() {
    ThreadSafeQueue<int> queue(5);  // 최대 크기 5인 큐 생성
    
    // 생산자 스레드
    std::thread producer([&queue] {
        for (int i = 0; i < 10; i++) {
            queue.push(i);
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    });
    
    // 소비자 스레드
    std::thread consumer([&queue] {
        for (int i = 0; i < 10; i++) {
            int item = queue.pop();
            std::this_thread::sleep_for(std::chrono::milliseconds(150));
        }
    });
    
    producer.join();
    consumer.join();
    
    return 0;
}
```

### 모델2: 읽기-쓰기
여러 스레드가 읽기 작업을 동시에 수행할 수 있지만, 쓰기 작업은 배타적으로 수행되어야 합니다.

```cpp
#include <shared_mutex>

class ReadWriteData {
public:
    // 읽기 작업: 여러 스레드가 동시에 가능
    int read() const {
        std::shared_lock<std::shared_mutex> lock(mutex);
        return data;
    }
    
    // 쓰기 작업: 한 번에 한 스레드만 가능
    void write(int new_value) {
        std::unique_lock<std::shared_mutex> lock(mutex);
        data = new_value;
    }
    
private:
    int data = 0;
    mutable std::shared_mutex mutex;
};
```

### 모델3: 식사하는 철학자들
원형 테이블에 앉은 철학자들이 각자 왼쪽과 오른쪽의 포크를 모두 집어야 식사가 가능한 모델입니다.

```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <array>
#include <chrono>

const int NUM_PHILOSOPHERS = 5;

class DiningPhilosophers {
public:
    DiningPhilosophers() {
        for (int i = 0; i < NUM_PHILOSOPHERS; i++) {
            fork_status[i] = true; // 모든 포크 사용 가능
        }
    }
    
    void philosopher(int id) {
        int left_fork = id;
        int right_fork = (id + 1) % NUM_PHILOSOPHERS;
        
        // 데드락 방지: 짝수 번호 철학자는 왼쪽 포크부터, 홀수 번호는 오른쪽 포크부터
        if (id % 2 == 0) {
            std::swap(left_fork, right_fork);
        }
        
        for (int i = 0; i < 3; i++) { // 3번 식사
            think(id);
            
            // 첫 번째 포크 집기
            {
                std::lock_guard<std::mutex> lock(mutex);
                while (!fork_status[left_fork]) {
                    std::this_thread::yield();
                }
                fork_status[left_fork] = false;
                std::cout << "철학자 " << id << "가 포크 " << left_fork << "를 집었습니다." << std::endl;
            }
            
            // 두 번째 포크 집기
            {
                std::lock_guard<std::mutex> lock(mutex);
                while (!fork_status[right_fork]) {
                    std::this_thread::yield();
                }
                fork_status[right_fork] = false;
                std::cout << "철학자 " << id << "가 포크 " << right_fork << "를 집었습니다." << std::endl;
            }
            
            eat(id);
            
            // 포크 내려놓기
            {
                std::lock_guard<std::mutex> lock(mutex);
                fork_status[left_fork] = true;
                fork_status[right_fork] = true;
                std::cout << "철학자 " << id << "가 포크를 내려놓았습니다." << std::endl;
            }
        }
    }
    
private:
    std::mutex mutex;
    std::array<bool, NUM_PHILOSOPHERS> fork_status;
    
    void think(int id) {
        std::cout << "철학자 " << id << "가 생각 중입니다." << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    void eat(int id) {
        std::cout << "철학자 " << id << "가 식사 중입니다." << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
};
```

## 동기화하는 메서드 사이의 의존성 관리

공유 객체의 여러 메서드를 호출해야 할 때 세 가지 접근법을 사용할 수 있습니다:

### 1. 클라이언트 측 잠금

```cpp
class BankAccount {
public:
    void deposit(double amount) {
        balance += amount;
    }
    
    bool withdraw(double amount) {
        if (balance >= amount) {
            balance -= amount;
            return true;
        }
        return false;
    }
    
    double getBalance() const {
        return balance;
    }
    
private:
    double balance = 0.0;
};

// 클라이언트 측 잠금 예시
void transferMoney(BankAccount& from, BankAccount& to, double amount, std::mutex& lock) {
    // 클라이언트가 잠금 관리
    std::lock_guard<std::mutex> guard(lock);
    
    if (from.withdraw(amount)) {
        to.deposit(amount);
        std::cout << "이체 성공: " << amount << "원" << std::endl;
    } else {
        std::cout << "이체 실패: 잔액 부족" << std::endl;
    }
}
```

### 2. 서버 측 잠금

```cpp
class BankAccount {
public:
    void deposit(double amount) {
        std::lock_guard<std::mutex> guard(mutex);
        balance += amount;
    }
    
    bool withdraw(double amount) {
        std::lock_guard<std::mutex> guard(mutex);
        if (balance >= amount) {
            balance -= amount;
            return true;
        }
        return false;
    }
    
    double getBalance() const {
        std::lock_guard<std::mutex> guard(mutex);
        return balance;
    }
    
private:
    mutable std::mutex mutex;
    double balance = 0.0;
};

// 서버 측 잠금 사용 예시
void transferMoney(BankAccount& from, BankAccount& to, double amount) {
    // 각 메서드에서 자체적으로 잠금 관리
    if (from.withdraw(amount)) {
        to.deposit(amount);
        std::cout << "이체 성공: " << amount << "원" << std::endl;
    } else {
        std::cout << "이체 실패: 잔액 부족" << std::endl;
    }
}
```

### 3. 적응적 서버

```cpp
class BankAccount {
public:
    void deposit(double amount) {
        std::lock_guard<std::mutex> guard(mutex);
        depositImpl(amount);
    }
    
    bool withdraw(double amount) {
        std::lock_guard<std::mutex> guard(mutex);
        return withdrawImpl(amount);
    }
    
    double getBalance() const {
        std::lock_guard<std::mutex> guard(mutex);
        return balance;
    }
    
    // 복합 작업을 위한 원자적 메서드
    bool transfer(BankAccount& to, double amount) {
        // 두 계좌의 잠금 순서 결정 (데드락 방지)
        BankAccount* first = (this < &to) ? this : &to;
        BankAccount* second = (this < &to) ? &to : this;
        
        std::lock_guard<std::mutex> lock1(first->mutex);
        std::lock_guard<std::mutex> lock2(second->mutex);
        
        if (this->balance >= amount) {
            this->balance -= amount;
            to.balance += amount;
            return true;
        }
        return false;
    }
    
private:
    mutable std::mutex mutex;
    double balance = 0.0;
    
    // 내부 구현 메서드 (잠금 없음)
    void depositImpl(double amount) {
        balance += amount;
    }
    
    bool withdrawImpl(double amount) {
        if (balance >= amount) {
            balance -= amount;
            return true;
        }
        return false;
    }
};
```

## 동기화 부분을 작게 만들기

임계영역이 커질수록 스레드 간 경쟁이 심해지고 성능이 저하됩니다. 따라서 동기화 영역을 최소화해야 합니다.

```cpp
#include <mutex>
#include <vector>
#include <algorithm>

class DataProcessor {
public:
    // 잘못된 예: 전체 메서드에 잠금 적용
    void processBad(const std::vector<int>& inputData) {
        std::lock_guard<std::mutex> lock(mutex);
        
        // 1. 무거운 전처리 작업 (잠금 불필요)
        std::vector<int> processedData;
        for (int value : inputData) {
            // CPU 집약적 연산
            int result = 0;
            for (int i = 0; i < 10000; i++) {
                result += (value * i) % 7;
            }
            processedData.push_back(result);
        }
        
        // 2. 공유 자원 업데이트 (잠금 필요)
        results.insert(results.end(), processedData.begin(), processedData.end());
        
        // 3. 무거운 후처리 작업 (잠금 불필요)
        std::sort(results.begin(), results.end());
    }
    
    // 개선된 예: 필요한 부분만 잠금 적용
    void processGood(const std::vector<int>& inputData) {
        // 1. 무거운 전처리 작업 (잠금 불필요)
        std::vector<int> processedData;
        for (int value : inputData) {
            // CPU 집약적 연산
            int result = 0;
            for (int i = 0; i < 10000; i++) {
                result += (value * i) % 7;
            }
            processedData.push_back(result);
        }
        
        // 2. 공유 자원 업데이트 (잠금 필요)
        {
            std::lock_guard<std::mutex> lock(mutex);
            results.insert(results.end(), processedData.begin(), processedData.end());
        }
        
        // 3. 무거운 후처리 작업 (결과의 로컬 복사본 사용)
        std::vector<int> localResults;
        {
            std::lock_guard<std::mutex> lock(mutex);
            localResults = results;
        }
        std::sort(localResults.begin(), localResults.end());
    }
    
private:
    std::mutex mutex;
    std::vector<int> results;
};
```

## 올바른 종료 코드 구현의 어려움

부모 스레드가 여러 자식 스레드를 생성하고 모든 자식 스레드가 종료될 때까지 기다린 후 자원을 해제하는 시스템에서, 자식 스레드 하나가 데드락에 빠지면 전체 시스템이 블록될 수 있습니다.

```cpp
#include <iostream>
#include <thread>
#include <vector>
#include <mutex>
#include <chrono>
#include <atomic>

class TaskManager {
public:
    TaskManager() : running(true) {}
    
    void start(int numWorkers) {
        std::cout << "작업 관리자 시작..." << std::endl;
        
        // 여러 작업자 스레드 생성
        for (int i = 0; i < numWorkers; i++) {
            workers.push_back(std::thread(&TaskManager::workerFunction, this, i));
        }
    }
    
    ~TaskManager() {
        // 종료 신호 전송
        running = false;
        
        std::cout << "모든 작업자 종료 대기 중..." << std::endl;
        
        // 모든 스레드 종료 대기 - 여기서 문제 발생 가능!
        for (auto& worker : workers) {
            // 스레드 중 하나가 데드락에 빠지면 영원히 대기하게 됨
            if (worker.joinable()) {
                worker.join();
            }
        }
        
        std::cout << "작업 관리자 종료됨" << std::endl;
    }
    
private:
    void workerFunction(int id) {
        std::cout << "작업자 " << id << " 시작" << std::endl;
        
        // 작업자 0은 의도적으로 데드락 발생
        if (id == 0) {
            std::cout << "작업자 0: 데드락 시뮬레이션" << std::endl;
            std::mutex mtx;
            mtx.lock();
            mtx.lock();  // 같은 뮤텍스를 두 번 잠그려 시도 -> 데드락!
        } else {
            // 정상 작동하는 작업자
            while (running) {
                // 작업 수행
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
                std::cout << "작업자 " << id << " 작업 중..." << std::endl;
            }
            std::cout << "작업자 " << id << " 정상 종료" << std::endl;
        }
    }
    
    std::vector<std::thread> workers;
    std::atomic<bool> running;
};

// 위 문제를 해결하기 위한 개선된 버전 - 타임아웃 추가
class TaskManagerImproved {
public:
    TaskManagerImproved() : running(true) {}
    
    void start(int numWorkers) {
        std::cout << "개선된 작업 관리자 시작..." << std::endl;
        
        for (int i = 0; i < numWorkers; i++) {
            workers.push_back(std::thread(&TaskManagerImproved::workerFunction, this, i));
        }
    }
    
    ~TaskManagerImproved() {
        // 종료 신호 전송
        running = false;
        
        std::cout << "모든 작업자 종료 대기 중 (타임아웃 적용)..." << std::endl;
        
        // 각 스레드마다 타임아웃 적용
        for (auto& worker : workers) {
            // detach는 권장되지 않지만 데드락 방지를 위한 마지막 수단
            if (worker.joinable()) {
                std::thread watchdog([&worker]() {
                    auto timeoutPoint = std::chrono::system_clock::now() + std::chrono::seconds(2);
                    if (worker.joinable()) {
                        std::cout << "작업자 스레드 join 시도 중..." << std::endl;
                        worker.join();
                    }
                });
                
                // 워치독 스레드를 detach - 타임아웃 초과 시 프로그램 종료
                watchdog.detach();
                std::this_thread::sleep_for(std::chrono::seconds(3));
            }
        }
        
        std::cout << "작업 관리자 종료됨" << std::endl;
    }
    
private:
    void workerFunction(int id) {
        std::cout << "작업자 " << id << " 시작" << std::endl;
        
        if (id == 0) {
            std::cout << "작업자 0: 데드락 시뮬레이션" << std::endl;
            std::mutex mtx;
            mtx.lock();
            mtx.lock();  // 데드락 발생
        } else {
            while (running) {
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
                std::cout << "작업자 " << id << " 작업 중..." << std::endl;
            }
            std::cout << "작업자 " << id << " 정상 종료" << std::endl;
        }
    }
    
    std::vector<std::thread> workers;
    std::atomic<bool> running;
};
```

## 스레드 코드 테스트하기

동시성 코드는 테스트하기 어렵습니다:
- 문제를 노출하는 테스트 케이스 작성
- 프로그램 설정, 시스템 설정, 부하를 다양하게 변경하며 테스트
- 다양한 환경에서 반복 테스트 필요

```cpp
#include <gtest/gtest.h>
#include <thread>
#include <vector>
#include <mutex>
#include <atomic>

// 테스트 대상 클래스
class Counter {
public:
    void increment() {
        std::lock_guard<std::mutex> lock(mutex);
        value++;
    }
    
    int getValue() const {
        std::lock_guard<std::mutex> lock(mutex);
        return value;
    }
    
private:
    mutable std::mutex mutex;
    int value = 0;
};

// 기본 테스트
TEST(CounterTest, BasicIncrement) {
    Counter counter;
    const int NUM_INCREMENTS = 1000;
    
    for (int i = 0; i < NUM_INCREMENTS; i++) {
        counter.increment();
    }
    
    EXPECT_EQ(counter.getValue(), NUM_INCREMENTS);
}

// 스트레스 테스트 - 여러 스레드에서 동시에 증가
TEST(CounterTest, ConcurrentIncrement) {
    Counter counter;
    const int NUM_THREADS = 10;
    const int INCREMENTS_PER_THREAD = 1000;
    
    std::vector<std::thread> threads;
    for (int i = 0; i < NUM_THREADS; i++) {
        threads.push_back(std::thread([&]() {
            for (int j = 0; j < INCREMENTS_PER_THREAD; j++) {
                counter.increment();
            }
        }));
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    EXPECT_EQ(counter.getValue(), NUM_THREADS * INCREMENTS_PER_THREAD);
}

// 교차 테스트 - 서로 다른 시점에 실행
TEST(CounterTest, InterleavedTest) {
    Counter counter;
    std::atomic<bool> threadADone(false);
    
    // 스레드 A: 증가 500번 수행
    std::thread threadA([&]() {
        for (int i = 0; i < 500; i++) {
            counter.increment();
        }
        threadADone = true;
    });
    
    // 스레드 B: 스레드 A가 절반 정도 진행될 때까지 대기 후 증가 500번 수행
    std::thread threadB([&]() {
        // 스레드 A가 진행되도록 약간 대기
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        
        for (int i = 0; i < 500; i++) {
            counter.increment();
        }
    });
    
    threadA.join();
    threadB.join();
    
    EXPECT_EQ(counter.getValue(), 1000);
}

// 시스템 부하 테스트 - CPU 사용률이 높은 상황에서 동시성 테스트
TEST(CounterTest, HighLoadTest) {
    Counter counter;
    const int NUM_THREADS = 20;
    
    // 시스템에 부하를 주는 스레드들
    std::vector<std::thread> loadThreads;
    for (int i = 0; i < 4; i++) {
        loadThreads.push_back(std::thread([]() {
            std::vector<int> data;
            for (int j = 0; j < 10000000; j++) {
                data.push_back(j);
                if (data.size() > 1000000) data.clear();
            }
        }));
    }
    
    // 테스트 대상 스레드들
    std::vector<std::thread> testThreads;
    for (int i = 0; i < NUM_THREADS; i++) {
        testThreads.push_back(std::thread([&]() {
            for (int j = 0; j < 100; j++) {
                counter.increment();
            }
        }));
    }
    
    for (auto& t : testThreads) {
        t.join();
    }
    
    for (auto& t : loadThreads) {
        t.join();
    }
    
    EXPECT_EQ(counter.getValue(), NUM_THREADS * 100);
}
```

## 동시성 코드 구현 지침

1. **일회성 오류도 넘기지 마라**: 간헐적으로 발생하는 동시성 문제는 무시하지 말고 반드시 해결해야 합니다.

2. **다중 스레드를 고려하지 않은 순차 코드부터 제대로 구현**: 먼저 단일 스레드 코드가 올바르게 동작하는지 확인한 후, 동시성 지원을 추가합니다.

```cpp
// 1. 먼저 기능이 올바르게 작동하는 단일 스레드 코드 작성
class Calculator {
public:
    int add(int a, int b) {
        return a + b;
    }
    
    int subtract(int a, int b) {
        return a - b;
    }
    
    int getLastResult() const {
        return lastResult;
    }
    
    void storeResult(int result) {
        lastResult = result;
    }
    
private:
    int lastResult = 0;
};

// 2. 동시성 지원 추가
class ThreadSafeCalculator {
public:
    int add(int a, int b) {
        int result = calculator.add(a, b);
        std::lock_guard<std::mutex> lock(mutex);
        calculator.storeResult(result);
        return result;
    }
    
    int subtract(int a, int b) {
        int result = calculator.subtract(a, b);
        std::lock_guard<std::mutex> lock(mutex);
        calculator.storeResult(result);
        return result;
    }
    
    int getLastResult() const {
        std::lock_guard<std::mutex> lock(mutex);
        return calculator.getLastResult();
    }
    
private:
    Calculator calculator;
    mutable std::mutex mutex;
};
```

3. **다중 스레드를 쓰는 코드 부분을 다양한 환경에 쉽게 넣을 수 있도록 구현**: 동시성 코드를 모듈화하고 환경에 따라 설정 가능하게 만듭니다.

4. **다중 스레드를 쓰는 코드 부분을 상황에 맞춰 조정할 수 있게 작성**: 스레드 수, 대기열 크기 등을 조정 가능하게 설계합니다.

5. **프로세서 수보다 많은 스레드를 돌려 테스트**: 스레드 간 컨텍스트 전환을 강제하여 잠재적 문제를 발견합니다.

6. **다른 플랫폼에서 돌려 테스트**: 서로 다른 운영 체제, 하드웨어에서 테스트하여 플랫폼 의존적 문제를 발견합니다.

7. **코드에 보조 코드를 넣어 강제로 실패를 유발하는 테스트**: 스레드 스케줄링을 인위적으로 변경하여 경쟁 상태를 발생시키는 테스트를 수행합니다.

```cpp
#include <thread>
#include <atomic>
#include <chrono>

class TestHarness {
public:
    // 스레드 간 경쟁 상태를 강제로 유발하는 도구
    static void forceConcurrencyIssue(int threadId, int point) {
        if (shouldInjectDelay.load()) {
            if (threadId % 2 == 0 && point == injectionPoint) {
                // 짝수 ID 스레드에 지연 주입
                std::this_thread::sleep_for(std::chrono::milliseconds(5));
            }
        }
    }
    
    static void enableDelayInjection(int point) {
        shouldInjectDelay.store(true);
        injectionPoint = point;
    }
    
    static void disableDelayInjection() {
        shouldInjectDelay.store(false);
    }
    
private:
    static std::atomic<bool> shouldInjectDelay;
    static int injectionPoint;
};

std::atomic<bool> TestHarness::shouldInjectDelay(false);
int TestHarness::injectionPoint = 0;

// 사용 예시
void workerWithDebugging(int id, SharedData& data) {
    // 작업 시작
    TestHarness::forceConcurrencyIssue(id, 1);
    
    // 공유 데이터 읽기
    int value = data.getValue();
    TestHarness::forceConcurrencyIssue(id, 2);
    
    // 연산 수행
    value++;
    TestHarness::forceConcurrencyIssue(id, 3);
    
    // 결과 저장
    data.setValue(value);
}
```

이러한 지침을 따르면 동시성 코드의 가독성, 유지보수성, 그리고 무엇보다 정확성을 향상시킬 수 있습니다.



# 클린코드를 넘어서: 최신 동시성 문제 해결 기법

클린코드 13장에서 다루지 않은 여러 고급 동시성 기법들을 소개합니다. 이러한 기술들은 복잡한 멀티스레드 환경에서 발생하는 문제를 효과적으로 해결하는 데 도움이 됩니다.

## CAS(Compare-And-Swap) 연산

CAS는 락 프리 프로그래밍의 기본이 되는 원자적 연산입니다. 메모리의 값을 예상 값과 비교한 후, 일치할 경우에만 새 값으로 교체합니다.

```cpp
#include <atomic>

template <typename T>
bool compare_and_swap(std::atomic<T>& value, T expected, T new_value) {
    // 현재 값이 expected와 같으면 new_value로 교체하고 true 반환
    // 그렇지 않으면 false 반환
    return value.compare_exchange_strong(expected, new_value);
}

// 사용 예시: CAS 기반 스택
template <typename T>
class LockFreeStack {
private:
    struct Node {
        T data;
        Node* next;
    };

    std::atomic<Node*> head{nullptr};

public:
    void push(T value) {
        Node* new_node = new Node{value, nullptr};
        
        Node* old_head;
        do {
            old_head = head.load();
            new_node->next = old_head;
        } while (!head.compare_exchange_weak(old_head, new_node));
        // CAS 실패 시 old_head가 자동으로 업데이트되어 다시 시도
    }

    bool pop(T& result) {
        Node* old_head;
        do {
            old_head = head.load();
            if (!old_head) return false;  // 스택이 비어있음
        } while (!head.compare_exchange_weak(old_head, old_head->next));
        
        result = old_head->data;
        delete old_head;
        return true;
    }
};
```

CAS 연산의 장점:
- 락 없이도 원자적 업데이트 가능
- 데드락 방지
- 높은 병렬성 제공

단점:
- ABA 문제 발생 가능 (값이 A→B→A로 변경되었을 때 변경을 감지하지 못함)
- 반복 시도로 인한 CPU 사용량 증가 가능

## 락 프리(Lock-Free) 프로그래밍

락 프리 프로그래밍은 뮤텍스와 같은 명시적인 잠금 메커니즘을 사용하지 않고도 스레드 안전성을 보장하는 기법입니다. 주로 원자적 연산(atomic operations)을 활용합니다.

```cpp
#include <atomic>

class LockFreeCounter {
private:
    std::atomic<int> count{0};

public:
    void increment() {
        count.fetch_add(1, std::memory_order_relaxed);
    }

    int get() const {
        return count.load(std::memory_order_relaxed);
    }
};
```

락 프리 알고리즘의 장점:
- 데드락 위험 없음
- 스레드 간 경쟁 감소로 성능 향상
- 우선순위 역전 문제 방지

## 메모리 순서(Memory Ordering)

C++11부터 도입된 메모리 순서 지정은 원자적 연산의 가시성(visibility)과 순서(ordering)를 세밀하게 제어할 수 있게 해줍니다.

```cpp
std::atomic<bool> ready{false};
std::atomic<int> data{0};

// 스레드 1
void producer() {
    data.store(42, std::memory_order_release);
    ready.store(true, std::memory_order_release);
}

// 스레드 2
void consumer() {
    while (!ready.load(std::memory_order_acquire)) {
        // 스핀
    }
    // data가 반드시 42임을 보장
    assert(data.load(std::memory_order_acquire) == 42);
}
```

## RCU(Read-Copy-Update)

RCU는 주로 읽기 작업이 많은 데이터 구조에 적합한 동기화 기법입니다. 읽기 작업은 락 없이 진행하고, 쓰기 작업은 데이터의 새 복사본을 만들어 원자적으로 교체합니다.

```cpp
template <typename T>
class RCUPointer {
private:
    std::atomic<T*> ptr;
    std::mutex write_mutex;

public:
    RCUPointer(T* initial = nullptr) : ptr(initial) {}

    // 읽기 - 락 없음
    T* read() const {
        return ptr.load(std::memory_order_acquire);
    }

    // 쓰기 - 새 객체 생성 후 포인터 교체
    void update(T* new_data) {
        std::lock_guard<std::mutex> lock(write_mutex);
        T* old_data = ptr.load(std::memory_order_relaxed);
        ptr.store(new_data, std::memory_order_release);
        
        // 실제 RCU에서는 여기서 grace period를 기다림
        // 그 후 old_data 삭제
    }
};
```

## 하자드 포인터(Hazard Pointers)

메모리 관리 문제를 해결하는 기법으로, 스레드가 특정 메모리 영역을 사용 중임을 표시하여 다른 스레드가 해당 메모리를 해제하지 못하게 합니다.

```cpp
// 간략화된 하자드 포인터 개념
thread_local Node* hazard_pointer = nullptr;

Node* read_node(std::atomic<Node*>& node_ptr) {
    Node* ptr;
    do {
        ptr = node_ptr.load();
        hazard_pointer = ptr;  // 이 노드 사용 중임을 표시
    } while (ptr != node_ptr.load());  // ABA 문제 방지
    
    return ptr;
}

void retire_node(Node* node) {
    // 모든 스레드의 hazard_pointer 검사
    if (어떤_스레드라도_이_노드를_가리키는지_확인(node)) {
        // 나중에 다시 시도
        퇴출_큐에_추가(node);
    } else {
        // 안전하게 삭제 가능
        delete node;
    }
}
```

## MVCC(다중 버전 동시성 제어)

데이터베이스 시스템에서 자주 사용되는 이 기법은 데이터의 여러 버전을 유지하여 읽기 작업이 쓰기 작업을 차단하지 않도록 합니다.

```cpp
template <typename T>
class MVCCObject {
private:
    struct Version {
        T data;
        long long timestamp;
        Version* prev;
    };
    
    std::atomic<Version*> latest_version;
    std::mutex write_mutex;
    std::atomic<long long> global_timestamp{0};

public:
    // 쓰기 - 새 버전 생성
    void write(const T& new_data) {
        std::lock_guard<std::mutex> lock(write_mutex);
        Version* old_version = latest_version.load();
        Version* new_version = new Version{
            new_data,
            global_timestamp.fetch_add(1),
            old_version
        };
        latest_version.store(new_version);
    }

    // 읽기 - 타임스탬프에 따른 버전 선택
    T read(long long read_timestamp = -1) const {
        if (read_timestamp == -1) {
            read_timestamp = global_timestamp.load();
        }
        
        Version* current = latest_version.load();
        while (current && current->timestamp > read_timestamp) {
            current = current->prev;
        }
        
        return current ? current->data : T{};
    }
};
```

이러한 고급 동시성 기법들은 성능, 확장성, 안정성 측면에서 전통적인 락 기반 동기화보다 많은 이점을 제공할 수 있습니다. 다만 구현과 이해가 더 복잡하므로 신중하게 적용해야 합니다.