---
layout: post
title: "초보자를 위한 Windows 그래픽 함수 이해하기: FillRect, SelectObject, DeleteObject, BitBlt"
date: 2025-04-04
categories: windows
tags: [windows, win32, rendering, FillRect, SelectObject, DeleteObject, BitBlt]
excerpt: "윈도우즈 프로그램의 렌더링링 원리"
comments: true
---

# 초보자를 위한 Windows 그래픽 함수 이해하기: FillRect, SelectObject, DeleteObject, BitBlt

Windows 프로그램에서 화면에 무언가를 그리려면 여러 그래픽 함수들을 사용해야 합니다. 이 글에서는 가장 많이 사용되는 그래픽 함수인 `FillRect`, `SelectObject`, `DeleteObject`, `BitBlt`가 실제로 어떻게 동작하는지 쉽게 설명하겠습니다.

## 그림 그리기의 기본 개념

Windows에서 그림을 그리는 것을 이해하려면 먼저 몇 가지 기본 개념을 알아야 합니다:

### DC(Device Context)란 무엇인가?

DC는 그림을 그릴 수 있는 캔버스라고 생각하면 됩니다. 화면에 그림을 그리려면 먼저 이 캔버스가 필요합니다. Windows에서는 이 캔버스를 "Device Context"라고 부르며, 줄여서 DC라고 합니다.

- **화면 DC**: 화면에 직접 그리는 캔버스
- **메모리 DC**: 화면에는 보이지 않는, 메모리 상의 임시 캔버스

### GDI 객체란 무엇인가?

GDI 객체는 그림을 그리는 도구들입니다:

- **브러시(Brush)**: 영역을 채우는 도구 (예: 빨간색 페인트)
- **펜(Pen)**: 선을 그리는 도구 (예: 파란색 펜)
- **비트맵(Bitmap)**: 이미지를 저장하는 도화지
- **폰트(Font)**: 글자를 그리는 스타일

이제 각 함수의 역할과 동작 방식을 자세히 살펴보겠습니다.

## SelectObject 함수: 캔버스에 도구 장착하기

`SelectObject` 함수는 이름 그대로 "객체를 선택"합니다. 그런데 이게 정확히 무슨 뜻일까요?

### SelectObject의 실제 의미

실생활에 비유하자면:

1. 여러분이 화가이고, 앞에 캔버스(DC)가 있습니다.
2. 옆에는 여러 그림 도구들(브러시, 펜, 비트맵 등)이 있습니다.
3. `SelectObject`는 "지금부터 이 도구를 사용할게요"라고 말하는 것과 같습니다.

```cpp
// 파란색 브러시 생성
HBRUSH hBlueBrush = CreateSolidBrush(RGB(0, 0, 255));

// 이제 이 브러시를 사용하겠다고 선언 (이전 브러시는 치워둠)
HBRUSH hOldBrush = (HBRUSH)SelectObject(hdc, hBlueBrush);
```

이 코드를 실행하면 "지금부터 파란색 브러시로 그릴게요"라고 말하는 것과 같습니다.

### SelectObject가 하는 일

1. DC(캔버스)에 어떤 도구를 사용할지 알려줍니다.
2. 이전에 사용하던 도구는 따로 저장해두고, 나중에 다시 사용할 수 있게 합니다.
3. 선택한 도구의 특성(예: 색상, 패턴)이 이후 모든 그리기 작업에 적용됩니다.

### 비트맵과 SelectObject

비트맵은 조금 특별합니다. 메모리 DC에 비트맵을 선택하면, 그 DC는 비트맵 위에 그림을 그리는 방식으로 동작합니다.

```cpp
// 메모리 DC 생성
HDC memDC = CreateCompatibleDC(hdc);

// 비트맵 생성
HBITMAP memBitmap = CreateCompatibleBitmap(hdc, 100, 100);

// 비트맵을 메모리 DC에 선택
HBITMAP oldBitmap = (HBITMAP)SelectObject(memDC, memBitmap);

// 이제 memDC에 그리면 memBitmap에 그려집니다!
```

이제 `memDC`에 무엇을 그리든 실제로는 `memBitmap`에 그려지게 됩니다. 마치 종이(비트맵)를 캔버스(DC)에 올려놓고 그림을 그리는 것과 같습니다.

## DeleteObject 함수: 사용한 도구 버리기

Windows에서 GDI 객체를 만들면(예: 브러시, 비트맵 등), 이 객체들은 시스템 메모리를 사용합니다. 다 사용한 후에는 이 메모리를 반환해야 합니다. 그것이 `DeleteObject` 함수의 역할입니다.

### DeleteObject가 하는 일

실생활에 비유하자면:

1. 여러분이 그림을 다 그렸습니다.
2. 더 이상 필요없는 페인트와 도구들을 정리하고 버립니다.

```cpp
// 더 이상 필요없는 브러시 삭제
DeleteObject(hBlueBrush);
```

### 중요한 주의사항

- 현재 캔버스(DC)에 선택된 도구는 삭제할 수 없습니다. 먼저 다른 도구로 바꾸거나, 원래 도구로 돌아가야 합니다.
- 도구를 삭제하지 않으면 메모리가 낭비됩니다(메모리 누수).
- Windows가 기본으로 제공하는 도구(스톡 객체)는 삭제하면 안 됩니다.

```cpp
// 올바른 방법
SelectObject(hdc, hOldBrush); // 원래 브러시로 복원
DeleteObject(hBlueBrush);     // 그런 다음 삭제
```

## FillRect 함수: 사각형 영역 채우기

`FillRect` 함수는 사각형 영역을 특정 브러시로 채웁니다. 매우 간단한 함수지만, 화면을 지우거나 배경을 그릴 때 자주 사용됩니다.

### FillRect가 하는 일

실생활에 비유하자면:

1. 캔버스의 특정 영역에 마스킹 테이프를 붙여 사각형을 만듭니다.
2. 그 영역을 브러시로 완전히 채웁니다.

```cpp
// 화면의 (10,10)부터 (110,110)까지 영역을 빨간색으로 채우기
RECT rect = { 10, 10, 110, 110 };
HBRUSH hRedBrush = CreateSolidBrush(RGB(255, 0, 0));
FillRect(hdc, &rect, hRedBrush);
DeleteObject(hRedBrush);
```

### 배경 지우기가 필요한 이유

```cpp
// 배경 지우기
RECT rcClient = { 0, 0, width, height };
FillRect(hdcMem, &rcClient, (HBRUSH)GetStockObject(WHITE_BRUSH));
```

이 코드가 필요한 이유는:

1. **깨끗한 시작점**: 비트맵을 새로 만들면, 그 내용은 초기화되지 않은 쓰레기 값들로 가득 차 있습니다. 새 그림을 그리기 전에 캔버스를 깨끗하게 지워야 합니다.

2. **이전 내용 제거**: 같은 캔버스를 계속 재사용할 때, 이전에 그린 그림이 남아 있을 수 있습니다. 새 그림을 그리기 전에 이전 내용을 지워야 합니다.

3. **일관된 배경색**: 배경색을 명확하게 설정하여 그림의 나머지 부분과 조화를 이루게 합니다.

배경을 지우지 않으면 어떻게 될까요? 이전에 그려진 내용 위에 새로운 내용이 그려지므로, 화면이 지저분해지고 사용자가 혼란스러워할 수 있습니다.

## BitBlt 함수: 이미지 복사하기

`BitBlt` 함수는 한 DC에서 다른 DC로 이미지를 복사합니다. 이 함수는 더블 버퍼링에서 핵심적인 역할을 합니다.

### BitBlt가 하는 일

실생활에 비유하자면:

1. 한 종이(소스 DC)에 그려진 그림을
2. 다른 종이(대상 DC)에 복사하는 것과 같습니다.

```cpp
// 메모리 DC의 내용을 화면 DC로 복사
BitBlt(hdc, 0, 0, width, height, memDC, 0, 0, SRCCOPY);
```

이 코드는 "memDC에 그려진 내용을 hdc로 그대로 복사해주세요"라는 의미입니다.

### 더블 버퍼링과 BitBlt

더블 버퍼링은 화면 깜빡임을 방지하는 기법입니다:

1. 메모리에 그림을 모두 그린 다음(사용자에게 보이지 않음)
2. 완성된 그림을 한 번에 화면에 복사합니다.

이렇게 하면 사용자는 그림이 그려지는 과정을 보지 않고, 완성된 결과만 보게 됩니다.

## 전체 과정 이해하기: 간단한 예제

이 함수들이 어떻게 함께 동작하는지 이해하기 위해 간단한 예제를 살펴보겠습니다:

```cpp
void 간단한그림그리기(HDC hdc, int width, int height)
{
    // 1. 메모리 캔버스와 도화지 준비하기
    HDC memDC = CreateCompatibleDC(hdc);                  // 보이지 않는 임시 캔버스 생성
    HBITMAP memBitmap = CreateCompatibleBitmap(hdc, width, height); // 도화지(비트맵) 생성
    HBITMAP oldBitmap = (HBITMAP)SelectObject(memDC, memBitmap);    // 캔버스에 도화지 장착

    // 2. 도화지 깨끗하게 지우기(흰색으로)
    RECT rcClient = { 0, 0, width, height };
    FillRect(memDC, &rcClient, (HBRUSH)GetStockObject(WHITE_BRUSH));

    // 3. 빨간색 사각형 그리기
    HBRUSH hRedBrush = CreateSolidBrush(RGB(255, 0, 0));  // 빨간색 브러시 만들기
    RECT rcRed = { 50, 50, 150, 150 };                    // 사각형 위치와 크기 설정
    FillRect(memDC, &rcRed, hRedBrush);                   // 사각형 채우기
    DeleteObject(hRedBrush);                              // 다 쓴 브러시 정리하기

    // 4. 그려진 그림을 화면으로 한 번에 복사하기
    BitBlt(hdc, 0, 0, width, height, memDC, 0, 0, SRCCOPY);

    // 5. 정리하기 (항상 생성의 역순으로)
    SelectObject(memDC, oldBitmap);  // 원래 비트맵으로 복원
    DeleteObject(memBitmap);         // 생성한 비트맵 삭제
    DeleteDC(memDC);                 // 메모리 DC 삭제
}
```

### 코드 설명

1. **준비 단계**: 보이지 않는 메모리 캔버스와 도화지를 만들고 연결합니다.
2. **배경 지우기**: 도화지를 흰색으로 깨끗하게 지웁니다.
3. **그림 그리기**: 빨간색 사각형을 그립니다.
4. **화면에 표시**: 완성된 그림을 한 번에 화면으로 복사합니다.
5. **정리 단계**: 사용한 자원들을 모두 정리합니다.

## 각 함수의 역할 정리

- **SelectObject**: "이 도구로 그릴게요" 또는 "이 도화지에 그릴게요"
- **DeleteObject**: "이 도구는 다 썼으니 버릴게요"
- **FillRect**: "이 사각형 영역을 이 브러시로 채울게요"
- **BitBlt**: "이 그림을 저쪽으로 복사할게요"

## 자주 하는 실수들

### 1. 객체를 삭제하지 않는 경우
GDI 객체를 생성한 후 삭제하지 않으면 메모리 누수가 발생합니다. 모든 `Create`에는 반드시 `Delete`가 필요합니다.

### 2. 현재 선택된 객체를 삭제하는 경우
현재 DC에 선택된 객체를 바로 삭제하면 오류가 발생합니다. 반드시 다른 객체를 선택하거나 원래 객체로 복원한 후 삭제해야 합니다.

### 3. 배경을 지우지 않는 경우
새 그림을 그리기 전에 배경을 지우지 않으면, 이전 그림이 남아 있어 화면이 지저분해질 수 있습니다.

### 4. 정리를 잊는 경우
프로그램이 종료될 때까지 GDI 객체와 DC를 정리하지 않으면, 시스템 리소스가 고갈될 수 있습니다.

## 마치며

Windows에서 그래픽 프로그래밍은 처음에는 복잡해 보일 수 있지만, `SelectObject`, `DeleteObject`, `FillRect`, `BitBlt`의 기본 개념과 역할을 이해하면 대부분의 그래픽 작업을 처리할 수 있습니다.

이 네 가지 함수는 마치 미술 수업에서 배우는 기본 기술과 같습니다. 캔버스와 도구를 준비하고, 배경을 지우고, 원하는 그림을 그리고, 작품을 전시하고, 마지막으로 정리하는 과정과 유사합니다.

이러한 기본 개념을 토대로 더 복잡한 그래픽 작업에도 도전해 보죠..!