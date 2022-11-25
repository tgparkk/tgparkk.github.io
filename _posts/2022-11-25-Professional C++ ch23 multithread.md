---
layout: post
title:  "2022-11-25-Professional C++ ch23 multithread"
summary: ".."
author: tgparkk
date: '2022-11-25 18:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/Professional C++ ch23 multithread/
usemathjax: true
---

# C++ 멀티스레드 프로그래밍

여러 스레드가 공유 메모리를 동시에 읽거나 쓰지 않도록 디자인해야 합니다!!!

### 1.1 경쟁 상태
여러 스레드가 공유 리소스를 동시에 접근할 때 *경쟁 상태* 가 발생할 수 있다.  
그중에서도 공유메모리에 대한 경쟁 상태를 흔히 *데이터 경쟁* 이라 부른다.  
(예전 아키텍처는 아토믹하게 실행되는(주어진 시점에 혼자서만 실행되는) 경우도 있긴 했어요.)

### 1.2 테어링
테어링*tearing* 이란 데이터 경쟁의 특수한 경우로서, 크게 읽기 테어링(torn read) 과 쓰기 테어링(torn write) 의 두 가지가 있어요.  

어떤 스레드가 메모리에 데이터의 일부만 쓰고 나머지 부분을 미처 쓰지 못한 상태에서 다른 스레드가 이 데이터를 읽으면 두 스레드가 보는 값이 달라집니다. <- 읽기 테어링  

두 스레드가 이 데이터에 동시에 쓸 때 한 스레드는 그 데이터의 한쪽 부분을 쓰고, 다른 스레드는 그 데이터의 다른 부분을 썼다면 각자 수행한 결과가 달라져요. <- 쓰기 테어링  

## 23.2 스레드

### 전역함수를 스레드로 사용하는 예시
```c++
#include <thread>

// 쓰레드 함수
void workerThread()
{
	// 쓰레드 작업 코드
}

void main()
{
  std::thread t(workerThread);
  ...
  t.join(); // 쓰레드 종료 시까지 대기
}
```

### 전역함수에 파라미터 넣는 방법
```c++
#include <iostream>
#include <thread>

void threadfunction1()
{
	std::cout << "ThreadFuntion1"<< std::endl;
}

void threadfunction2(int n)
{
	std::this_thread::sleep_for(100ms);
	std::cout << "ThreadFuntion2 => N:"<<n << std::endl;
}

void threadfunction3(int n, int tid)
{
	std::this_thread::sleep_for(150ms);
	std::cout << "ThreadFuntion3 => N:" << n <<", tId:"<<tid<< std::endl;
}

int main()
{
	std::thread t1(threadfunction1);
	std::thread t2(threadfunction2, 10);
	std::thread t3 = std::thread(threadfunction3, 10, 2);

	t1.join();
	t2.join();
	t3.join();

	return 0;
}
```

```c++
#include <iostream>
#include <thread>

class ThreadTest
{
public:
	static void ThreadFunc(int n) {
		std::cout << "ThreadFunc is calling..., n:"<<n << std::endl;
	}
	
	void ThreadFunc2(int n) {
		this_thread::sleep_for(100ms);
		std::cout << "ThreadFunc2 is calling..., n:" << n << std::endl;
	}
};

int main()
{
	// 클래스 내 static 함수 호출 시
	std::thread t1(ThreadTest::ThreadFunc, 10);
	// 클래스 내 함수 호출 시, 두번째 인자에는 클래스 객체 전달 필요함
	std::thread t2(&ThreadTest::ThreadFunc2, ThreadTest(), 20);

	t1.join();
	t2.join();

	return 0;
}
```