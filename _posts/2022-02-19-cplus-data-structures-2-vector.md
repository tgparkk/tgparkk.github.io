---
layout: post
title:  "C++ DataStructers and Algorithm"
summary: "std::vectir"
author: tgparkk
date: '2022-02-19 00:58:23 +0530'
category: C++
thumbnail: /assets/img/posts/code.jpg
keywords: C++, DataStructers, Algorithm, vector
permalink: /blog/CPLUS-DataStructures-std-vector/
usemathjax: true
---

## 1.4.1 std::vector 가변 크기 배열

```c++
//크기가 0인 벡터 선언
std::vector<int> vec;

//지정한 초깃값으로 이루어진 크기가 5인 벡터 선언
std::vector<int> vec = {1,2,3,4,5};

//크키가 10인 벡터 선언
std::vector<int> vec(10);

//크기가 10이고, 모든 원소가 5로 초기화된 벡터 선언
std::vector<int> vec(10,5);

```

## 원소 삽입

```c++
vec.insert(vec.begin(), 0); //맨 앞에 원소 추가

std::vector<int> vec; // 비어 있는 벡터 생성 : {}

vec.push_back(1); // 맨 뒤에 1 추가 : {1}

vec.push_back(2); // 맨 뒤에 2 추가 : {1,2}

vec.insert(vec.begin(), 0); //맨 앞에 0 추가 : {0,1,2}

vec.insert( find(vec.begin(), vec.end(), 1), 4);
// 1 앞에 4추가 : {0, 4, 1, 2}
```

push_back() 또는 insert() 함수와 비교하여 좀 더 효율적인 원소 추가 방법에 대해 알아보겠습니다.

push_back() 또는 insert() 함수의 단점 중 하나는 이들 함수가 추가할 원소를 먼저 임시로 생성한 후, 벡터 버퍼 내부 위치로 복사 또는 이동을 수행한다는 점입니다.

이러한 단점은 새로운 원소가 추가될 위치에서 해당 원소를 생성하는 방식으로 최적화할 수 있으며, 이러한 기능이 emplace_back() 또는 emplace() 함수에 구현되어 있습니다.

이 경우 새 원소 위치에서 곧바로 객체가 생성되기 때문에 이들 함수 인자에 생성된 객체를 전달하는 것이 아니라 생성자에 필요한 매개변수를 전달해야 합니다.

## 원소 제거

pop_back() 함수는 남아 있는 위치 조정 필요 X -> O(1)

erase() 함수는 특정 위치 원소를 삭제한 후, 뒤쪽의 원소들을 모두 앞으로 이동해야 하기 때문에 O(n) 의 시간 소요

```c++
std::vector<int> vec = {0,1,2,3,4,5,6,7,8,9};

//맨 마지막 원소 하나를 제거합니다.
//{0,1,2,3,4,5,6,7,8}
vec.pop_back();

//맨 처음 원소를 제거합니다.
//{1,2,3,4,5,6,7,8}
vec.erase(vec.begin());

//1번째 원소부터 4번째 앞 원소까지 제거합니다.
//{1,5,6,7,8}
vec.erase(vec.begin() + 1, vec.begin() + 4);
```

## 몇가지 std::vector 의 멤버 함수

### cleare() : 모든 원소를 제거하여 완전히 비어 있는 벡터로 만듭니다.

### reserve(capacity) : 벡터에서 사용할 용량을 지정, 매개변수가 현재 용량보다 크면 메모리를 매개변수 크기만큼 재할당, 같거나 작으면 동작 X, 이 함수는 벡터의 크기를 변경하지 않는다.

### shrink_to_fit() : 여분의 메모리 공간을 해제하는 용도로 사용, 이 함수를 호출하면 벡터의 용량이 벡터 크기와 같게 설정. 벡터 크기가 더 이상 변경되지 않을 때 사용하면 유용합니다.

