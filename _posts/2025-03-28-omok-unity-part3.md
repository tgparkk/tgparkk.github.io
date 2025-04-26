---
layout: post
title: "Unity로 오목 만들기 – Part 3: 승리조건, Awake() 함수, NullReferenceException 해결"
date: 2025-03-28
categories: gamedev
tags: [c##, game, unity, 오목, 게임, 유니티, 씨샵]
excerpt: "모바일 오목게임, 유니티 게임, Awake() 함수"
comments: true
---


---

# Unity 오목 게임 개발 일지 – 승리조건, Awake() 함수, NullReferenceException 해결

**2025-03-25**

안녕하세요!  
오늘은 Unity로 오목 게임을 개발하면서 겪은 세 가지 중요한 이슈에 대해 공유하려고 합니다. 바로 **승리조건 기능구현**, **Awake() 함수 이해**, 그리고 **NullReferenceException 해결**입니다. 각각의 주제에 대해 구체적인 코드와 해결 방법을 함께 살펴보겠습니다.

---

## 1. 승리조건 기능구현

오목 게임에서 가장 핵심적인 로직은 **돌이 연속 5개 놓였을 때 승리**를 판단하는 것입니다.  
이를 위해 각 돌이 놓일 때마다 4가지 방향(가로, 세로, 대각선 ↘, 대각선 ↗)으로 연속된 돌의 개수를 세는 함수를 구현했습니다.

### 핵심 코드 예시

```csharp
public void OnStonePlaced(Vector2Int gridPos, int player)
{
    if (CheckWin(gridPos, player))
    {
        GameOver(player);
    }
    else
    {
        // 예: 턴 전환 및 UI 업데이트
    }
}

bool CheckWin(Vector2Int pos, int player)
{
    // 4가지 방향: 가로, 세로, 두 대각선
    Vector2Int[] directions = {
        new Vector2Int(1, 0),
        new Vector2Int(0, 1),
        new Vector2Int(1, 1),
        new Vector2Int(1, -1)
    };

    foreach (Vector2Int dir in directions)
    {
        int count = 1;
        // 한쪽 방향으로 연속된 돌 수
        count += CountStonesInDirection(pos, dir, player);
        // 반대 방향으로 연속된 돌 수
        count += CountStonesInDirection(pos, -dir, player);

        if (count >= 5)
            return true;
    }
    return false;
}

int CountStonesInDirection(Vector2Int start, Vector2Int dir, int player)
{
    int count = 0;
    Vector2Int pos = start + dir;
    while (boardManager.IsValid(pos) && boardManager.GetBoardValue(pos) == player)
    {
        count++;
        pos += dir;
    }
    return count;
}
```

이 코드를 통해 플레이어가 돌을 놓을 때마다 승리 조건이 만족되는지 자동으로 체크하고, 조건이 충족되면 게임 종료 이벤트를 호출합니다.

---

## 2. Awake() 함수 이해

Unity에서 **Awake()** 함수는 MonoBehaviour 스크립트가 활성화되기 전에 호출되는 초기화 함수입니다.  
이 함수는 다음과 같은 특징을 가지고 있습니다:

- **초기화 타이밍:**  
  Awake()는 게임 오브젝트가 활성화되기 전에 한 번 호출됩니다. 이를 통해 다른 컴포넌트나 스크립트가 초기화되기 전에 자신의 변수를 설정할 수 있습니다.

- **한 번만 호출:**  
  각 스크립트 인스턴스에 대해 한 번 호출되므로, 다른 초기화 작업과 의존성을 처리할 때 매우 유용합니다.

### Awake() 함수 사용 예시

```csharp
public class BoardManager : MonoBehaviour
{
    public GameManager gameManager;

    void Awake()
    {
        // Inspector에 gameManager가 할당되지 않았다면 자동으로 찾습니다.
        if (gameManager == null)
            gameManager = FindObjectOfType<GameManager>();

        // 보드 크기 계산 등 초기 설정 작업
        SpriteRenderer sr = GetComponent<SpriteRenderer>();
        Vector2 boardWorldSize = sr.bounds.size;
        cellSize = boardWorldSize.x / (boardSize - 1);
        origin = (Vector2)transform.position - boardWorldSize * 0.5f;
    }
}
```

위 예시처럼 Awake() 함수를 사용하면 다른 스크립트 간의 의존성을 해결하고, 실행 전에 필수 변수들을 초기화할 수 있습니다.

---

## 3. NullReferenceException 해결

개발 초반에 자주 발생하는 문제 중 하나는 **NullReferenceException**입니다.  
이번 프로젝트에서는 BoardManager에서 `gameManager` 참조가 제대로 연결되지 않아 발생하는 오류가 있었습니다.

### 문제 분석 및 해결

**문제 원인:**  
BoardManager 스크립트 내에서 `gameManager.OnStonePlaced(...)`를 호출할 때, `gameManager`가 null인 상태였기 때문입니다.

**해결 방법:**  
1. **Inspector 연결:**  
   - Hierarchy에서 `BoardManager` 오브젝트를 선택한 후, Inspector의 `GameManager` 슬롯에 실제 GameManager GameObject를 드래그하여 할당합니다.
2. **자동 연결 코드 추가:**  
   - Awake() 함수에서 아래와 같이 `FindObjectOfType<GameManager>()`를 사용하여 자동으로 연결되도록 합니다.
   
   ```csharp
   void Awake()
   {
       if (gameManager == null)
           gameManager = FindObjectOfType<GameManager>();
       // 나머지 초기화 작업...
   }
   ```

이 두 가지 방법을 통해 NullReferenceException 문제를 해결할 수 있었습니다.

---

## 결론

오늘은 오목 게임에서 **승리조건 기능구현**을 위한 로직을 작성하고, **Awake() 함수**의 역할과 사용법을 이해하며, **NullReferenceException 해결** 방법에 대해 알아보았습니다.  
이런 기초적인 문제들을 해결해 나가면서 게임 개발의 밑거름을 다지는 과정은 매우 중요합니다.  
다음 단계에서는 승리 시 애니메이션 효과나 게임 재시작 기능 등 추가적인 사용자 경험 개선 작업에 도전해 보려고 합니다.