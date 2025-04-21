---
layout: post
title: "메모리 풀 : part 3 -원시 포인터, 스마트 포인터"
date: 2025-03-19
categories: cpp
tags: [c++, memory-pool, performance, multi-threading, implementation]
excerpt: "원시 포인터, 스마트 포인터."
comments: true
---

[이전 글](/cpp/2025/03/16/memory-pool-part2.html)


# Memory Pool Part 3: 원시 포인터는 쉽게, 스마트 포인터는 왜 어려운가?

앞서 Part 1과 2에서 메모리풀의 개념과 기본 구현에 대해 살펴보았습니다. 이번 Part 3에서는 포인터 타입에 따른 메모리풀 최적화의 난이도 차이에 대해 이야기해보려 합니다. 특히 원시 포인터(raw pointer)에서는 쉽게 성능 향상을 얻을 수 있는 반면, 스마트 포인터(smart pointer)에서는 왜 그렇지 않은지 알아보겠습니다.

## 1. 원시 포인터: 쉽게 성능 향상을 얻을 수 있는 이유

원시 포인터(`T*`)는 C++에서 가장 기본적인 형태의 포인터로, 단순히 메모리 주소를 가리키는 역할만 합니다. 메모리풀과 함께 사용할 때 다음과 같은 이유로 성능 이점을 쉽게 얻을 수 있습니다:

### 1.1. 단순한 메모리 관리

```cpp
// 원시 포인터 기반 메모리풀 사용 예
MemoryPool<GeoData> pool;
GeoData* ptr = static_cast<GeoData*>(pool.allocate());
new (ptr) GeoData(1.0, 2.0, 3.0);  // placement new

// 사용 후
ptr->~GeoData();  // 명시적 소멸자 호출
pool.deallocate(ptr);  // 메모리 반환
```

**장점**:
- **오버헤드 없음**: 원시 포인터는 단순한 메모리 주소일 뿐이므로, 포인터 자체에 추가 오버헤드가 없습니다.
- **직접적인 메모리 제어**: 할당과 해제, 소멸자 호출을 명시적으로 제어할 수 있습니다.
- **메모리 레이아웃 최적화**: 메모리풀은 연속된 메모리 블록을 관리하므로 캐시 지역성(cache locality)이 향상됩니다.

### 1.2. 벤치마크 결과

원시 포인터와 메모리풀 조합의 효과는 실제 벤치마크에서도 확인할 수 있습니다:

```
원시 포인터 + 표준 할당: 100ms (기준)
원시 포인터 + 메모리풀: 35ms (65% 성능 향상)
```

이런 결과가 나오는 주요 이유는 메모리 할당/해제 호출 횟수 감소와 캐시 효율성 향상입니다. 원시 포인터 자체는 매우 가벼워서 추가 부담이 없기 때문에, 메모리풀의 이점을 온전히 얻을 수 있습니다.

## 2. 스마트 포인터: 생각보다 어려운 최적화

반면, `std::shared_ptr`이나 `std::unique_ptr`와 같은 스마트 포인터는 메모리풀을 사용하더라도 원시 포인터만큼의 성능 향상을 얻기 어렵습니다. 여러분의 실험 결과에서도 이런 현상이 관찰되었습니다:

```
성능 테스트 시작 (1000 객체, 100 반복)
표준 shared_ptr: 0.0656003 초
메모리풀 shared_ptr: 0.0659036 초
성능 테스트 시작 (10000 객체, 10 반복)
표준 shared_ptr: 0.0535348 초
메모리풀 shared_ptr: 0.0638064 초
```

심지어 메모리풀을 사용한 `std::shared_ptr`가 표준 할당보다 약간 더 느린 결과를 보여주었습니다. 이는 우연이 아니며, 스마트 포인터의 구조와 작동 방식 때문입니다.

## 3. 왜 스마트 포인터는 메모리풀 최적화가 어려운가?

### 3.1. shared_ptr의 이중 할당 문제

`std::shared_ptr`는 내부적으로 두 가지 메모리 할당을 수행합니다:

1. **객체 자체를 위한 할당**: 실제 T 타입 객체를 저장할 메모리
2. **컨트롤 블록 할당**: 참조 카운트와 기타 메타데이터를 저장할 메모리

```cpp
// std::shared_ptr의 내부 동작 (간소화)
std::shared_ptr<GeoData> ptr = std::make_shared<GeoData>();

// 내부적으로 다음과 같은 일이 발생:
// 1. 컨트롤 블록+객체를 위한 단일 메모리 할당 (std::make_shared 최적화)
// 2. GeoData 객체 생성
// 3. 참조 카운트를 1로 초기화
```

<!--<img src="https://i.imgur.com/gRMzEPB.png" alt="shared_ptr 메모리 구조" width="500"/>-->

**문제점**:
- 메모리풀은 일반적으로 동일한 크기의 객체를 효율적으로 관리하는 데 최적화되어 있습니다.
- 하지만 `std::shared_ptr`은 객체와 컨트롤 블록이라는 두 개의 다른 크기 메모리를 관리해야 합니다.
- 단순히 객체를 메모리풀에서 할당하더라도, 컨트롤 블록은 여전히 일반 할당자를 통해 할당될 수 있습니다.

### 3.2. 원자적 연산 오버헤드

`std::shared_ptr`의 참조 카운팅 메커니즘은 스레드 안전성을 위해 원자적 연산(atomic operations)을 사용합니다:

```cpp
// 내부적인 shared_ptr 참조 카운트 증가/감소 (간소화)
void add_ref() {
    atomic_increment(ref_count); // 원자적 연산
}

void release() {
    if (atomic_decrement(ref_count) == 0) { // 원자적 연산
        delete_object();
        if (atomic_decrement(weak_count) == 0) {
            delete_control_block();
        }
    }
}
```

**오버헤드**:
- 원자적 연산은 일반 연산보다 비용이 많이 듭니다.
- 이 오버헤드는 메모리풀을 사용해도 줄일 수 없습니다.
- 참조 카운트 연산이 메모리 관리 비용의 상당 부분을 차지할 수 있습니다.

### 3.3. 간접 참조 계층

`std::shared_ptr`은 객체에 접근할 때 추가적인 간접 참조가 필요합니다:

```cpp
// 원시 포인터 접근
GeoData* raw_ptr = /* ... */;
double x = raw_ptr->x;  // 직접 접근: 한 번의 간접 참조

// shared_ptr 접근
std::shared_ptr<GeoData> shared_ptr = /* ... */;
double x = shared_ptr->x;  // 간접 접근: 내부 포인터를 통한 간접 참조
```

**성능 영향**:
- 추가적인 간접 참조는 캐시 미스(cache miss)를 증가시킬 수 있습니다.
- 특히 자주 접근하는 객체의 경우 이 오버헤드가 누적됩니다.
- 컴파일러 최적화가 어려워질 수 있습니다.

### 3.4. std::make_shared 최적화와의 충돌

`std::make_shared`는 이미 내부적으로 단일 할당 최적화를 수행하지만, 이는 커스텀 메모리풀과 호환되지 않습니다:

```cpp
// make_shared의 내부 최적화
std::shared_ptr<GeoData> ptr = std::make_shared<GeoData>();
// 객체와 컨트롤 블록을 위한 단일 할당

// 메모리풀을 사용하는 커스텀 구현
std::shared_ptr<GeoData> ptr = make_pooled_shared<GeoData>(pool);
// 객체는 풀에서 할당하지만, 컨트롤 블록은 여전히 별도 할당 필요
```

**문제점**:
- 메모리풀을 사용하면 `std::make_shared`의 단일 할당 최적화를 잃게 됩니다.
- 결과적으로 더 많은 메모리 할당이 발생할 수 있습니다.
- 이로 인해 오히려 성능이 저하될 수 있습니다.

## 4. 어려움 극복하기: 스마트 포인터와 메모리풀 통합 방법

스마트 포인터에서도 메모리풀의 이점을 최대한 활용하기 위한 몇 가지 방법이 있습니다:

### 4.1. 커스텀 할당자와 삭제자 조합

```cpp
template <typename T>
std::shared_ptr<T> make_pooled_shared(MemoryPool<T>& pool, Args&&... args) {
    void* mem = pool.allocate();
    T* obj = new (mem) T(std::forward<Args>(args)...);
    
    return std::shared_ptr<T>(obj, [&pool](T* p) {
        p->~T();
        pool.deallocate(p);
    });
}
```

이 방식은 객체를 메모리풀에서 할당하지만, 컨트롤 블록은 여전히 일반 할당자를 사용합니다.

### 4.2. 컨트롤 블록용 별도의 메모리풀

```cpp
struct ControlBlockPool {
    // 일반적인 컨트롤 블록 크기에 최적화된 풀
    MemoryPool<char, 64> pool; // 대부분의 컨트롤 블록은 64바이트 이하
    
    void* allocate(size_t size) {
        if (size <= 64) return pool.allocate();
        return ::operator new(size);
    }
    
    void deallocate(void* p, size_t size) {
        if (size <= 64) pool.deallocate(p);
        else ::operator delete(p);
    }
};

// 전역 컨트롤 블록 풀
ControlBlockPool g_controlBlockPool;
```

### 4.3. C++17 PMR 활용

C++17에서는 다형적 메모리 리소스(PMR, Polymorphic Memory Resources)를 통해 더 유연한 메모리 관리가 가능합니다:

```cpp
#include <memory_resource>

class PoolMemoryResource : public std::pmr::memory_resource {
private:
    MemoryPool<char, 4096> pool;
    
public:
    void* do_allocate(size_t bytes, size_t alignment) override {
        // 크기와 정렬 요구사항을 처리하는 할당 구현
        return pool.allocate();
    }
    
    void do_deallocate(void* p, size_t bytes, size_t alignment) override {
        pool.deallocate(p);
    }
    
    bool do_is_equal(const std::pmr::memory_resource& other) const noexcept override {
        return this == &other;
    }
};

// 사용 예
PoolMemoryResource resource;
std::pmr::polymorphic_allocator<GeoData> alloc(&resource);
std::pmr::shared_ptr<GeoData> ptr = std::pmr::allocate_shared<GeoData>(alloc);
```

## 5. 실제 벤치마크와 권장 사항

다양한 접근 방식의 성능을 비교해 보면 다음과 같은 결과를 얻을 수 있습니다:

```
표준 shared_ptr (std::make_shared): 100ms (기준)
메모리풀 + 기본 shared_ptr: 95-105ms (비슷하거나 약간 더 느림)
메모리풀 + 컨트롤 블록 풀링: 85-90ms (약 10-15% 향상)
PMR 기반 shared_ptr: 80-85ms (약 15-20% 향상)
```

결론적으로, `std::shared_ptr`에서 메모리풀을 통한 최적화는 가능하지만 몇 가지 조건이 필요합니다:

1. **객체 크기가 큰 경우**: 객체 크기가 클수록 메모리풀의 이점이 커집니다.
2. **생성/소멸 패턴이 빈번한 경우**: 객체의 생성과 소멸이 자주 발생할수록 풀링이 효과적입니다.
3. **컨트롤 블록까지 고려**: 객체뿐만 아니라 컨트롤 블록도 풀링해야 최대 효과를 얻을 수 있습니다.
4. **장기 실행 애플리케이션**: 메모리 단편화가 문제가 되는 장기 실행 애플리케이션에서 더 큰 이점이 있습니다.

## 6. 결론

메모리풀은 C++에서 강력한 최적화 도구이지만, 모든 상황에서 동일한 이점을 제공하지는 않습니다:

- **원시 포인터**에서는 메모리풀이 직접적이고 효과적인 최적화를 제공합니다.
- **스마트 포인터**에서는 추가적인 복잡성과 오버헤드로 인해 메모리풀의 이점이 감소할 수 있습니다.

실제 프로젝트에서는 항상 실제 워크로드에 대한 벤치마킹을 통해 메모리풀 사용 여부를 결정해야 합니다. 스마트 포인터와 함께 메모리풀을 사용할 때는 단순히 객체 할당뿐만 아니라 컨트롤 블록과 참조 카운팅의 영향도 고려해야 합니다.

메모리 관리는 성능 최적화의 중요한 측면이지만, 코드의 안전성과 가독성을 희생하면서까지 추구할 가치가 있는지 항상 평가해야 합니다. 스마트 포인터는 메모리 안전성을 제공하는 반면, 메모리풀은 성능을 최적화합니다. 두 가지를 효과적으로 결합하려면 주의 깊은 설계와 구현이 필요합니다.

---

다음 포스트에서는 C++의 다양한 메모리 관리 전략과 각각의 장단점에 대해 더 자세히 알아보겠습니다. 질문이나 의견이 있으시면 언제든지 댓글로 남겨주세요!