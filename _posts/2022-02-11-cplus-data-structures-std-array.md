---
layout: post
title:  "C++ DataStructers and Algorithm"
summary: "std::array"
author: tgparkk
date: '2022-02-11 22:30:23 +0530'
category: C++
thumbnail: /assets/img/posts/code.jpg
keywords: C++, DataStructers, Algorithm, Array
permalink: /blog/CPLUS-DataStructures-std-array/
usemathjax: true
---

# 1.2 연속된 자료구조와 연결된 자료구조
자료구조는 크게 연속된 자료구조와 연결된 자료구조로 구분

## 1.2.1 연속된 자료구조
연속된 자료구조(contiguous data structures)는 모든 원소를 단일 메모리 청크(chunk)에 저장합니다.  *메모리 청크는 하나의 연속된 메모리 덩어리를 의미합니다.

```C++
int arr[size]; // 정적 배열
int* arr = (int*)malloc(size * sizeof(int)); // C언어 동적배열
int* arr = new int[size]; // C++ 동적배열

/// 정적배열은 스택(stack) 메모리 영역에 할당되기 때문에 함수를 벗어날 때 자동으로 해제
/// 동적배열은 힙(heap) 영역에 할당되며 사용자가 직접 해제하기 전까지 유지
```

# 1.2.2 연결된 자료구조
연결된 자료 구조(linked data structures) 는 노드라고 하는 여러 개의 메모리 청크에 데이터를 저장한다.

# 1.2.4 C 스타일 배열의 제약 사항
* 메모리 할당과 해제를 수동으로 처리해야 한다.
* [] 연산자에서 배열 크기보다 큰 원소를 참조하는 것을 검사하지 못합니다.
* 배열을 중첩해서 사용할 경우, 문법이 복잡함
* 깊은 복사(deep copy)가 기본으로 동작하지 않습니다. 이러한 동작은 수동으로 구현해야 합니다.

# 1.3 std::array
std::array 는 메모리를 자동으로 할당하고 해제합니다.
원소의 타입과 배열 크기를 매개변수로 사용하는 클래스 템플릿입니다.

```C++
std::array<int, 10> arr1;

arr1[0] = 1;

std::array<int, 4> arr2 = {1,2,3,4};

for(int i=0; i<arr2.size(); i++)
{
    std::cout << arr2[i] << " ";
}
```

std::array 는 배열 원소에 접근할 수 있는 []연산자를 제공합니다. [] 연산자에 접근하고자 하는 배열 원소 인덱스(index)를 지정할 경우, 빠른 동작을 위해 전달된 인덱스 값이 배열의 크기보다 작은지를 검사하지는 않습니다. 대신 std::array는 at(index) 형식의 함수를 제공하며, 이 함수는 인자로 전달된 index 값이 유효하지 않으면 std::out_of_range 예외(exception)를 발생시킵니다.

```C++
std::array<int, 4> arr3 = {1,2,3,4};
try
{
    std::cout << arr3.at(3) << std::endl; // 에러 아님
    std::cout << arr3.at(4) << std::endl; // std::out_of_range 예외 발생
}
catch(const std::out_of_range& ex)
{
    std::cerr << ex.what() << std::endl;
}
```

std::array 객체를 다른 함수에 전달하는 방식은 기본 데이터 타입을 전달하는 것과 유사합니다. 값 또는 참조(reference) 로 전달할 수 있고, const 를 함께 사용할 수도 있습니다.

C 스타일 배열을 함수에 전달할 때처럼 포인터 연산을 사용한다거나 참조 또는 역참조(de-reference) 연산을 하지 않아도 됩니다.

그러므로 다차원 배열을 전달하는 경우에도 std::array를 사용하는 것이 가독성이 훨씬 좋습니다.

```C++
void print(std::array<int, 5> arr)
{
    for(auto ele: arr)
        std::cout << ele << ", ";
}

std::array<int, 5> arr = {1,2,3,4,5};
print(arr);
```

앞 예제의 print() 함수의 매개변수 데이터 타입에 전달받을 배열 크기가 고정되어 있기 때문에 다른 크기의 배열을 전달할 수 없습니다.

만약 다양한 크기의 std::array 객체에 대해 동작하는 범용적인 배열 출력 함수를 만들고 싶다면 print() 를 함수 템플릿으로 선언하고, 배열 크기를 템플릿 매개변수로 전달하면 됩니다. 즉,
```C++
template <size_t N>
void print(const std::array<int, N>& arr);
```
함수에 std::array 객체를 전달할 경우, 기본적으로 새로운 배열에 모든 원소가 복사됩니다. 즉, 자동으로 깊은 복사가 동작합니다. 만약 이러한 동작을 피하고 싶다면 참조 또는 const 참조를 사용할 수 있습니다.


배열의 원소를 차례대로 접근하는 연산은 매우 자주 발생. std::array는 반복자(iterator)와 범위 기반 for(range-based for) 문법을 이용하여 원소에 차례대로 접근할 수 있습니다.

std::array 는 begin() 과 end() 라는 이름의 멤버 함수 제공
begin() 는 첫 번째 원소, end()는 마지막 원소의 다음 위치

```C++
for(auto it = arr.begin(); it!= arr.end(); it++)
{
    auto element = (*it);
    std::cout << element;
}
```

const_iterator 또는 reverse_iterator 같은 형태의 반복자도 사용 가능
const_iterator 는 일반 반복자의 const 버전

* std::array의 원소 접근 함수
|함수|설명|
|---|---|
|front()|배열의 첫 번째 원소에 대한 참조를 반환|
|back()|배열의 마지막 원소에 대한 참조를 반환|
|data()|배열 객체 내부에서 실제 데이터 메모리 버퍼를 가리키는 포인터를 반환합니다.|

```C++
std::array<int, 5> arr = {1,2,3,4,5};
std::cout << arr.front() << std::endl; // 1 출력
std::cout << arr.back() << std::endl; // 5 출력
std::cout << *(arr.data() + 1) << std::endl; // 2 출력
```

* std::array에 대해 관계 연산자를 사용할 경우, 두 배열긔 크기가 같아야 합니다. 이는 std::array로 생성한 배열 객체의 경우, 배열의 크기가 데이터 타입 일부로 동작하기 때문입니다. 즉, 크기가 다른 배열은 서로 다른 타입으로 인식되므로 비교할 수 없습니다.

