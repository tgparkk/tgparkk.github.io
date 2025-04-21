---
layout: post
title: "메모리 풀 : part 2 - 구현 및 성능 분석"
date: 2025-03-16
categories: cpp
tags: [c++, memory-pool, performance, multi-threading, implementation]
excerpt: "메모리 풀의 실제 구현과 성능 분석 결과를 통해 효율성을 검증해봅니다."
comments: true
---

[이전 글](/cpp/2025/03/12/memory-pool-part1.html)에서는 메모리 풀이 필요한 이유와 메모리 단편화 문제에 대해 알아보았습니다. 이번 글에서는 실제 C++에서 메모리 풀을 어떻게 구현하는지, 그리고 그 성능은 어떠한지 분석해보겠습니다.

## 목차
1. [메모리 풀 구현](#1-메모리-풀-구현)
2. [성능 테스트 결과](#2-성능-테스트-결과)
3. [분석 및 결론](#3-분석-및-결론)
4. [고려사항 및 개선 방향](#4-고려사항-및-개선-방향)

## 1. 메모리 풀 구현

### 1.1 메모리 헤더 구조체

먼저 할당된 메모리 블록에 크기 정보를 기록하기 위한 헤더 구조체를 정의합니다.

```cpp
struct MemoryHeader {
    int allocSize;
};

inline void* AttachHeader(MemoryHeader* header, int allocSize) {
    header->allocSize = allocSize;
    // 헤더 바로 뒤의 영역을 사용자에게 반환
    return static_cast<void*>(header + 1);
}

inline MemoryHeader* DetachHeader(void* ptr) {
    return (static_cast<MemoryHeader*>(ptr)) - 1;
}
```

- `MemoryHeader`: 메모리 블록의 크기 정보를 저장하는 간단한 구조체입니다.
- `AttachHeader`: 메모리 헤더에 할당 크기를 설정하고, 실제 사용 가능한 메모리 영역의 포인터를 반환합니다.
- `DetachHeader`: 사용자 데이터 포인터로부터 헤더의 시작 위치를 계산합니다.

이 헤더는 메모리 블록이 해제될 때 어떤 크기의 풀로 돌아가야 하는지를 결정하는 데 사용됩니다.

### 1.2 MemoryPool 클래스

특정 크기의 메모리 블록들을 관리하는 클래스입니다.

```cpp
class MemoryPool {
public:
    // poolSize: 관리할 블록의 크기(헤더 포함X)
    MemoryPool(int poolSize) : _poolSize(poolSize) {}

    ~MemoryPool() {
        for (MemoryHeader* header : _pool)
            _aligned_free(header);
    }

    MemoryHeader* Pop() {
        lock_guard<mutex> lock(_mutex);
        if (!_pool.empty()) {
            MemoryHeader* header = _pool.back();
            _pool.pop_back();
            return header;
        }
        // 풀에 없으면 새로 할당
        MemoryHeader* header = reinterpret_cast<MemoryHeader*>(_aligned_malloc(_poolSize, 16));
        return header;
    }

    void Push(MemoryHeader* header) {
        lock_guard<mutex> lock(_mutex);
        _pool.push_back(header);
    }

private:
    int _poolSize;
    mutex _mutex;
    vector<MemoryHeader*> _pool;
};
```

`MemoryPool` 클래스의 주요 특징:

- **고정 크기 관리**: 각 풀은 특정 크기의 블록만 관리합니다.
- **스레드 안전성**: `mutex`를 사용하여 멀티스레드 환경에서 안전합니다.
- **Pop()**: 풀에서 메모리 블록을 가져오는 메서드입니다. 풀이 비어있으면 새로 할당합니다.
- **Push()**: 사용이 끝난 메모리 블록을 풀에 반환합니다.
- **메모리 정렬**: 16바이트 경계에 정렬된 메모리를 사용하여 성능을 최적화합니다.

### 1.3 Memory 클래스

다양한 크기의 메모리 요청을 처리하기 위해 여러 `MemoryPool`을 관리하는 클래스입니다.

```cpp
class Memory {
public:
    enum { MAX_ALLOC_SIZE = 4096 }; // 최대 관리 크기

    Memory() {
        int currentKey = 0;
        // [1단계] 32 ~ 1024 바이트: 32 단위 증가
        for (int s = 32; s <= 1024; s += 32) {
            MemoryPool* pool = new MemoryPool(s);
            _pools.push_back(pool);
            while (currentKey <= s && currentKey <= MAX_ALLOC_SIZE) {
                _poolTable[currentKey] = pool;
                currentKey++;
            }
        }
        // [2단계] 1024 초과 ~ 2048: 128 단위 증가
        for (int s = 1024 + 128; s <= 2048; s += 128) {
            MemoryPool* pool = new MemoryPool(s);
            _pools.push_back(pool);
            while (currentKey <= s && currentKey <= MAX_ALLOC_SIZE) {
                _poolTable[currentKey] = pool;
                currentKey++;
            }
        }
        // [3단계] 2048 초과 ~ 4096: 256 단위 증가
        for (int s = 2048 + 256; s <= 4096; s += 256) {
            MemoryPool* pool = new MemoryPool(s);
            _pools.push_back(pool);
            while (currentKey <= s && currentKey <= MAX_ALLOC_SIZE) {
                _poolTable[currentKey] = pool;
                currentKey++;
            }
        }
    }

    ~Memory() {
        for (auto pool : _pools)
            delete pool;
        _pools.clear();
    }

    // request: 헤더 제외한 요청 크기
    void* Allocate(int request) {
        int allocSize = request + sizeof(MemoryHeader);
        MemoryHeader* header = nullptr;
        if (allocSize > MAX_ALLOC_SIZE) {
            header = reinterpret_cast<MemoryHeader*>(_aligned_malloc(allocSize, 16));
        }
        else {
            header = _poolTable[allocSize]->Pop();
        }
        return AttachHeader(header, allocSize);
    }

    void Release(void* ptr) {
        MemoryHeader* header = DetachHeader(ptr);
        int allocSize = header->allocSize;
        if (allocSize > MAX_ALLOC_SIZE) {
            _aligned_free(header);
        }
        else {
            _poolTable[allocSize]->Push(header);
        }
    }

private:
    vector<MemoryPool*> _pools;
    MemoryPool* _poolTable[MAX_ALLOC_SIZE + 1];
};
```

`Memory` 클래스의 주요 특징:

- **크기별 풀 관리**:
  - 작은 크기(32~1024바이트): 32바이트 단위로 풀 생성
  - 중간 크기(1024~2048바이트): 128바이트 단위로 풀 생성
  - 큰 크기(2048~4096바이트): 256바이트 단위로 풀 생성
  - 이런 세분화는 메모리 낭비와 관리 오버헤드의 균형을 맞춥니다.

- **빠른 풀 조회**:
  - `_poolTable` 배열을 통해 O(1) 시간에 적절한 풀을 찾을 수 있습니다.
  - 요청 크기에 해당하는 배열 인덱스에 바로 접근하여 해당 풀을 얻습니다.

- **대형 할당 처리**:
  - `MAX_ALLOC_SIZE`(4096바이트)를 초과하는 요청은 일반 메모리 할당(`_aligned_malloc`)을 사용합니다.
  - 이는 매우 큰 요청을 위해 풀을 유지하는 비효율을 방지합니다.

이 구현의 가장 큰 특징은 각 요청 크기에 대해 적절한 풀을 O(1) 시간에 찾는 `_poolTable` 입니다. 이는 전통적인 이진 검색 트리나 리스트를 통한 풀 관리보다 훨씬 효율적입니다.

## 2. 성능 테스트 결과

구현한 메모리 풀의 성능을 검증하기 위해 다양한 크기의 메모리 할당/해제 시나리오에서 테스트를 진행했습니다. 각 테스트는 커스텀 메모리 풀과 표준 C++ `std::vector`를 비교합니다.

### 2.1 단일 스레드 기본 테스트

다양한 크기(32~4096바이트)에 대해 할당, 해제, 총 시간을 측정했습니다.

#### 할당 시간 비교 (단위: 마이크로초, µs)

| 크기   | Custom 할당 | std::vector 할당 | 개선율(%) |
|------:|------------:|------------------:|----------:|
| 32    | 19,617      | 39,632            | 50.5%     |
| 64    | 21,960      | 44,468            | 50.6%     |
| 128   | 35,943      | 62,067            | 42.1%     |
| 256   | 26,532      | 68,984            | 61.5%     |
| 512   | 32,849      | 54,089            | 39.3%     |
| 1024  | 45,931      | 66,716            | 31.2%     |
| 2048  | 74,825      | 97,381            | 23.2%     |
| 4096  | 145,309     | 165,542           | 12.2%     |

#### 해제 시간 비교 (단위: 마이크로초, µs)

| 크기   | Custom 해제 | std::vector 해제 | 개선율(%) |
|------:|------------:|------------------:|----------:|
| 32    | 11,067      | 30,516            | 63.7%     |
| 64    | 12,126      | 40,686            | 70.2%     |
| 128   | 22,293      | 36,469            | 38.9%     |
| 256   | 13,790      | 36,762            | 62.5%     |
| 512   | 15,519      | 40,446            | 61.6%     |
| 1024  | 17,498      | 52,466            | 66.7%     |
| 2048  | 17,474      | 64,563            | 72.9%     |
| 4096  | 64,701      | 98,003            | 34.0%     |

#### 총 시간 비교 (할당 + 해제, 단위: 마이크로초, µs)

| 크기   | Custom 총시간 | std::vector 총시간 | 개선율(%) |
|------:|-------------:|-------------------:|----------:|
| 32    | 30,684       | 70,148             | 56.3%     |
| 64    | 34,086       | 85,154             | 60.0%     |
| 128   | 58,236       | 98,536             | 40.9%     |
| 256   | 40,322       | 105,746            | 61.9%     |
| 512   | 48,368       | 94,535             | 48.8%     |
| 1024  | 63,429       | 119,182            | 46.8%     |
| 2048  | 92,299       | 161,944            | 43.0%     |
| 4096  | 210,010      | 263,545            | 20.3%     |

<!-- ![단일 스레드 총 시간 비교](/assets/images/memory_pool_single_thread_total.png) -->

단일 스레드 환경에서 모든 크기에 대해 커스텀 메모리 풀이 `std::vector`보다 우수한 성능을 보였습니다. 특히 작은 크기(32~256바이트)에서 성능 향상이 더 두드러졌으며, 해제 과정에서 더 큰 성능 차이를 보였습니다.

### 2.2 멀티 스레드 기본 테스트

16개 스레드 환경에서의 성능 비교입니다.

#### 멀티 스레드 총 실행 시간 비교 (단위: 마이크로초, µs)

| 크기   | Custom 총시간 | std::vector 총시간 | 개선율(%) |
|------:|-------------:|-------------------:|----------:|
| 32    | 149,215      | 395,385            | 62.3%     |
| 64    | 112,763      | 401,286            | 71.9%     |
| 128   | 150,903      | 403,629            | 62.6%     |
| 256   | 139,120      | 396,669            | 64.9%     |
| 512   | 111,769      | 414,968            | 73.1%     |
| 1024  | 111,241      | 428,075            | 74.0%     |
| 2048  | 105,083      | 467,433            | 77.5%     |
| 4096  | 287,078      | 556,764            | 48.4%     |

<!-- ![멀티 스레드 총 시간 비교](/assets/images/memory_pool_multi_thread_total.png) -->

멀티 스레드 환경에서는 커스텀 메모리 풀의 성능 우위가 더욱 두드러졌습니다. 대부분의 경우 60~77%의 성능 향상을 보였으며, 특히 2048바이트에서 가장 큰 성능 차이(77.5%)를 보였습니다.

### 2.3 스트레스 테스트

부분 해제 및 재할당을 포함한 스트레스 테스트에서도 커스텀 메모리 풀은 우수한 성능을 보였습니다.

#### 단일 스레드 스트레스 테스트 (단위: 마이크로초, µs)

| 크기   | Custom      | std::vector  | 개선율(%) |
|------:|------------:|--------------:|----------:|
| 32    | 42,363      | 105,945       | 60.0%     |
| 64    | 39,068      | 101,389       | 61.5%     |
| 128   | 43,261      | 96,262        | 55.1%     |
| 256   | 41,289      | 90,209        | 54.2%     |
| 512   | 42,548      | 108,854       | 60.9%     |
| 1024  | 41,221      | 119,736       | 65.6%     |
| 2048  | 40,548      | 160,025       | 74.7%     |
| 4096  | 204,551     | 290,467       | 29.6%     |

<!-- ![단일 스레드 스트레스 테스트](/assets/images/memory_pool_single_thread_stress.png) -->

#### 멀티 스레드 스트레스 테스트 (단위: 마이크로초, µs)

| 크기   | Custom      | std::vector  | 개선율(%) |
|------:|------------:|--------------:|----------:|
| 32    | 85,359      | 275,283       | 69.0%     |
| 64    | 129,766     | 287,603       | 54.9%     |
| 128   | 90,128      | 290,820       | 69.0%     |
| 256   | 86,626      | 291,227       | 70.3%     |
| 512   | 98,199      | 311,558       | 68.5%     |
| 1024  | 105,056     | 335,413       | 68.7%     |
| 2048  | 101,169     | 372,636       | 72.9%     |
| 4096  | 288,918     | 489,047       | 40.9%     |

<!-- ![멀티 스레드 스트레스 테스트](/assets/images/memory_pool_multi_thread_stress.png) -->

스트레스 테스트에서도 커스텀 메모리 풀은 `std::vector`보다 우수한 성능을 보였습니다. 특히 멀티 스레드 환경에서는 더 큰 성능 차이를 보였으며, 이는 시스템 할당자의 경합 상황에서 메모리 풀이 효과적임을 의미합니다.

## 3. 분석 및 결론

### 3.1 주요 성능 분석

1. **할당 성능**:
   - 단일 스레드 환경에서 커스텀 메모리 풀은 `std::vector`보다 할당 시간이 12~62% 개선되었습니다.
   - 작은 크기에서 성능 향상이 더 두드러지는데, 이는 시스템 할당자의 오버헤드가 작은 할당에 더 큰 영향을 미치기 때문입니다.

2. **해제 성능**:
   - 해제 성능은 할당보다 더 큰 차이를 보였으며, 최대 72.9%까지 개선되었습니다.
   - 이는 메모리 풀에서의 해제가 단순한 포인터 조작만으로 이루어지기 때문입니다.

3. **멀티스레드 환경**:
   - 멀티스레드 환경에서 성능 차이가 더 커졌으며, 최대 77.5%까지 개선되었습니다.
   - 이는 시스템 할당자의 경합이 심한 상황에서 메모리 풀의 로컬 관리가 효과적임을 보여줍니다.

4. **스트레스 테스트**:
   - 부분 해제 및 재할당 시나리오에서도 메모리 풀은 우수한 성능을 유지했습니다.
   - 특히 2048바이트 크기에서 단일 스레드 환경에서 74.7%, 멀티스레드 환경에서 72.9%의 성능 향상을 보였습니다.

### 3.2 결론

1. **전반적인 성능 향상**:
   - 모든 테스트 시나리오에서 커스텀 메모리 풀은 `std::vector`보다 우수한 성능을 보였습니다.
   - 평균적으로 단일 스레드 환경에서는 40~60%, 멀티스레드 환경에서는 60~70%의 성능 향상이 있었습니다.

2. **크기별 성능 특성**:
   - 작은 크기(32~256바이트)에서는 할당/해제 오버헤드 감소로 인한 성능 향상이 두드러졌습니다.
   - 큰 크기(2048~4096바이트)에서도 상당한 성능 향상이 있었으나, 상대적으로 작은 크기보다는 효과가 적었습니다.

3. **멀티스레드 효율성**:
   - 멀티스레드 환경에서 성능 차이가 더 커진 것은 메모리 풀이 스레드 간 경합을 줄이는 데 효과적임을 의미합니다.
   - 각 풀별 `mutex`를 사용하여 특정 크기에 대한 경합만 발생하므로, 시스템 할당자의 전역 경합보다 효율적입니다.

4. **활용 가치**:
   - 메모리 할당/해제가 빈번한 애플리케이션에서 메모리 풀은 큰 성능 향상을 가져올 수 있습니다.
   - 특히 네트워크 서버, 게임 엔진, 실시간 시스템 등에서 유용합니다.

## 4. 고려사항 및 개선 방향

### 4.1 현재 구현의 한계점

1. **메모리 오버헤드**:
   - 각 메모리 블록마다 헤더를 추가하므로, 매우 작은 크기의 할당에서는 상대적 오버헤드가 큽니다.
   - 예를 들어, 8바이트 할당 시 헤더(4바이트)는 50%의 오버헤드를 차지합니다.

2. **내부 단편화**:
   - 요청 크기를 올림하여 처리하므로, 일부 메모리가 낭비될 수 있습니다.
   - 예를 들어, 33바이트 요청은 64바이트 풀에서 처리되어 31바이트가 낭비됩니다.

3. **메모리 사용량 예측 어려움**:
   - 사용자가 메모리를 해제해도 실제로는 풀에 반환되므로, 시스템 메모리 사용량은 감소하지 않습니다.
   - 이는 장기 실행 애플리케이션에서 메모리 누수처럼 보일 수 있습니다.

4. **대형 할당 처리**:
   - `MAX_ALLOC_SIZE`(4096바이트)를 초과하는 요청은 표준 할당자를 사용하므로, 일관된 성능 이점을 얻지 못합니다.

### 4.2 개선 방향

1. **스레드별 풀 관리**:
   - 각 스레드가 별도의 로컬 풀을 가지도록 하여 동기화 오버헤드를 더욱 줄일 수 있습니다.
   - 이는 Thread Local Storage(TLS)를 활용하여 구현할 수 있습니다.

2. **동적 메모리 반환**:
   - 사용량이 적은 풀의 메모리를 시스템에 반환하는 전략을 구현하여 메모리 사용량을 최적화할 수 있습니다.
   - 이는 주기적인 가비지 컬렉션이나, 사용률 기반 축소 전략으로 구현할 수 있습니다.

3. **크기 클래스 최적화**:
   - 실제 애플리케이션의 할당 패턴을 분석하여 크기 클래스를 최적화할 수 있습니다.
   - 자주 사용되는 크기에 대해 더 세밀한 풀을 제공하는 것이 효율적입니다.

4. **정렬 옵션 제공**:
   - SIMD 연산 등을 위해 다양한 정렬 옵션을 제공할 수 있습니다.
   - 예를 들어, AVX-512 명령어를 위한 64바이트 정렬 등을 지원할 수 있습니다.

5. **풀 확장성 개선**:
   - 대형 할당을 위한 전용 전략을 구현하여 모든 크기에서 일관된 성능을 제공할 수 있습니다.
   - 이는 큰 블록을 여러 작은 블록으로 관리하거나, 특수 목적 할당자를 개발하는 방식으로 가능합니다.

### 4.3 실제 사용 시 팁

1. **적절한 사용 시나리오**:
   - 작고 균일한 크기의 객체를 빈번하게 할당/해제하는 경우에 가장 효과적입니다.
   - 네트워크 패킷 처리, 게임 엔티티 관리, 이벤트 시스템 등이 좋은 예입니다.

2. **메모리 누수 디버깅**:
   - 메모리 풀을 사용하면 표준 메모리 누수 탐지 도구의 효과가 줄어들 수 있습니다.
   - 사용자 정의 추적 메커니즘을 구현하여 디버깅을 지원하는 것이 좋습니다.

3. **초기화 및 정리**:
   - 객체 할당 시 메모리를 자동으로 초기화하지 않으므로, 보안이 중요한 애플리케이션에서는 추가 초기화 단계가 필요할 수 있습니다.
   - 풀에서 재사용되는 메모리에 민감한 정보가 남아있을 수 있으므로 주의가 필요합니다.

4. **사용자 프로파일링**:
   - 실제 애플리케이션에서 메모리 사용 패턴을 프로파일링하여 풀 크기 및 구성을 최적화하는 것이 좋습니다.

---

이번 글에서는 C++에서 메모리 풀을 구현하는 방법과 그 성능을 분석해보았습니다. 결과적으로 커스텀 메모리 풀은 표준 할당자에 비해 상당한 성능 향상을 제공하며, 특히 멀티스레드 환경과 빈번한 할당/해제가 있는 시나리오에서 더욱 효과적임을 확인했습니다.


<details>
    <summary> 소스 보기 </summary>
{% highlight cpp linenos %}
#include <iostream>
#include <vector>
#include <chrono>
#include <thread>
#include <mutex>
#include <cstdlib>
#include <cstdint>
#include <stdlib.h>  // rand, srand
#include <ctime>     // time

using namespace std;
using namespace std::chrono;

//---------------------------------------------------------------------------
// MemoryHeader: 할당된 메모리 앞에 붙여 할당 크기를 기록합니다.
//---------------------------------------------------------------------------
struct MemoryHeader {
    int allocSize;
};

inline void* AttachHeader(MemoryHeader* header, int allocSize) {
    header->allocSize = allocSize;
    // 헤더 바로 뒤의 영역을 사용자에게 반환
    return static_cast<void*>(header + 1);
}

inline MemoryHeader* DetachHeader(void* ptr) {
    return (static_cast<MemoryHeader*>(ptr)) - 1;
}

//---------------------------------------------------------------------------
// MemoryPool: 단순한 스레드 안전 메모리풀 구현 (_aligned_malloc/_aligned_free 사용)
//---------------------------------------------------------------------------
class MemoryPool {
public:
    // poolSize: 관리할 블록의 크기(헤더 포함X)
    MemoryPool(int poolSize) : _poolSize(poolSize) {}

    ~MemoryPool() {
        for (MemoryHeader* header : _pool)
            _aligned_free(header);
    }

    MemoryHeader* Pop() {
        lock_guard<mutex> lock(_mutex);
        if (!_pool.empty()) {
            MemoryHeader* header = _pool.back();
            _pool.pop_back();
            return header;
        }
        // 풀에 없으면 새로 할당
        MemoryHeader* header = reinterpret_cast<MemoryHeader*>(_aligned_malloc(_poolSize, 16));
        return header;
    }

    void Push(MemoryHeader* header) {
        lock_guard<mutex> lock(_mutex);
        _pool.push_back(header);
    }

private:
    int _poolSize;
    mutex _mutex;
    vector<MemoryHeader*> _pool;
};

//---------------------------------------------------------------------------
// Memory: 여러 MemoryPool을 관리하여 요청 크기에 맞게 할당합니다.
//---------------------------------------------------------------------------

class Memory {
public:
    enum { MAX_ALLOC_SIZE = 4096 }; // 최대 관리 크기

    Memory() {
        int currentKey = 0;
        // [1단계] 32 ~ 1024 바이트: 32 단위 증가
        for (int s = 32; s <= 1024; s += 32) {
            MemoryPool* pool = new MemoryPool(s);
            _pools.push_back(pool);
            while (currentKey <= s && currentKey <= MAX_ALLOC_SIZE) {
                _poolTable[currentKey] = pool;
                currentKey++;
            }
        }
        // [2단계] 1024 초과 ~ 2048: 128 단위 증가
        for (int s = 1024 + 128; s <= 2048; s += 128) {
            MemoryPool* pool = new MemoryPool(s);
            _pools.push_back(pool);
            while (currentKey <= s && currentKey <= MAX_ALLOC_SIZE) {
                _poolTable[currentKey] = pool;
                currentKey++;
            }
        }
        // [3단계] 2048 초과 ~ 4096: 256 단위 증가
        for (int s = 2048 + 256; s <= 4096; s += 256) {
            MemoryPool* pool = new MemoryPool(s);
            _pools.push_back(pool);
            while (currentKey <= s && currentKey <= MAX_ALLOC_SIZE) {
                _poolTable[currentKey] = pool;
                currentKey++;
            }
        }
    }

    ~Memory() {
        for (auto pool : _pools)
            delete pool;
        _pools.clear();
    }

    // request: 헤더 제외한 요청 크기
    void* Allocate(int request) {
        int allocSize = request + sizeof(MemoryHeader);
        MemoryHeader* header = nullptr;
        if (allocSize > MAX_ALLOC_SIZE) {
            header = reinterpret_cast<MemoryHeader*>(_aligned_malloc(allocSize, 16));
        }
        else {
            header = _poolTable[allocSize]->Pop();
        }
        return AttachHeader(header, allocSize);
    }

    void Release(void* ptr) {
        MemoryHeader* header = DetachHeader(ptr);
        int allocSize = header->allocSize;
        if (allocSize > MAX_ALLOC_SIZE) {
            _aligned_free(header);
        }
        else {
            _poolTable[allocSize]->Push(header);
        }
    }

private:
    vector<MemoryPool*> _pools;
    MemoryPool* _poolTable[MAX_ALLOC_SIZE + 1];
};

Memory* gMemory = nullptr;

//---------------------------------------------------------------------------
// 시간 측정 유틸리티 (마이크로초 단위)
//---------------------------------------------------------------------------
template <typename Func>
long long measureTime(Func f) {
    auto start = high_resolution_clock::now();
    f();
    auto end = high_resolution_clock::now();
    return duration_cast<microseconds>(end - start).count();
}

const int ITERATIONS = 100000;

//---------------------------------------------------------------------------
// [기본 테스트] 단일 스레드 테스트: custom allocator
//---------------------------------------------------------------------------
void testCustomAllocatorSingleThread(int size) {
    vector<void*> allocated;
    allocated.reserve(ITERATIONS);

    long long allocTime = measureTime([&]() {
        for (int i = 0; i < ITERATIONS; i++) {
            void* ptr = gMemory->Allocate(size);
            allocated.push_back(ptr);
        }
        });

    long long deallocTime = measureTime([&]() {
        for (auto ptr : allocated) {
            gMemory->Release(ptr);
        }
        });

    long long combinedTime = measureTime([&]() {
        for (int i = 0; i < ITERATIONS; i++) {
            void* ptr = gMemory->Allocate(size);
            gMemory->Release(ptr);
        }
        });

    cout << "== Custom Allocator (Size " << size << ") Single-thread ==" << endl;
    cout << " Allocation: " << allocTime << " µs" << endl;
    cout << " Deallocation: " << deallocTime << " µs" << endl;
    cout << " Combined (alloc+dealloc): " << combinedTime << " µs" << endl;
    cout << " Total (alloc + dealloc): " << (allocTime + deallocTime) << " µs" << endl;
    cout << endl;
}

//---------------------------------------------------------------------------
// [기본 테스트] 단일 스레드 테스트: std::vector 이용
//---------------------------------------------------------------------------
void testStdVectorSingleThread(int size) {
    vector<vector<char>*> allocated;
    allocated.reserve(ITERATIONS);

    long long allocTime = measureTime([&]() {
        for (int i = 0; i < ITERATIONS; i++) {
            vector<char>* vec = new vector<char>(size);
            allocated.push_back(vec);
        }
        });

    long long deallocTime = measureTime([&]() {
        for (auto vec : allocated) {
            delete vec;
        }
        });

    long long combinedTime = measureTime([&]() {
        for (int i = 0; i < ITERATIONS; i++) {
            vector<char>* vec = new vector<char>(size);
            delete vec;
        }
        });

    cout << "== std::vector Allocator (Size " << size << ") Single-thread ==" << endl;
    cout << " Allocation: " << allocTime << " µs" << endl;
    cout << " Deallocation: " << deallocTime << " µs" << endl;
    cout << " Combined (alloc+dealloc): " << combinedTime << " µs" << endl;
    cout << " Total (alloc + dealloc): " << (allocTime + deallocTime) << " µs" << endl;
    cout << endl;
}

//---------------------------------------------------------------------------
// [기본 테스트] 멀티 스레드 테스트용 결과 구조체 및 함수
//---------------------------------------------------------------------------
struct ThreadResult {
    long long allocTime;
    long long deallocTime;
    long long combinedTime;
};

void customAllocatorThread(int size, int iterations, ThreadResult& result) {
    vector<void*> allocated;
    allocated.reserve(iterations);

    result.allocTime = measureTime([&]() {
        for (int i = 0; i < iterations; i++) {
            void* ptr = gMemory->Allocate(size);
            allocated.push_back(ptr);
        }
        });

    result.deallocTime = measureTime([&]() {
        for (auto ptr : allocated)
            gMemory->Release(ptr);
        });

    result.combinedTime = measureTime([&]() {
        for (int i = 0; i < iterations; i++) {
            void* ptr = gMemory->Allocate(size);
            gMemory->Release(ptr);
        }
        });
}

void stdVectorThread(int size, int iterations, ThreadResult& result) {
    vector<vector<char>*> allocated;
    allocated.reserve(iterations);

    result.allocTime = measureTime([&]() {
        for (int i = 0; i < iterations; i++) {
            vector<char>* vec = new vector<char>(size);
            allocated.push_back(vec);
        }
        });

    result.deallocTime = measureTime([&]() {
        for (auto vec : allocated)
            delete vec;
        });

    result.combinedTime = measureTime([&]() {
        for (int i = 0; i < iterations; i++) {
            vector<char>* vec = new vector<char>(size);
            delete vec;
        }
        });
}

void testCustomAllocatorMultiThread(int size, int numThreads) {
    vector<thread> threads;
    vector<ThreadResult> results(numThreads);
    int iterationsPerThread = ITERATIONS / numThreads;

    auto start = high_resolution_clock::now();
    for (int i = 0; i < numThreads; i++) {
        threads.emplace_back(customAllocatorThread, size, iterationsPerThread, ref(results[i]));
    }
    for (auto& t : threads)
        t.join();
    auto end = high_resolution_clock::now();
    long long overallElapsed = duration_cast<microseconds>(end - start).count();

    long long totalAlloc = 0, totalDealloc = 0, totalCombined = 0;
    for (const auto& r : results) {
        totalAlloc += r.allocTime;
        totalDealloc += r.deallocTime;
        totalCombined += r.combinedTime;
    }

    cout << "== Custom Allocator (Size " << size << ") Multi-thread (" << numThreads << " threads) ==" << endl;
    cout << " Total Allocation (sum): " << totalAlloc << " µs" << endl;
    cout << " Total Deallocation (sum): " << totalDealloc << " µs" << endl;
    cout << " Total Combined (sum): " << totalCombined << " µs" << endl;
    cout << " Overall elapsed time: " << overallElapsed << " µs" << endl;
    cout << endl;
}

void testStdVectorMultiThread(int size, int numThreads) {
    vector<thread> threads;
    vector<ThreadResult> results(numThreads);
    int iterationsPerThread = ITERATIONS / numThreads;

    auto start = high_resolution_clock::now();
    for (int i = 0; i < numThreads; i++) {
        threads.emplace_back(stdVectorThread, size, iterationsPerThread, ref(results[i]));
    }
    for (auto& t : threads)
        t.join();
    auto end = high_resolution_clock::now();
    long long overallElapsed = duration_cast<microseconds>(end - start).count();

    long long totalAlloc = 0, totalDealloc = 0, totalCombined = 0;
    for (const auto& r : results) {
        totalAlloc += r.allocTime;
        totalDealloc += r.deallocTime;
        totalCombined += r.combinedTime;
    }

    cout << "== std::vector Allocator (Size " << size << ") Multi-thread (" << numThreads << " threads) ==" << endl;
    cout << " Total Allocation (sum): " << totalAlloc << " µs" << endl;
    cout << " Total Deallocation (sum): " << totalDealloc << " µs" << endl;
    cout << " Total Combined (sum): " << totalCombined << " µs" << endl;
    cout << " Overall elapsed time: " << overallElapsed << " µs" << endl;
    cout << endl;
}

//---------------------------------------------------------------------------
// [추가 스트레스 테스트] 
// 1. 일부 해제 후 재할당: 단일 스레드
//---------------------------------------------------------------------------
void testStressCustomAllocatorSingleThread(int size) {
    vector<void*> allocated;
    allocated.reserve(ITERATIONS);

    long long initialAllocTime = measureTime([&]() {
        for (int i = 0; i < ITERATIONS; i++) {
            allocated.push_back(gMemory->Allocate(size));
        }
        });

    long long partialFreeTime = measureTime([&]() {
        // 전체의 약 1/3을 해제 (매 3번째)
        for (int i = 0; i < ITERATIONS; i += 3) {
            gMemory->Release(allocated[i]);
            allocated[i] = nullptr;
        }
        });

    long long reAllocTime = measureTime([&]() {
        // 해제된 슬롯에 대해 재할당
        for (int i = 0; i < ITERATIONS; i += 3) {
            allocated[i] = gMemory->Allocate(size);
        }
        });

    long long finalFreeTime = measureTime([&]() {
        for (int i = 0; i < ITERATIONS; i++) {
            gMemory->Release(allocated[i]);
        }
        });

    cout << "== Custom Allocator Stress Test (Size " << size << ") Single-thread ==" << endl;
    cout << " Initial Allocation: " << initialAllocTime << " µs" << endl;
    cout << " Partial Free (every 3rd): " << partialFreeTime << " µs" << endl;
    cout << " Re-allocation: " << reAllocTime << " µs" << endl;
    cout << " Final Free: " << finalFreeTime << " µs" << endl;
    cout << " Total Stress Test Time: " << (initialAllocTime + partialFreeTime + reAllocTime + finalFreeTime) << " µs" << endl;
    cout << endl;
}

void testStressStdVectorSingleThread(int size) {
    vector<vector<char>*> allocated;
    allocated.reserve(ITERATIONS);

    long long initialAllocTime = measureTime([&]() {
        for (int i = 0; i < ITERATIONS; i++) {
            allocated.push_back(new vector<char>(size));
        }
        });

    long long partialFreeTime = measureTime([&]() {
        for (int i = 0; i < ITERATIONS; i += 3) {
            delete allocated[i];
            allocated[i] = nullptr;
        }
        });

    long long reAllocTime = measureTime([&]() {
        for (int i = 0; i < ITERATIONS; i += 3) {
            allocated[i] = new vector<char>(size);
        }
        });

    long long finalFreeTime = measureTime([&]() {
        for (int i = 0; i < ITERATIONS; i++) {
            delete allocated[i];
        }
        });

    cout << "== std::vector Stress Test (Size " << size << ") Single-thread ==" << endl;
    cout << " Initial Allocation: " << initialAllocTime << " µs" << endl;
    cout << " Partial Free (every 3rd): " << partialFreeTime << " µs" << endl;
    cout << " Re-allocation: " << reAllocTime << " µs" << endl;
    cout << " Final Free: " << finalFreeTime << " µs" << endl;
    cout << " Total Stress Test Time: " << (initialAllocTime + partialFreeTime + reAllocTime + finalFreeTime) << " µs" << endl;
    cout << endl;
}

//---------------------------------------------------------------------------
// [추가 테스트] 혼합 크기 스트레스 테스트 (단일 스레드, custom allocator)
// 여러 크기를 랜덤하게 선택하여 할당/해제하여 단편화 현상을 관찰할 수 있습니다.
void testMixedSizeStressSingleThread() {
    vector<int> sizes = { 32, 64, 128, 256, 512, 1024, 2048, 4096 };
    vector<void*> allocated;
    allocated.reserve(ITERATIONS);

    long long initialAllocTime = measureTime([&]() {
        for (int i = 0; i < ITERATIONS; i++) {
            int idx = rand() % sizes.size();
            void* ptr = gMemory->Allocate(sizes[idx]);
            allocated.push_back(ptr);
        }
        });

    long long partialFreeTime = measureTime([&]() {
        for (int i = 0; i < ITERATIONS; i++) {
            if (rand() % 100 < 30) { // 약 30% 해제
                gMemory->Release(allocated[i]);
                allocated[i] = nullptr;
            }
        }
        });

    long long reAllocTime = measureTime([&]() {
        for (int i = 0; i < ITERATIONS; i++) {
            if (allocated[i] == nullptr) {
                int idx = rand() % sizes.size();
                allocated[i] = gMemory->Allocate(sizes[idx]);
            }
        }
        });

    long long finalFreeTime = measureTime([&]() {
        for (int i = 0; i < ITERATIONS; i++) {
            gMemory->Release(allocated[i]);
        }
        });

    long long totalTime = initialAllocTime + partialFreeTime + reAllocTime + finalFreeTime;
    cout << "== Custom Allocator Mixed Size Stress Test Single-thread ==" << endl;
    cout << " Initial Allocation: " << initialAllocTime << " µs" << endl;
    cout << " Partial Free: " << partialFreeTime << " µs" << endl;
    cout << " Re-allocation: " << reAllocTime << " µs" << endl;
    cout << " Final Free: " << finalFreeTime << " µs" << endl;
    cout << " Total Time: " << totalTime << " µs" << endl;
    cout << endl;
}

//---------------------------------------------------------------------------
// [멀티 스레드 스트레스 테스트] 결과 구조체 및 함수
//---------------------------------------------------------------------------
struct ThreadStressResult {
    long long initialAllocTime;
    long long partialFreeTime;
    long long reAllocTime;
    long long finalFreeTime;
};

void customAllocatorStressThread(int size, int iterations, ThreadStressResult& result) {
    vector<void*> allocated;
    allocated.reserve(iterations);

    result.initialAllocTime = measureTime([&]() {
        for (int i = 0; i < iterations; i++) {
            allocated.push_back(gMemory->Allocate(size));
        }
        });

    result.partialFreeTime = measureTime([&]() {
        for (int i = 0; i < iterations; i += 3) {
            gMemory->Release(allocated[i]);
            allocated[i] = nullptr;
        }
        });

    result.reAllocTime = measureTime([&]() {
        for (int i = 0; i < iterations; i += 3) {
            allocated[i] = gMemory->Allocate(size);
        }
        });

    result.finalFreeTime = measureTime([&]() {
        for (int i = 0; i < iterations; i++) {
            gMemory->Release(allocated[i]);
        }
        });
}

void stdVectorStressThread(int size, int iterations, ThreadStressResult& result) {
    vector<vector<char>*> allocated;
    allocated.reserve(iterations);

    result.initialAllocTime = measureTime([&]() {
        for (int i = 0; i < iterations; i++) {
            allocated.push_back(new vector<char>(size));
        }
        });

    result.partialFreeTime = measureTime([&]() {
        for (int i = 0; i < iterations; i += 3) {
            delete allocated[i];
            allocated[i] = nullptr;
        }
        });

    result.reAllocTime = measureTime([&]() {
        for (int i = 0; i < iterations; i += 3) {
            allocated[i] = new vector<char>(size);
        }
        });

    result.finalFreeTime = measureTime([&]() {
        for (int i = 0; i < iterations; i++) {
            delete allocated[i];
        }
        });
}

void testCustomAllocatorStressMultiThread(int size, int numThreads) {
    vector<thread> threads;
    vector<ThreadStressResult> results(numThreads);
    int iterationsPerThread = ITERATIONS / numThreads;

    auto start = high_resolution_clock::now();
    for (int i = 0; i < numThreads; i++) {
        threads.emplace_back(customAllocatorStressThread, size, iterationsPerThread, ref(results[i]));
    }
    for (auto& t : threads)
        t.join();
    auto end = high_resolution_clock::now();
    long long overallElapsed = duration_cast<microseconds>(end - start).count();

    long long totalInitial = 0, totalPartial = 0, totalReAlloc = 0, totalFinal = 0;
    for (const auto& r : results) {
        totalInitial += r.initialAllocTime;
        totalPartial += r.partialFreeTime;
        totalReAlloc += r.reAllocTime;
        totalFinal += r.finalFreeTime;
    }

    cout << "== Custom Allocator Stress Test (Size " << size << ") Multi-thread (" << numThreads << " threads) ==" << endl;
    cout << " Total Initial Allocation: " << totalInitial << " µs" << endl;
    cout << " Total Partial Free: " << totalPartial << " µs" << endl;
    cout << " Total Re-allocation: " << totalReAlloc << " µs" << endl;
    cout << " Total Final Free: " << totalFinal << " µs" << endl;
    cout << " Overall elapsed time: " << overallElapsed << " µs" << endl;
    cout << endl;
}

void testStdVectorStressMultiThread(int size, int numThreads) {
    vector<thread> threads;
    vector<ThreadStressResult> results(numThreads);
    int iterationsPerThread = ITERATIONS / numThreads;

    auto start = high_resolution_clock::now();
    for (int i = 0; i < numThreads; i++) {
        threads.emplace_back(stdVectorStressThread, size, iterationsPerThread, ref(results[i]));
    }
    for (auto& t : threads)
        t.join();
    auto end = high_resolution_clock::now();
    long long overallElapsed = duration_cast<microseconds>(end - start).count();

    long long totalInitial = 0, totalPartial = 0, totalReAlloc = 0, totalFinal = 0;
    for (const auto& r : results) {
        totalInitial += r.initialAllocTime;
        totalPartial += r.partialFreeTime;
        totalReAlloc += r.reAllocTime;
        totalFinal += r.finalFreeTime;
    }

    cout << "== std::vector Stress Test (Size " << size << ") Multi-thread (" << numThreads << " threads) ==" << endl;
    cout << " Total Initial Allocation: " << totalInitial << " µs" << endl;
    cout << " Total Partial Free: " << totalPartial << " µs" << endl;
    cout << " Total Re-allocation: " << totalReAlloc << " µs" << endl;
    cout << " Total Final Free: " << totalFinal << " µs" << endl;
    cout << " Overall elapsed time: " << overallElapsed << " µs" << endl;
    cout << endl;
}

//---------------------------------------------------------------------------
// main: 전역 메모리 객체 초기화 및 각 테스트 실행
//---------------------------------------------------------------------------
int main() {
    srand((unsigned)time(NULL));

    // 전역 메모리 풀 생성
    gMemory = new Memory();

    vector<int> testSizes = { 32, 64, 128, 256, 512, 1024, 2048, 4096 };
    int numThreads = thread::hardware_concurrency();
    if (numThreads == 0)
        numThreads = 4;

    cout << "===== Single-thread Basic Tests =====" << endl;
    for (int size : testSizes) {
        testCustomAllocatorSingleThread(size);
        testStdVectorSingleThread(size);
        cout << "---------------------------------" << endl;
    }

    cout << "\n===== Multi-thread Basic Tests =====" << endl;
    for (int size : testSizes) {
        testCustomAllocatorMultiThread(size, numThreads);
        testStdVectorMultiThread(size, numThreads);
        cout << "---------------------------------" << endl;
    }

    cout << "\n===== Single-thread Stress Tests =====" << endl;
    for (int size : testSizes) {
        testStressCustomAllocatorSingleThread(size);
        testStressStdVectorSingleThread(size);
        cout << "---------------------------------" << endl;
    }

    cout << "\n===== Multi-thread Stress Tests =====" << endl;
    for (int size : testSizes) {
        testCustomAllocatorStressMultiThread(size, numThreads);
        testStdVectorStressMultiThread(size, numThreads);
        cout << "---------------------------------" << endl;
    }

    cout << "\n===== Mixed Size Stress Test (Custom Allocator) Single-thread =====" << endl;
    testMixedSizeStressSingleThread();

    delete gMemory;

    return 0;
}
{% endhighlight %}
</details>```


## 참고 자료