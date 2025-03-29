---
layout: post
title: "고성능 게임에서 사용하는 그래픽 기법 - 더블 버퍼링"
date: 2025-03-29
categories: gamedev
tags: [cpp, game, win32]
excerpt: "트리플 A 게임 기법 및 간단한 더블 버퍼링 구현"
---


# 고성능 게임에서 사용하는 그래픽 기법

게임 개발에서 부드러운 그래픽 표현은 사용자 경험에 핵심적인 요소입니다. 오늘은 현대 게임에서 필수적으로 사용되는 그래픽 기법 중 하나인 '더블 버퍼링(Double Buffering)'에 대해 알아보겠습니다. 기본 개념부터 실제 구현까지 단계별로 살펴보며, Win32 API를 활용한 간단한 예제 코드로 이해를 돕겠습니다.

## 고성능 게임에서도 사용되는 더블 버퍼링 기법

더블 버퍼링은 단순한 2D 게임부터 AAA 게임까지 거의 모든 게임에서 사용되는 기본적인 그래픽 렌더링 기법입니다. 
최신 게임 엔진과 그래픽 API(DirectX, OpenGL, Vulkan 등)에서는 이 개념이 기본적으로 내장되어 있으며, 더 발전된 형태로 구현되어 있습니다.

현대 고성능 게임에서는 더블 버퍼링을 기반으로 한 다양한 발전된 기법들이 사용됩니다:

- **트리플 버퍼링**: 세 개의 버퍼를 사용하여 CPU와 GPU 간의 작업을 더 효율적으로 병렬화합니다.
- **스왑 체인**: DirectX와 같은 그래픽 API에서 여러 버퍼를 관리하는 구조입니다.
- **V-Sync 및 적응형 동기화**: 화면 찢어짐 현상을 방지하기 위한 기술로, 최신 기술인 G-Sync나 FreeSync는 모니터의 재생률을 GPU의 프레임 생성 속도에 맞추는 적응형 기술입니다.
- **멀티 렌더 타겟**: 하나의 렌더링 패스에서 여러 버퍼에 다양한 정보를 렌더링하는 기법입니다.

이러한 발전된 기법들은 모두 기본적인 더블 버퍼링의 개념을 확장한 것이라고 볼 수 있습니다.

## 더블 버퍼링이 필요한 이유

더블 버퍼링이 왜 필요한지 이해하려면 화면에 그래픽을 표시하는 기본 원리를 알아야 합니다. 컴퓨터 화면은 보통 초당 60회(60Hz) 또는 그 이상의 속도로 업데이트됩니다. 그런데 그래픽을 그리는 과정은 순간적으로 이루어지지 않고 일정 시간이 소요됩니다.

더블 버퍼링이 없다면 다음과 같은 문제가 발생합니다:

1. **화면 깜빡임(Flickering)**: 화면이 지워지고 다시 그려지는 과정이 사용자에게 보이면 화면이 깜빡이는 현상이 발생합니다.
2. **화면 찢어짐(Tearing)**: 화면이 업데이트되는 도중에 새 프레임 그리기가 시작되면 화면의 일부는 이전 프레임, 나머지는 새 프레임으로 표시되어 화면이 '찢어진' 것처럼 보입니다.
3. **불완전한 그리기**: 복잡한 장면을 그리는 중간에 사용자에게 보여지면 완성되지 않은 그래픽이 노출됩니다.

더블 버퍼링은 이러한 문제를 해결하기 위해 두 개의 별도 버퍼를 사용합니다:
- **백 버퍼(Back Buffer)**: 다음 프레임을 완전히 그리는 작업이 이루어지는 화면에 보이지 않는 버퍼
- **프론트 버퍼(Front Buffer)**: 현재 화면에 표시되는 버퍼

그리기 작업이 백 버퍼에서 완전히 완료된 후, 두 버퍼를 '스왑(swap)'하여 완성된 이미지를 한 번에 화면에 표시합니다. 이 방식으로 사용자는 항상 완전하고 안정적인 프레임만 보게 됩니다.

## Win32를 통한 간단한 더블 버퍼링 구현

Windows API(Win32)를 사용하여 간단한 더블 버퍼링을 구현해 보겠습니다. 이 예제는 화면에서 부드럽게 움직이는 빨간 공을 표시합니다:

```cpp
#include <windows.h>

// 윈도우 프로시저 함수 선언
LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

// 더블 버퍼링을 위한 전역 변수
HDC g_hdcMemory = NULL;       // 메모리 DC (백 버퍼)
HBITMAP g_hbmMemory = NULL;   // 메모리 비트맵
HBITMAP g_hbmOld = NULL;      // 이전 비트맵 저장용
int g_nWidth = 800;           // 윈도우 너비
int g_nHeight = 600;          // 윈도우 높이

// 애니메이션을 위한 변수
int g_ballX = 100;            // 공의 X 위치
int g_ballY = 100;            // 공의 Y 위치
int g_ballSize = 50;          // 공의 크기
int g_velocityX = 5;          // X축 속도
int g_velocityY = 3;          // Y축 속도

// 더블 버퍼 초기화 함수
void InitDoubleBuffering(HWND hwnd)
{
    HDC hdc = GetDC(hwnd);
    
    // 메모리 DC 생성
    g_hdcMemory = CreateCompatibleDC(hdc);
    
    // 호환 비트맵 생성
    g_hbmMemory = CreateCompatibleBitmap(hdc, g_nWidth, g_nHeight);
    
    // 메모리 DC에 비트맵 선택, 이전 비트맵 저장
    g_hbmOld = (HBITMAP)SelectObject(g_hdcMemory, g_hbmMemory);
    
    ReleaseDC(hwnd, hdc);
}

// 더블 버퍼 해제 함수
void CleanupDoubleBuffering()
{
    if (g_hdcMemory)
    {
        // 원래 비트맵으로 복원
        SelectObject(g_hdcMemory, g_hbmOld);
        
        // 메모리 DC 삭제
        DeleteDC(g_hdcMemory);
        g_hdcMemory = NULL;
    }
    
    if (g_hbmMemory)
    {
        // 비트맵 삭제
        DeleteObject(g_hbmMemory);
        g_hbmMemory = NULL;
    }
}

// 애니메이션 업데이트 함수
void UpdateAnimation()
{
    // 공 위치 업데이트
    g_ballX += g_velocityX;
    g_ballY += g_velocityY;
    
    // 경계 충돌 확인 및 처리
    if (g_ballX <= 0 || g_ballX + g_ballSize >= g_nWidth)
        g_velocityX = -g_velocityX;
        
    if (g_ballY <= 0 || g_ballY + g_ballSize >= g_nHeight)
        g_velocityY = -g_velocityY;
}

// 화면 그리기 함수
void Render(HWND hwnd)
{
    HDC hdc = GetDC(hwnd);
    
    // 백 버퍼 클리어 (검은색)
    HBRUSH hBrushBlack = CreateSolidBrush(RGB(0, 0, 0));
    RECT rcClient = { 0, 0, g_nWidth, g_nHeight };
    FillRect(g_hdcMemory, &rcClient, hBrushBlack);
    DeleteObject(hBrushBlack);
    
    // 백 버퍼에 빨간 공 그리기
    HBRUSH hBrushRed = CreateSolidBrush(RGB(255, 0, 0));
    HBRUSH hOldBrush = (HBRUSH)SelectObject(g_hdcMemory, hBrushRed);
    Ellipse(g_hdcMemory, g_ballX, g_ballY, g_ballX + g_ballSize, g_ballY + g_ballSize);
    SelectObject(g_hdcMemory, hOldBrush);
    DeleteObject(hBrushRed);
    
    // 백 버퍼 내용을 화면으로 복사 (버퍼 스왑)
    BitBlt(hdc, 0, 0, g_nWidth, g_nHeight, g_hdcMemory, 0, 0, SRCCOPY);
    
    ReleaseDC(hwnd, hdc);
}

// 윈도우 진입점 함수
int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPWSTR lpCmdLine, int nCmdShow)
{
    // 윈도우 클래스 등록
    const wchar_t CLASS_NAME[] = L"DoubleBufferingExample";
    
    WNDCLASS wc = { 0 };
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = CLASS_NAME;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)GetStockObject(BLACK_BRUSH);
    
    RegisterClass(&wc);
    
    // 클라이언트 영역이 원하는 크기가 되도록 윈도우 크기 조정
    RECT rc = { 0, 0, g_nWidth, g_nHeight };
    AdjustWindowRect(&rc, WS_OVERLAPPEDWINDOW, FALSE);
    
    // 윈도우 생성
    HWND hwnd = CreateWindow(
        CLASS_NAME,           // 윈도우 클래스 이름
        L"더블 버퍼링 예제",    // 윈도우 제목
        WS_OVERLAPPEDWINDOW,  // 윈도우 스타일
        CW_USEDEFAULT, CW_USEDEFAULT, // 위치 (시스템 기본값)
        rc.right - rc.left, rc.bottom - rc.top, // 크기
        NULL,       // 부모 윈도우
        NULL,       // 메뉴
        hInstance,  // 인스턴스 핸들
        NULL);      // 추가 데이터
        
    if (!hwnd)
        return 0;
        
    // 윈도우 표시
    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);
    
    // 더블 버퍼링 초기화
    InitDoubleBuffering(hwnd);
    
    // 타이머 설정 (약 60 FPS)
    SetTimer(hwnd, 1, 16, NULL);
    
    // 메시지 루프
    MSG msg = { 0 };
    while (GetMessage(&msg, NULL, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    
    // 더블 버퍼링 해제
    CleanupDoubleBuffering();
    
    return (int)msg.wParam;
}

// 윈도우 프로시저
LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
    switch (uMsg)
    {
    case WM_TIMER:
        // 애니메이션 업데이트 및 화면 다시 그리기
        UpdateAnimation();
        InvalidateRect(hwnd, NULL, FALSE);
        return 0;
        
    case WM_PAINT:
        {
            PAINTSTRUCT ps;
            BeginPaint(hwnd, &ps);
            // 더블 버퍼링을 사용한 렌더링
            Render(hwnd);
            EndPaint(hwnd, &ps);
        }
        return 0;
        
    case WM_SIZE:
        // 윈도우 크기가 변경될 때 더블 버퍼 재초기화
        g_nWidth = LOWORD(lParam);
        g_nHeight = HIWORD(lParam);
        
        // 기존 버퍼 정리
        CleanupDoubleBuffering();
        
        // 새 크기로 재초기화
        InitDoubleBuffering(hwnd);
        return 0;
        
    case WM_DESTROY:
        // 타이머 해제
        KillTimer(hwnd, 1);
        
        // 종료 메시지 게시
        PostQuitMessage(0);
        return 0;
    }
    
    return DefWindowProc(hwnd, uMsg, wParam, lParam);
}
```

이 코드는 Win32 API를 사용하여 간단한 더블 버퍼링 애니메이션을 구현합니다. 화면에 빨간 공이 부드럽게 튕기며 움직이는 것을 볼 수 있습니다.

## 'Win32를 통한 간단한 더블 버퍼링 구현' 코드 설명

위 코드의 주요 부분을 자세히 살펴보겠습니다:

### 1. 더블 버퍼링을 위한 핵심 요소

```cpp
// 더블 버퍼링을 위한 전역 변수
HDC g_hdcMemory = NULL;       // 메모리 DC (백 버퍼)
HBITMAP g_hbmMemory = NULL;   // 메모리 비트맵
```

- `g_hdcMemory`: 백 버퍼로 사용될 메모리 Device Context
- `g_hbmMemory`: 실제 픽셀 데이터를 저장할 비트맵

### 2. 더블 버퍼 초기화 함수

```cpp
void InitDoubleBuffering(HWND hwnd)
{
    HDC hdc = GetDC(hwnd);
    g_hdcMemory = CreateCompatibleDC(hdc);
    g_hbmMemory = CreateCompatibleBitmap(hdc, g_nWidth, g_nHeight);
    g_hbmOld = (HBITMAP)SelectObject(g_hdcMemory, g_hbmMemory);
    ReleaseDC(hwnd, hdc);
}
```

이 함수는:
1. 윈도우의 Device Context를 가져옵니다.
2. 화면과 호환되는 메모리 DC를 생성합니다.
3. 윈도우 크기와 같은 비트맵을 생성합니다.
4. 메모리 DC에 비트맵을 선택하여 그리기 작업을 준비합니다.

### 3. 렌더링 함수

```cpp
void Render(HWND hwnd)
{
    HDC hdc = GetDC(hwnd);
    
    // 백 버퍼 클리어
    HBRUSH hBrushBlack = CreateSolidBrush(RGB(0, 0, 0));
    RECT rcClient = { 0, 0, g_nWidth, g_nHeight };
    FillRect(g_hdcMemory, &rcClient, hBrushBlack);
    DeleteObject(hBrushBlack);
    
    // 백 버퍼에 빨간 공 그리기
    HBRUSH hBrushRed = CreateSolidBrush(RGB(255, 0, 0));
    HBRUSH hOldBrush = (HBRUSH)SelectObject(g_hdcMemory, hBrushRed);
    Ellipse(g_hdcMemory, g_ballX, g_ballY, g_ballX + g_ballSize, g_ballY + g_ballSize);
    SelectObject(g_hdcMemory, hOldBrush);
    DeleteObject(hBrushRed);
    
    // 백 버퍼를 화면으로 복사 (버퍼 스왑)
    // BitBlt 함수는a "Bit Block Transfer"의 약자로, 한 DC에서 다른 DC로 비트맵 데이터를 복사하는 함수입니다.
    BitBlt(hdc, 0, 0, g_nWidth, g_nHeight, g_hdcMemory, 0, 0, SRCCOPY);
    
    ReleaseDC(hwnd, hdc);
}
```

더블 버퍼링의 핵심 과정:
1. 백 버퍼를 검은색으로 지웁니다.
2. 백 버퍼에 빨간 공을 그립니다.
3. 완성된 백 버퍼 내용을 화면(프론트 버퍼)으로 한 번에 복사합니다.

### 4. 윈도우 프로시저와 타이머

```cpp
case WM_TIMER:
    // 애니메이션 업데이트 및 화면 다시 그리기
    UpdateAnimation();
    InvalidateRect(hwnd, NULL, FALSE);
    return 0;
```

- `SetTimer(hwnd, 1, 16, NULL)` 호출로 약 60FPS의 타이머를 설정합니다.
- 타이머 이벤트가 발생할 때마다:
  1. `UpdateAnimation()`으로 공의 위치를 업데이트합니다.
  2. `InvalidateRect()`로 화면 갱신을 요청합니다.
  3. 이로 인해 `WM_PAINT` 메시지가 발생하여 `Render()` 함수가 호출됩니다.

### 5. 더블 버퍼링의 핵심 과정

더블 버퍼링의 전체 과정은 다음과 같습니다:
1. 메모리에 백 버퍼를 생성합니다.
2. 애니메이션 상태를 업데이트합니다.
3. 백 버퍼에 모든 그리기 작업을 수행합니다.
4. 완성된 백 버퍼 내용을 화면으로
 복사합니다.
5. 다음 프레임을 위해 1-4 과정을 반복합니다.

이 과정을 통해 사용자는 항상 완전하게 렌더링된 프레임만 보게 되므로, 깜빡임이나 찢어짐 현상 없이 부드러운 애니메이션을 경험할 수 있습니다.

## 결론

더블 버퍼링은 부드러운 그래픽 표현을 위한 필수적인 기법으로, 간단한 2D 게임부터 최신 3D 게임까지 모든 종류의 그래픽 애플리케이션에서 사용됩니다. 현대 게임 엔진과 그래픽 API에서는 이 개념이 더욱 발전된 형태로 구현되어 있지만, 기본 원리는 동일합니다.

Win32 API를 사용한 간단한 예제를 통해 더블 버퍼링의 구현 방법을 살펴보았습니다. 이를 통해 더블 버퍼링이 어떻게 화면 깜빡임과 찢어짐 현상을 방지하고 부드러운 애니메이션을 가능하게 하는지 이해할 수 있습니다.

고성능 게임 개발에서는 이러한 기본 개념을 넘어서 트리플 버퍼링, 수직 동기화, 다중 렌더 타겟 등 더 발전된 기법들을 활용하지만, 모두 더블 버퍼링의 기본 원리에서 출발했다는 점을 기억하는 것이 중요합니다.

# 보충 수업 (win32 함수 설명)
win32 함수들중 이해 안되는 부분이 있어, 추가로 정리 하고자 합니다!

## SelectObject 함수

`SelectObject` 함수는 Windows GDI(Graphics Device Interface)에서 그래픽 객체를 Device Context(DC)에 연결하는 핵심 함수입니다.

```cpp
HGDIOBJ SelectObject(HDC hdc, HGDIOBJ hgdiobj);
```

### 주요 특징과 작동 방식:

1. **용도**: 펜, 브러시, 비트맵, 폰트 등의 그래픽 객체를 특정 DC에 선택(활성화)합니다.

2. **작동 원리**: 
   - DC는 그래픽 출력을 위한 "그리기 환경"입니다.
   - `SelectObject`는 이 환경에 어떤 도구(객체)를 사용할지 지정합니다.
   - 비트맵을 선택하면 DC가 그 비트맵에 그림을 그립니다.

3. **반환값**:
   - 이전에 선택되어 있던 같은 유형의 객체의 핸들을 반환합니다.
   - 이 값을 저장해 두었다가 나중에 다시 선택하면 원래 상태로 복원할 수 있습니다.

4. **자원 관리**:
   - Windows의 GDI 자원은 제한되어 있어 올바른 관리가 중요합니다.
   - 객체 사용이 끝나면 원래 객체로 복원하고, 생성한 객체는 `DeleteObject`로 삭제해야 합니다.

### 예시:

```cpp
// 비트맵 선택 예시
HBITMAP hOldBitmap = (HBITMAP)SelectObject(hdcMemory, hBitmap);
// 여기서 hdcMemory에 그리기 작업 수행
// ... 
// 원래 비트맵으로 복원
SelectObject(hdcMemory, hOldBitmap);

// 브러시 선택 예시
HBRUSH hBrush = CreateSolidBrush(RGB(255, 0, 0));  // 빨간 브러시 생성
HBRUSH hOldBrush = (HBRUSH)SelectObject(hdc, hBrush);
// 이제 hdc에서의 채우기 작업은 빨간색 브러시를 사용
// ... 
// 원래 브러시로 복원
SelectObject(hdc, hOldBrush);
// 생성한 브러시 삭제
DeleteObject(hBrush);
```

더블 버퍼링에서 `SelectObject`는 메모리 DC에 비트맵을 연결하여 화면 대신 비트맵에 그림을 그릴 수 있게 합니다.

## BitBlt 함수

`BitBlt` 함수는a "Bit Block Transfer"의 약자로, 한 DC에서 다른 DC로 비트맵 데이터를 복사하는 함수입니다.

```cpp
BOOL BitBlt(
  HDC hdcDest,      // 목적지 DC
  int nXDest,       // 목적지 X 좌표
  int nYDest,       // 목적지 Y 좌표
  int nWidth,       // 복사할 영역 너비
  int nHeight,      // 복사할 영역 높이
  HDC hdcSrc,       // 소스 DC
  int nXSrc,        // 소스 X 좌표
  int nYSrc,        // 소스 Y 좌표
  DWORD dwRop       // 래스터 연산 코드
);
```

### 주요 특징과 작동 방식:

1. **용도**: 
   - 이미지 데이터를 한 곳에서 다른 곳으로 복사합니다.
   - 더블 버퍼링에서는 백 버퍼에서 화면으로 이미지를 복사하는 데 사용됩니다.

2. **매개변수**:
   - 소스와 목적지 DC, 복사할 영역의 좌표와 크기를 지정합니다.
   - `dwRop`은 래스터 연산 코드로, 소스와 목적지 픽셀이 어떻게 결합될지 결정합니다.

3. **래스터 연산 코드**:
   - `SRCCOPY`: 소스를 그대로 목적지에 복사 (가장 일반적)
   - `SRCAND`, `SRCOR`, `SRCINVERT` 등: 논리 연산 수행
   - 특수 효과나 마스킹 등에 다양한 코드 사용 가능

4. **성능**:
   - 하드웨어 가속을 활용할 수 있어 매우 빠른 속도로 대량의 픽셀 데이터 복사 가능
   - 이 때문에 더블 버퍼링의 버퍼 스왑에 이상적입니다.

### 더블 버퍼링에서의 활용:

```cpp
// 백 버퍼(g_hdcMemory)의 내용을 화면(hdc)으로 복사
BitBlt(hdc, 0, 0, g_nWidth, g_nHeight, g_hdcMemory, 0, 0, SRCCOPY);
```

이 한 줄의 코드가 더블 버퍼링의 핵심인 "버퍼 스왑" 역할을 합니다. 백 버퍼의 완성된 이미지가 화면에 한 번에 복사되어 깜빡임이 없는 부드러운 화면 전환이 가능해집니다.

## 메시지 루프 구문의 의미

```cpp
MSG msg = { 0 };
while (GetMessage(&msg, NULL, 0, 0)) {
    TranslateMessage(&msg);
    DispatchMessage(&msg);
}
```

이 코드는 Windows 애플리케이션의 핵심인 "메시지 루프"입니다:

1. **MSG msg = { 0 };**
   - Windows 메시지를 저장할 구조체를 초기화합니다.
   - `{ 0 }`은 모든 필드를 0으로 초기화하는 C/C++ 문법입니다.

2. **GetMessage(&msg, NULL, 0, 0)**
   - 애플리케이션의 메시지 큐에서 메시지를 가져옵니다.
   - 메시지가 있으면 `msg` 구조체에 저장하고 `TRUE`를 반환합니다.
   - `WM_QUIT` 메시지가 오면 `FALSE`를 반환하여 루프가 종료됩니다.
   - 매개변수:
     - `&msg`: 메시지를 저장할 구조체의 주소
     - 첫 번째 `NULL`: 모든 윈도우의 메시지를 받음
     - `0, 0`: 모든 메시지 유형을 받음

3. **TranslateMessage(&msg)**
   - 키보드 입력 메시지를 처리합니다.
   - 키 입력을 문자 메시지(`WM_CHAR`)로 변환합니다.
   - 텍스트 입력이 필요한 애플리케이션에서 중요합니다.

4. **DispatchMessage(&msg)**
   - 메시지를 해당 윈도우의 윈도우 프로시저(`WindowProc`)에 전달합니다.
   - 이 호출로 인해 `WindowProc` 함수가 실행되고 메시지 처리가 이루어집니다.

### 작동 흐름:

1. 사용자가 키를 누르거나 마우스를 클릭하면 Windows가 메시지를 생성합니다.
2. `GetMessage`가 메시지 큐에서 메시지를 가져옵니다.
3. `TranslateMessage`가 필요한 변환을 수행합니다.
4. `DispatchMessage`가 메시지를 윈도우 프로시저에 전달합니다.
5. 윈도우 프로시저가 메시지를 처리합니다(예: 키 입력, 마우스 클릭, 타이머 이벤트 등).
6. 반복: 애플리케이션이 종료될 때까지 이 과정을 반복합니다.

이 메시지 루프는 윈도우 애플리케이션의 "심장"으로, 사용자 입력과 시스템 이벤트에 반응하는 이벤트 기반 프로그래밍의 기초입니다.

## '윈도우의 Device Context를 가져옵니다' 의미

```cpp
HDC hdc = GetDC(hwnd);
```

이 코드는 특정 윈도우에 그림을 그릴 수 있게 해주는 "그래픽 컨텍스트"를 얻는 과정입니다:

1. **Device Context(DC)란?**
   - Windows에서 그래픽 출력을 위한 추상화된 그리기 환경입니다.
   - 화면, 프린터, 메모리 등 다양한 대상에 그리기 위한 인터페이스를 제공합니다.
   - 펜, 브러시, 폰트 등의 그래픽 속성과 현재 그리기 위치 등의 상태 정보를 포함합니다.

2. **GetDC 함수**:
   - 지정된 윈도우의 클라이언트 영역에 그리기 위한 DC를 가져옵니다.
   - 매개변수 `hwnd`는 DC를 가져올 윈도우의 핸들입니다.
   - 반환값은 해당 윈도우에 그리기 위한 DC 핸들입니다.

3. **사용 목적**:
   - 이 DC를 사용하여 텍스트, 선, 도형 등을 윈도우에 직접 그릴 수 있습니다.
   - 더블 버퍼링에서는 화면 DC의 특성을 파악하고 이와 호환되는 메모리 DC를 만들기 위해 사용합니다.

4. **자원 관리**:
   - `GetDC`로 가져온 DC는 사용 후 반드시 `ReleaseDC` 함수로 해제해야 합니다.
   - DC는 시스템 자원이므로 적절히 관리하지 않으면 자원 누수가 발생합니다.

더블 버퍼링 예제에서는 화면 DC를 임시로 가져와 호환되는 메모리 DC와 비트맵을 생성한 후, 다시 해제합니다.

## '화면과 호환되는 메모리 DC를 생성합니다' 의미

```cpp
g_hdcMemory = CreateCompatibleDC(hdc);
```

이 코드는 기존 DC(보통 화면 DC)와 호환되는 메모리 기반 DC를 만드는 과정입니다:

1. **메모리 DC란?**
   - 실제 화면이 아닌 메모리에 그림을 그릴 수 있는 가상의 그리기 환경입니다.
   - 화면에 직접 그리지 않고 "백 버퍼"로 사용할 수 있습니다.

2. **CreateCompatibleDC 함수**:
   - 매개변수로 전달된 DC와 호환되는 메모리 DC를 생성합니다.
   - "호환된다"는 것은 색상 형식, 해상도 등의 특성이 동일하다는 의미입니다.
   - 반환된 메모리 DC는 초기에 1x1 픽셀 크기의 기본 비트맵이 선택되어 있습니다.

3. **호환성의 중요성**:
   - 메모리 DC의 출력 형식이 화면 DC와 호환되어야 나중에 화면으로 복사할 때 문제가 없습니다.
   - 색상 깊이, 픽셀 형식 등이 일치해야 올바른 시각적 결과를 얻을 수 있습니다.

4. **더블 버퍼링에서의 역할**:
   - 화면에 직접 그리지 않고 먼저 메모리에 그릴 "백 버퍼"를 제공합니다.
   - 이 메모리 DC에 모든 그리기 작업을 수행한 후, 완성된 이미지를 한 번에 화면으로 복사합니다.

메모리 DC 생성 후에는 적절한 크기의 비트맵을 생성하여 이 DC에 선택해야 합니다. 그래야 원하는 크기의 이미지를 그릴 수 있습니다:

```cpp
g_hbmMemory = CreateCompatibleBitmap(hdc, g_nWidth, g_nHeight);
g_hbmOld = (HBITMAP)SelectObject(g_hdcMemory, g_hbmMemory);
```

이러한 과정을 통해 화면과 완전히 동일한 특성을 가진 "가상 캔버스"를 메모리에 만들고, 여기에 먼저 그림을 그린 후 완성된 결과를 화면에 한 번에 표시하는 더블 버퍼링을 구현할 수 있습니다.