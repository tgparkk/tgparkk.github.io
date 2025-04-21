---
layout: post
title: "윈도우 프로그래밍의 핵심: 단계별로 이해하는 메시지 시스템"
date: 2025-03-30
categories: windows
tags: [windows, win32, message]
excerpt: "윈도우즈 프로그램의 원리"
comments: true
---

# 윈도우 프로그래밍의 여정: 단계별로 이해하는 메시지 시스템

## 1단계: 윈도우 프로그래밍의 기초 이해하기

윈도우 프로그래밍을 처음 접하는 여러분을 위해, 가장 기본적인 개념부터 시작해보겠습니다.

### 일반 프로그램 vs 윈도우 프로그램

일반적인 콘솔 프로그램은 시작점에서 출발하여 순차적으로 실행되다가 종료됩니다. 예를 들어:

```c
int main() {
    // 1. 초기화
    // 2. 작업 수행
    // 3. 종료
    return 0;
}
```

하지만 윈도우 프로그램은 다릅니다. 윈도우 프로그램은 사용자와 상호작용하며, 사용자가 언제 어떤 행동을 할지 예측할 수 없습니다. 따라서 윈도우 프로그램은 **이벤트 기반 프로그래밍** 방식을 사용합니다.

### 이벤트 기반 프로그래밍

이벤트 기반 프로그래밍은 프로그램이 외부 이벤트(사용자 입력, 시스템 통지 등)에 반응하도록 설계된 프로그래밍 패러다임입니다.

예를 들어:
- 사용자가 버튼을 클릭합니다 → 프로그램이 반응합니다
- 사용자가 텍스트를 입력합니다 → 프로그램이 반응합니다
- 창의 크기가 변경됩니다 → 프로그램이 반응합니다

이러한 이벤트들은 예측할 수 없으며, 어떤 순서로 발생할지도 알 수 없습니다. 윈도우 프로그래밍에서는 이러한 이벤트들을 **메시지**라고 부릅니다.

## 2단계: 메시지 개념 이해하기

### 메시지란 무엇인가?

윈도우 프로그래밍에서 **메시지**는 운영체제와 애플리케이션 간의 통신 수단입니다. 모든 사용자 입력과 시스템 이벤트는 메시지로 변환되어 애플리케이션에 전달됩니다.

메시지는 다음과 같은 정보를 포함합니다:
- **hwnd**: 메시지를 받을 윈도우의 핸들
- **message**: 메시지 유형 (예: WM_PAINT, WM_KEYDOWN)
- **wParam**: 추가 정보 1
- **lParam**: 추가 정보 2

예를 들어, 사용자가 'A' 키를 누르면:
- **message**: WM_KEYDOWN (키가 눌림)
- **wParam**: 'A'의 가상 키 코드
- **lParam**: 키보드 상태에 대한 추가 정보

### 주요 메시지 유형

윈도우 프로그래밍에서 자주 사용되는 메시지 유형은 다음과 같습니다:

- **WM_CREATE**: 윈도우가 생성될 때
- **WM_DESTROY**: 윈도우가 파괴될 때
- **WM_PAINT**: 윈도우를 다시 그려야 할 때
- **WM_SIZE**: 윈도우 크기가 변경될 때
- **WM_KEYDOWN**: 키보드 키가 눌릴 때
- **WM_LBUTTONDOWN**: 마우스 왼쪽 버튼이 눌릴 때

이 단계에서는 메시지가 무엇인지 이해하는 것이 중요합니다. 다음으로, 이러한 메시지들이 어떻게 처리되는지 알아보겠습니다.

## 3단계: 메시지 큐 이해하기

이벤트가 발생할 때마다 메시지가 생성되는데, 이 메시지들은 어디에 저장될까요? 바로 **메시지 큐**입니다.

### 메시지 큐의 역할

메시지 큐는 처리 대기 중인 메시지들을 저장하는 자료구조입니다. 이는 마치 우체국의 우편함과 같습니다. 다양한 곳에서 온 편지들이 우편함에 쌓이고, 차례대로 처리되기를 기다립니다.

윈도우 운영체제는 각 스레드(실행 단위)마다 별도의 메시지 큐를 관리합니다. 메시지는 기본적으로 FIFO(First In, First Out) 방식으로 처리됩니다. 즉, 먼저 들어온 메시지가 먼저 처리됩니다.

```
메시지 큐: [WM_KEYDOWN] → [WM_MOUSEMOVE] → [WM_PAINT] → ...
```

그러나 모든 메시지가 동등하게 취급되는 것은 아닙니다. 일부 메시지(예: 입력 메시지)는 우선적으로 처리될 수 있습니다.

이 단계에서는 메시지 큐가 메시지를 임시 저장하는 장소라는 것을 이해하는 것이 중요합니다. 다음으로, 이 큐에서 메시지를 꺼내어 처리하는 방법을 알아보겠습니다.

## 4단계: 메시지 루프 이해하기

메시지 큐에 쌓인 메시지를 꺼내어 처리하는 코드 구조를 **메시지 루프**라고 합니다. 이는 윈도우 프로그램의 핵심 부분입니다.

### 메시지 루프의 기본 구조

```c
int WINAPI WinMain(...) {
    // 윈도우 생성 코드...
    
    // 메시지 루프
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    
    return (int)msg.wParam;
}
```

이 코드에서:
1. **GetMessage**: 메시지 큐에서 메시지를 가져옵니다. 메시지가 없으면 기다립니다.
2. **TranslateMessage**: 키보드 입력 메시지를 번역합니다(예: 가상 키 코드를 문자로).
3. **DispatchMessage**: 메시지를 적절한 윈도우 프로시저로 전달합니다.

메시지 루프는 프로그램이 종료될 때까지(WM_QUIT 메시지를 받을 때까지) 계속 실행됩니다.

이 단계에서는 메시지 루프가 메시지 큐에서 메시지를 가져와 처리하는 역할을 한다는 것을 이해하는 것이 중요합니다. 다음으로, 메시지가 어디로 전달되는지 알아보겠습니다.

## 5단계: 윈도우 프로시저 이해하기

메시지 루프의 `DispatchMessage` 함수는 메시지를 **윈도우 프로시저**로 전달합니다. 윈도우 프로시저는 메시지에 따라 적절한 동작을 수행하는 함수입니다.

### 윈도우 프로시저의 기본 구조

```c
LRESULT CALLBACK WindowProc(HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam) {
    switch (message) {
    case WM_PAINT:
        // 화면 그리기 코드
        break;
        
    case WM_KEYDOWN:
        // 키보드 입력 처리 코드
        break;
        
    case WM_DESTROY:
        PostQuitMessage(0);  // WM_QUIT 메시지를 게시하여 메시지 루프 종료
        break;
        
    default:
        // 기본 메시지 처리
        return DefWindowProc(hwnd, message, wParam, lParam);
    }
    return 0;
}
```

윈도우 프로시저는 `switch` 문을 사용하여 메시지 유형에 따라 다른 코드를 실행합니다. 처리하지 않는 메시지는 `DefWindowProc` 함수에 위임합니다.

윈도우 프로시저는 윈도우 클래스를 등록할 때 지정됩니다:

```c
WNDCLASS wc = {0};
wc.lpfnWndProc = WindowProc;  // 윈도우 프로시저 설정
wc.lpszClassName = L"MyWindowClass";
// 기타 설정...
RegisterClass(&wc);
```

이 단계에서는 윈도우 프로시저가 메시지에 반응하여 실제 작업을 수행하는 함수라는 것을 이해하는 것이 중요합니다.

## 6단계: 전체 흐름 이해하기

지금까지 배운 개념들을 통합하여 윈도우 프로그램의 전체 흐름을 이해해 봅시다.

1. **이벤트 발생**: 사용자가 키를 누르거나, 마우스를 클릭하거나, 시스템 이벤트가 발생합니다.
2. **메시지 생성**: 운영체제가 이벤트를 감지하고 메시지를 생성합니다.
3. **메시지 큐에 추가**: 생성된 메시지는 해당 애플리케이션의 메시지 큐에 추가됩니다.
4. **메시지 루프**: 애플리케이션의 메시지 루프가 메시지 큐에서 메시지를 가져옵니다.
5. **윈도우 프로시저**: 메시지가 적절한 윈도우 프로시저로 전달되어 처리됩니다.
6. **동작 수행**: 윈도우 프로시저가 메시지에 따라 적절한 동작을 수행합니다.

이러한 과정이 프로그램이 실행되는 동안 계속 반복됩니다.

### 구체적인 예: 버튼 클릭

사용자가 버튼을 클릭할 때 어떤 일이 일어나는지 단계별로 살펴봅시다:

1. 사용자가 버튼 위에서 마우스 왼쪽 버튼을 클릭합니다.
2. 운영체제가 WM_LBUTTONDOWN 메시지를 생성합니다.
3. 이 메시지는 버튼 윈도우의 메시지 큐에 추가됩니다.
4. 버튼의 윈도우 프로시저가 이 메시지를 처리하고, 버튼이 클릭되었음을 인식합니다.
5. 버튼은 자신의 부모 윈도우에 WM_COMMAND 메시지를 보냅니다.
6. 부모 윈도우의 윈도우 프로시저가 WM_COMMAND 메시지를 받고, 버튼 ID를 확인하여 적절한 동작을 수행합니다.

## 7단계: 실제 코드로 이해하기

이제 간단한 윈도우 애플리케이션 코드를 통해 모든 개념을 종합적으로 이해해 봅시다.

```c
#include <windows.h>

// 윈도우 프로시저 함수 선언
LRESULT CALLBACK WindowProc(HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam);

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    // 윈도우 클래스 등록
    const wchar_t CLASS_NAME[] = L"Sample Window Class";
    
    WNDCLASS wc = {0};
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = CLASS_NAME;
    RegisterClass(&wc);
    
    // 윈도우 생성
    HWND hwnd = CreateWindowEx(
        0,                      // 확장 스타일
        CLASS_NAME,             // 윈도우 클래스
        L"윈도우 제목",         // 윈도우 제목
        WS_OVERLAPPEDWINDOW,    // 윈도우 스타일
        CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT,
        NULL,       // 부모 윈도우
        NULL,       // 메뉴
        hInstance,  // 인스턴스 핸들
        NULL        // 추가 데이터
    );
    
    if (hwnd == NULL) {
        return 0;
    }
    
    // 윈도우 표시
    ShowWindow(hwnd, nCmdShow);
    
    // 메시지 루프
    MSG msg = {0};
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    
    return (int)msg.wParam;
}

// 윈도우 프로시저
LRESULT CALLBACK WindowProc(HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam) {
    switch (message) {
    case WM_PAINT: {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hwnd, &ps);
        
        // 간단한 텍스트 출력
        TextOut(hdc, 10, 10, L"안녕하세요, 윈도우 프로그래밍!", 15);
        
        EndPaint(hwnd, &ps);
        break;
    }
    
    case WM_DESTROY:
        PostQuitMessage(0);
        break;
        
    default:
        return DefWindowProc(hwnd, message, wParam, lParam);
    }
    return 0;
}
```

이 코드는 간단한 텍스트를 표시하는 윈도우 애플리케이션을 생성합니다. 코드의 주요 부분을 살펴보면:

1. **윈도우 클래스 등록**: `WindowProc` 함수를 윈도우 프로시저로 지정합니다.
2. **윈도우 생성**: 등록된 클래스를 사용하여 실제 윈도우를 생성합니다.
3. **메시지 루프**: `GetMessage`, `TranslateMessage`, `DispatchMessage` 함수를 사용하여 메시지를 처리합니다.
4. **윈도우 프로시저**: `WM_PAINT` 메시지에서는 텍스트를 그리고, `WM_DESTROY` 메시지에서는 종료 메시지를 게시합니다.

## 8단계: 고급 개념 소개

기본 개념을 이해했다면, 이제 몇 가지 고급 개념을 소개하겠습니다.

### 1. 여러 윈도우 프로시저 사용하기

하나의 애플리케이션에서 여러 종류의 윈도우를 사용할 경우, 각 윈도우 유형에 대해 별도의 윈도우 프로시저를 가질 수 있습니다.

```c
// 메인 윈도우 프로시저
LRESULT CALLBACK MainWindowProc(HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam) {
    // 메인 윈도우 처리...
}

// 대화 상자 프로시저
LRESULT CALLBACK DialogProc(HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam) {
    // 대화 상자 처리...
}
```

### 2. 사용자 정의 메시지

윈도우에서 제공하는 기본 메시지 외에도, 애플리케이션에서 필요한 사용자 정의 메시지를 만들 수 있습니다.

```c
// 사용자 정의 메시지 정의
#define WM_USER_CUSTOM (WM_USER + 100)

// 사용자 정의 메시지 전송
SendMessage(hwnd, WM_USER_CUSTOM, wParam, lParam);

// 윈도우 프로시저에서 처리
case WM_USER_CUSTOM:
    // 사용자 정의 메시지 처리
    break;
```

### 3. 메시지 필터링

특정 범위의 메시지만 처리하고 싶을 때는 `PeekMessage` 함수를 사용하여 메시지를 필터링할 수 있습니다.

```c
// 키보드 메시지만 처리
PeekMessage(&msg, NULL, WM_KEYFIRST, WM_KEYLAST, PM_REMOVE);
```

## 9단계: 실전 팁과 요약

### 디버깅 팁

윈도우 메시지를 디버깅할 때는 다음과 같은 방법을 사용할 수 있습니다:

1. **메시지 로깅**: 윈도우 프로시저에서 받는 메시지를 로그 파일에 기록합니다.
2. **Spy++**: 윈도우 SDK에 포함된 Spy++ 도구를 사용하여 메시지 흐름을 모니터링합니다.
3. **OutputDebugString**: 디버그 출력 창에 메시지 정보를 출력합니다.

### 핵심 요약

윈도우 프로그래밍의 핵심 개념을 정리하면:

1. **메시지**: 운영체제와 애플리케이션 간의 통신 수단
2. **메시지 큐**: 처리 대기 중인 메시지를 저장하는 자료구조
3. **메시지 루프**: 메시지 큐에서 메시지를 가져와 처리하는 코드 구조
4. **윈도우 프로시저**: 메시지에 따라 적절한 동작을 수행하는 함수

이러한 개념들이 상호작용하여 이벤트 기반의 윈도우 애플리케이션이 동작합니다.

### 다음 단계

윈도우 프로그래밍의 기본 개념을 이해했다면, 다음 단계로 배울 수 있는 주제들은:

1. **GDI/GDI+**: 그래픽 처리와 관련된 고급 기술
2. **다이얼로그 기반 프로그래밍**: 대화 상자를 이용한 사용자 인터페이스 구현
3. **공통 컨트롤**: 버튼, 리스트 박스, 트리 뷰 등의 표준 컨트롤 사용
4. **멀티스레딩**: 여러 스레드를 사용한 프로그래밍
5. **COM/OLE**: 컴포넌트 기반 프로그래밍

윈도우 프로그래밍은 처음에는 복잡해 보일 수 있지만, 기본 개념을 단계별로 이해하면 충분히 습득할 수 있습니다. 이 가이드가 여러분의 윈도우 프로그래밍 여정에 도움이 되기를 바랍니다.