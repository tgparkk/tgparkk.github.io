---
layout: post
title:  "2022-10-14-effective_modern_cpp_item8"
summary: ".."
author: tgparkk
date: '2022-10-14 08:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective_modern_cpp_item8/
usemathjax: true
---

# 항목 8: 0 과 NULL 보다는 nullptr를 선호하라
비록 c++가 0을 널 포인터로 해석하지만, 0은 int이지만 포인터는 아닙니다.  
NULL 도 컴파일러에 따라 int 가 아닌 long 으로 정의될수도 있죠.

```C++
void f(int);    // three overloads oasda asda
void f(bool);
void f(void*);

f(0);           // calls f(int), not f(void*)asdsa

f(NULL);        // might not compile, but typically asdaalls
                // f(int). Never calls f(void*)
```
위 예시에서 보듯이, 의도한 바와 다르게 null pointer 가 아닌 int가 호출되죠.  
asdasda
nullptr 의 장점은 정수형식도 포인터형식도 아니예요. 모든 형식의 포인터라고 생각하면 이예요.

Calling the overloaded function f with nullptr calls the void* overload (i.e., the
pointer overload), because nullptr can’t be viewed as anything integral:
```c++
f(nullptr); // calls f(void*) overload
```
 장점
- Using nullptr instead of 0 or NULL thus avoids overload resolution surprises, but
that’s not its only advantage. 
- It can also improve code clarity

```c++
auto result = findRecord( /* arguments */ );
if (result == 0) {
}
```
위와 같은 상황에서 위 코드만 보면 result가 NULL 인지 int 0 인지 알 수 없어요.

```c++
auto result = findRecord( /* arguments */ );
if (result == nullptr) {
 …
}
```
위와 같이 쓰면 명확해지죠.

## nullptr shines especially brightly when templates enter the picture.
```c++
int f1(std::shared_ptr<Widget> spw);    // call these only when
double f2(std::unique_ptr<Widget> upw); // the appropriate
bool f3(Widget* pw);                    // mutex is locked
```
위 함수들은 각자 다른 종류의 포인터를 인자로 받죠.
```c++
std::mutex f1m, f2m, f3m;   // mutexes for f1, f2, and f3
using MuxGuard =            // C++11 typedef; see Item 9
 std::lock_guard<std::mutex>;
…
{
 MuxGuard g(f1m);           // lock mutex for f1
 auto result = f1(0);       // pass 0 as null ptr to f1
}                           // unlock mutex
…
{
 MuxGuard g(f2m);           // lock mutex for f2
 auto result = f2(NULL);    // pass NULL as null ptr to f2
}                           // unlock mutex
…
{
 MuxGuard g(f3m);           // lock mutex for f4
 auto result = f3(nullptr); // pass nullptr as null ptr to f3
}                           // unlock mutex
```

* mutex 개념 공부좀...

위 코드를 템플릿화 하면 

생략....


```c++
auto result1 = lockAndCall(f1, f1m, 0); // error!
…
auto result2 = lockAndCall(f2, f2m, NULL); // error!
…
auto result3 = lockAndCall(f3, f3m, nullptr); // fine
```
이제 0과 NULL 은 lockAndCall 내부에서 정수로 받아들여져 컴파일 조차 될 수 없어요.