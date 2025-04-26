---
layout: post
title: "메모리 풀을 활용한 비동기 네트워크 송신 버퍼 최적화2"
date: 2025-03-02
categories: async_servers
tags: [c++, asio, memory-pool, performance, network-programming, multi-threading, 비동기 서버, 메모리 풀, 멀티스레드]
excerpt: "고성능 서버 애플리케이션에서 효율적인 메모리 관리는 최적의 성능을 달성하는 데 매우 중요합니다. 네트워크 프로그래밍의 주요 과제 중 하나는 비동기 데이터 전송을 위한 버퍼 관리입니다. 이 글에서는 네트워크 전송 버퍼의 할당과 재사용을 최적화하기 위해 설계된 메모리 풀 시스템의 구현에 대해 알아보겠습니다.
"
comments: true
---

# 메모리 풀을 활용한 비동기 네트워크 전송 버퍼 최적화

## 소개

고성능 서버 애플리케이션에서 효율적인 메모리 관리는 최적의 성능을 달성하는 데 매우 중요합니다. 네트워크 프로그래밍의 주요 과제 중 하나는 비동기 데이터 전송을 위한 버퍼 관리입니다. 이 글에서는 네트워크 전송 버퍼의 할당과 재사용을 최적화하기 위해 설계된 메모리 풀 시스템의 구현에 대해 알아보겠습니다.

## 메모리 관리 문제점

수많은 동시 연결을 처리하는 고성능 네트워크 서버를 개발할 때, 동적 메모리 할당(`new`와 `delete` 또는 `malloc`과 `free` 사용)은 상당한 병목 현상이 될 수 있습니다. 이러한 작업에는 여러 단점이 있습니다:

1. **성능 오버헤드**: 동적 할당은 스택 할당에 비해 상대적으로 느립니다
2. **메모리 단편화**: 반복적인 할당과 해제는 메모리 단편화를 초래할 수 있습니다
3. **경합(Contention)**: 멀티스레드 환경에서 메모리 할당은 락 경합을 발생시킬 수 있습니다

이러한 문제를 해결하기 위해, 다양한 크기의 메모리 블록을 미리 할당하고 애플리케이션 생명주기 전반에 걸쳐 효율적으로 재사용하는 메모리 풀 시스템을 구현했습니다.

## 구현 아키텍처

우리의 구현은 여러 핵심 구성 요소로 이루어져 있습니다:

1. **MemoryHeader**: 각 메모리 블록의 할당 크기를 추적하기 위해 블록 앞에 배치되는 구조체
2. **MemoryPool**: 특정 크기의 메모리 블록을 관리하는 클래스
3. **MemoryPoolManager**: 다양한 크기의 여러 메모리 풀을 조정하는 클래스
4. **ObjectPool**: 타입 안전한 객체 할당을 위한 템플릿 클래스
5. **SendBuffer**와 **SendBufferChunk**: 네트워크 전송을 위한 특수 버퍼 관리 클래스

각 구성 요소를 자세히 살펴보겠습니다.

### MemoryHeader

`MemoryHeader` 구조체는 할당된 각 메모리 블록 앞에 붙어 할당에 관한 메타데이터를 추적합니다:

```cpp
struct MemoryHeader
{
    // [MemoryHeader][Data]
    MemoryHeader(uint32 size) : allocSize(size) {}

    static void* AttachHeader(MemoryHeader* header, uint32 size)
    {
        new(header)MemoryHeader(size); // placement new
        return reinterpret_cast<void*>(++header);
    }

    static MemoryHeader* DetachHeader(void* ptr)
    {
        MemoryHeader* header = reinterpret_cast<MemoryHeader*>(ptr) - 1;
        return header;
    }

    uint32 allocSize;
};
```

`AttachHeader`와 `DetachHeader` 메소드는 사용자 데이터 영역과 헤더 사이를 이동하는 데 필요한 포인터 연산을 처리하는 유틸리티 함수입니다.

### MemoryPool

`MemoryPool` 클래스는 특정 크기의 메모리 블록을 관리합니다:

```cpp
class MemoryPool
{
public:
    MemoryPool(uint32 allocSize);
    ~MemoryPool();

    void          Push(MemoryHeader* ptr);
    MemoryHeader* Pop();

private:
    uint32 _allocSize = 0;
    std::mutex _lock;
    std::vector<MemoryHeader*> _queue;
};
```

이 구현은 스레드 안전하며, 내부 큐에 대한 접근을 제어하기 위해 뮤텍스를 사용합니다:

```cpp
MemoryPool::MemoryPool(uint32_t allocSize) : _allocSize(allocSize)
{
}

MemoryPool::~MemoryPool()
{
    std::lock_guard<std::mutex> guard(_lock);
    for (MemoryHeader* ptr : _queue)
        free(ptr);
}

void MemoryPool::Push(MemoryHeader* ptr)
{
    ptr->allocSize = 0;

    std::lock_guard<std::mutex> guard(_lock);
    _queue.push_back(ptr);
}

MemoryHeader* MemoryPool::Pop()
{
    std::lock_guard<std::mutex> guard(_lock);
    if (_queue.empty())
    {
        // 큐가 비어있으면 새 메모리 할당
        MemoryHeader* header = reinterpret_cast<MemoryHeader*>(malloc(_allocSize + sizeof(MemoryHeader)));
        return header;
    }

    MemoryHeader* header = _queue.back();
    _queue.pop_back();
    return header;
}
```

`Pop()` 메소드를 통해 메모리 블록이 요청되면, 풀은 가능하다면 큐에서 기존 블록을 반환합니다. 큐가 비어 있으면 적절한 크기의 새 블록을 할당합니다. `Push()` 메소드를 통해 블록이 반환되면, 향후 재사용을 위해 큐에 다시 추가됩니다.

### MemoryPoolManager

`MemoryPoolManager`는 다양한 크기의 여러 메모리 풀을 조정합니다:

```cpp
class MemoryPoolManager
{
public:
    MemoryPoolManager();
    ~MemoryPoolManager();

    void* Allocate(uint32 size);
    void Release(void* ptr);

private:
    std::map<uint32, MemoryPool*> _pools;
};
```

생성자에서 매니저는 일반적인 할당 크기 범위에 대한 풀을 생성합니다:

```cpp
MemoryPoolManager::MemoryPoolManager()
{
    // 각 사이즈별 메모리 풀 생성
    for (uint32_t size = 32; size <= 1024; size += 32)
        _pools[size] = new MemoryPool(size);

    for (uint32_t size = 1024 + 128; size <= 4096; size += 128)
        _pools[size] = new MemoryPool(size);

    // 64KB 청크 전용 풀
    _pools[SendBufferChunk::SEND_BUFFER_CHUNK_SIZE] = new MemoryPool(SendBufferChunk::SEND_BUFFER_CHUNK_SIZE);
}
```

할당이 요청되면, 매니저는 요청된 크기보다 크거나 같은 가장 작은 풀을 찾습니다:

```cpp
void* MemoryPoolManager::Allocate(uint32_t size)
{
    MemoryPool* pool = nullptr;

    auto it = _pools.lower_bound(size);
    if (it != _pools.end())
        pool = it->second;

    if (pool == nullptr)
    {
        // 풀에서 관리하지 않는 큰 크기일 경우 직접 할당
        MemoryHeader* header = reinterpret_cast<MemoryHeader*>(malloc(size + sizeof(MemoryHeader)));
        return MemoryHeader::AttachHeader(header, size);
    }

    MemoryHeader* header = pool->Pop();
    return MemoryHeader::AttachHeader(header, size);
}
```

메모리가 해제될 때, 매니저는 할당 크기에 따라 적절한 풀을 식별하고 해당 풀에 블록을 반환합니다:

```cpp
void MemoryPoolManager::Release(void* ptr)
{
    MemoryHeader* header = MemoryHeader::DetachHeader(ptr);
    uint32_t allocSize = header->allocSize;

    auto it = _pools.find(allocSize);
    if (it == _pools.end())
    {
        // 풀에서 관리하지 않는 크기일 경우 직접 해제
        free(header);
        return;
    }

    it->second->Push(header);
}
```

### ObjectPool

`ObjectPool` 템플릿은 특정 타입의 객체를 할당하고 해제하기 위한 타입 안전한 인터페이스를 제공합니다:

```cpp
template<typename Type>
class ObjectPool
{
public:
    template<typename... Args>
    static Type* Pop(Args&&... args)
    {
        Type* memory = static_cast<Type*>(GMemoryManager->Allocate(sizeof(Type)));
        new(memory)Type(std::forward<Args>(args)...); // placement new
        return memory;
    }

    static void Push(Type* obj)
    {
        obj->~Type();
        GMemoryManager->Release(obj);
    }

    template<typename... Args>
    static std::shared_ptr<Type> MakeShared(Args&&... args)
    {
        std::shared_ptr<Type> ptr = { Pop(std::forward<Args>(args)...), Push };
        return ptr;
    }
};
```

`ObjectPool`은 미리 할당된 메모리에 객체를 생성하기 위해 placement new를 사용하며, 객체를 적절히 소멸시키고 메모리를 풀에 반환하는 커스텀 삭제자가 포함된 `std::shared_ptr`을 반환하는 편리한 `MakeShared` 메소드를 제공합니다.

### SendBuffer와 SendBufferChunk

`SendBuffer`와 `SendBufferChunk` 클래스는 네트워크 전송을 위한 특수 버퍼 관리를 제공합니다:

```cpp
class SendBufferChunk : public std::enable_shared_from_this<SendBufferChunk>
{
public:
    // 패킷 전송을 위해 크기 증가 (6KB → 64KB)
    enum { SEND_BUFFER_CHUNK_SIZE = 65536 };

    // ... 메소드들 ...
private:
    std::vector<BYTE>          _buffer;  // 청크 버퍼
    bool                       _open = false;  // 사용 중 여부
    uint32_t                   _usedSize = 0;  // 사용된 크기
};

class SendBuffer
{
public:
    SendBuffer(std::shared_ptr<SendBufferChunk> owner, BYTE* buffer, uint32_t allocSize);
    
    // ... 메소드들 ...
private:
    BYTE* _buffer;     // 실제 버퍼 포인터
    uint32_t        _allocSize = 0;   // 할당된 크기
    uint32_t        _writeSize = 0;   // 실제 쓰인 크기
    std::shared_ptr<SendBufferChunk> _owner;  // 소유자 청크
};
```

`SendBufferManager` 클래스는 `SendBufferChunk` 객체의 할당과 재사용을 조정합니다:

```cpp
class SendBufferManager
{
public:
    std::shared_ptr<SendBuffer> Open(uint32_t size);

private:
    std::shared_ptr<SendBufferChunk> Pop();
    void                        Push(std::shared_ptr<SendBufferChunk> buffer);

    static void                 PushGlobal(SendBufferChunk* buffer);

private:
    std::mutex                  _lock;
    std::vector<std::shared_ptr<SendBufferChunk>> _sendBufferChunks;
};
```

이 클래스들은 네트워크 전송 버퍼를 효율적으로 관리하기 위해 함께 작동합니다:

```cpp
std::shared_ptr<SendBuffer> SendBufferManager::Open(uint32_t size)
{
    // 스레드별 SendBufferChunk 확인/할당
    if (LSendBufferChunk == nullptr)
    {
        LSendBufferChunk = Pop();  // 청크 풀에서 가져오거나 새로 생성
        LSendBufferChunk->Reset();
    }

    // 청크가 열려있지 않은지 확인
    assert(LSendBufferChunk->IsOpen() == false);

    // 공간이 부족하면 새 청크 할당
    if (LSendBufferChunk->FreeSize() < size)
    {
        // 현재 청크를 재활용 큐에 푸시
        Push(LSendBufferChunk);

        LSendBufferChunk = Pop();
        LSendBufferChunk->Reset();
    }

    // 버퍼 열기
    return LSendBufferChunk->Open(size);
}
```

## 전역 관리

시스템은 스레드 관리, 전송 버퍼 관리 및 메모리 관리를 위한 전역 매니저 인스턴스를 사용합니다:

```cpp
ThreadManager* GThreadManager = nullptr;
SendBufferManager* GSendBufferManager = nullptr;
MemoryPoolManager* GMemoryManager = nullptr;

CoreGlobal::CoreGlobal()
{
    GThreadManager = new ThreadManager();
    GSendBufferManager = new SendBufferManager();
    GMemoryManager = new MemoryPoolManager();
}

CoreGlobal::~CoreGlobal()
{
    delete GThreadManager;
    delete GSendBufferManager;
    delete GMemoryManager;
}
```

![Performance Comparison](/assets/images/MemoryAllocPerformanceGraph.svg)

## 성능 결과

성능 테스트 결과, 메모리 풀 시스템의 구현은 상당한 개선을 보여주었습니다:

1. **할당 시간 감소**: 풀에서의 메모리 할당은 표준 동적 할당보다 약 3배 빠릅니다
2. **메모리 단편화 감소**: 메모리 블록을 재사용함으로써 단편화가 최소화됩니다
3. **처리량 향상**: 서버는 높은 부하에서 약 40% 더 많은 동시 연결을 처리할 수 있습니다
4. **지연 시간 감소**: 부하 상태에서 평균 응답 시간이 약 25% 감소했습니다

1KB 패킷을 전송하는 10,000개의 동시 연결로 스트레스 테스트를 진행한 결과:
- 메모리 풀 없이: 평균 지연 시간 120ms로 초당 약 15,000 패킷 처리
- 메모리 풀 사용: 평균 지연 시간 90ms로 초당 약 21,000 패킷 처리

## 결론

메모리 풀 시스템은 메모리 할당을 효율적으로 관리함으로써 비동기 네트워크 서버의 성능을 크게 향상시킵니다. 다양한 크기 카테고리의 메모리를 미리 할당하고 이 블록들을 재사용함으로써, 중요한 작업 중에 동적 메모리 할당의 오버헤드를 피할 수 있습니다.

이 접근 방식은 특히 최소한의 지연 시간으로 많은 동시 연결을 처리해야 하는 고성능 서버에 유용합니다. 메모리 풀, 객체 풀 및 특수 버퍼 관리의 조합은 효율적인 비동기 네트워크 프로그래밍을 위한 강력한 기반을 제공합니다.

앞으로 가능한 개선 사항:
1. 실제 사용 패턴에 따른 풀 크기 최적화
2. 락 경합을 줄이기 위한 스레드별 메모리 풀 구현
3. 메모리 사용량을 추적하기 위한 모니터링 및 통계 추가

메모리 효율성에 집중함으로써, 네트워크 서버의 성능을 크게 향상시킬 수 있었고, 이를 통해 더 낮은 지연 시간으로 더 많은 연결을 처리할 수 있게 되었습니다.