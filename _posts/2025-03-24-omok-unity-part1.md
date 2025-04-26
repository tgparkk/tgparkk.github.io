---
layout: post
title: "Unity로 오목 만들기 – Part 1: 환경 설정 및 기획"
date: 2025-03-24
categories: gamedev
tags: [c##, game, unity, 오목, 게임, 유니티, 씨샵]
excerpt: "모바일 오목게임, 유니티 게임 ."
comments: true
---

---

## 🎯 프로젝트 소개

저는 앞으로 언리얼 엔진으로 고성능 게임 개발에 도전할 계획입니다.  
그 첫걸음으로 비교적 간단한 **오목 게임**을 Unity로 만들어 보며 게임 개발 워크플로우를 익히고자 합니다.

---

## 🎮 왜 Unity인가?

- **간단함:** 언리얼 엔진보다 진입 장벽이 낮아 초보자가 빠르게 시작하기에 적합  
- **빠른 프로토타이핑:** 오목 같은 2D 게임을 구현하기에 충분한 기능 제공  

---

## 🛠️ 개발 환경 세팅

### 1️⃣ Unity 설치

1. Unity Hub 다운로드 → [Unity 다운로드](https://unity.com/download)  
2. Unity Hub 실행 → **Installs → Add version → Unity 2023.3 LTS** 선택  
3. Windows/macOS Build Support 체크 후 설치  

### 2️⃣ Rider 설치

- JetBrains Rider 다운로드 → [Rider 다운로드](https://www.jetbrains.com/rider/)
- C# 코드 작성과 Unity 통합 지원이 우수하여 선택  

---


## 🎮 기능 정의 (Scope)

1. **보드 그리기** (15×15 그리드)  
2. **돌 놓기** (클릭 시 돌 생성)  
3. **승리 판정** (가로·세로·대각선 5연속 체크)  

---

## 📊 다이어그램



### 클래스 다이어그램

```mermaid
classDiagram
    class BoardManager {
        +int boardSize
        +GameObject blackStonePrefab
        +GameObject whiteStonePrefab
        +float cellSize
        +Vector2 boardOrigin
        -int[,] board
        -bool isBlackTurn
        +void Start()
        +void Update()
        +Vector2Int WorldToGrid(Vector2)
        +Vector3 GridToWorld(Vector2Int)
        +bool IsInBounds(Vector2Int)
        +void PlaceStone(Vector2Int)
        +bool IsValid(Vector2Int)
        +int GetBoardValue(Vector2Int)
    }

    class GameManager {
        +BoardManager boardManager
        +Text statusText
        -bool isGameOver
        +void Start()
        +void OnStonePlaced(int, Vector2Int)
        -bool CheckWin(Vector2Int, int)
        -int CountDirection(Vector2Int, Vector2Int, int)
    }

    class Stone {
        +int player
        +Vector2Int gridPos
    }

    class AIPlayer {
        <<empty>>
    }

    BoardManager --> Stone : instantiates
    BoardManager --> GameManager : notifies via OnStonePlaced
    GameManager --> BoardManager : queries board state
```

### 플로우차트

```mermaid
flowchart TD
    Start([게임 시작])
    Click[클릭 대기]
    Place[돌 생성]
    Check[승리 판정?]
    Win[승리 알림]
    Switch[턴 교체]
    End([게임 종료])

    Start --> Click
    Click --> Place
    Place --> Check
    Check -->|Yes| Win --> End
    Check -->|No| Switch --> Click
```
