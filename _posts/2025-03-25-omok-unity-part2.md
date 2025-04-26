---
layout: post
title: "Unity로 오목 만들기 – Part 2: 기본 기능 구현 및 씬 추가"
date: 2025-03-25
categories: gamedev
tags: [c##, game, unity, 오목, 게임, 유니티, 씨샵]
excerpt: "모바일 오목게임, 유니티 게임, 씬(scene)."
comments: true
---



## 🎬 Unity에서 “씬(Scene)”이란?

Unity의 **씬(Scene)** 은 게임 안의 하나의 “화면” 또는 “단계(Level)”를 뜻합니다. 씬은 **모든 게임 오브젝트(GameObject)** — 카메라, 배경, UI, 캐릭터, 스크립트 등 — 를 담는 컨테이너 역할을 하며, 서로 다른 씬을 불러오는 것으로 게임 내 메뉴, 레벨, 설정 화면 등을 전환할 수 있습니다. 예를 들어 **OpeningScene** 은 메인 메뉴 화면, **GameScene** 은 실제 오목 플레이 화면이 됩니다.

---

## 📝 오늘 작업 요약

### 1️⃣ OpeningScene(메인 메뉴) 구성
- 바둑알 배치
- Canvas → Background Image, Panel(반투명 팝업), “게임 시작” Button 배치  
- Panel RectTransform: Center Anchor, Size=300×200, Alpha=200  

## ✨ 추가 작업: 바둑알(Grid Snap) 정확히 배치하기

게임의 핵심은 “클릭한 위치가 바둑판의 교차점(격자)에 정확히 스냅” 되어야 한다는 점입니다. 오늘은 **BoardManager** 스크립트를 통해 이를 구현한 과정을 정리합니다.

---

### 🎯 구현 목표

- **월드 좌표 → 격자 좌표 → 다시 월드 좌표** 로 변환  
- 클릭 시 가장 가까운 교차점에 돌이 놓이도록  

---

### 🛠️ BoardManager 핵심 코드

```csharp
void Awake()
{
    // SpriteRenderer에서 실제 보드 크기 읽어오기
    SpriteRenderer sr = GetComponent<SpriteRenderer>();
    Vector2 boardSizeWorld = sr.bounds.size;

    // 15×15 오목판 → 칸 간격(cellSize)은 (가로 길이 ÷ (boardSize‑1))
    cellSize = boardSizeWorld.x / (boardSize - 1);
    
    // 보드 왼쪽 하단(origin) 좌표 계산
    origin = (Vector2)transform.position - boardSizeWorld * 0.5f;
}

public Vector2Int WorldToGrid(Vector2 worldPos)
{
    Vector2 local = worldPos - origin;
    return new Vector2Int(
        Mathf.RoundToInt(local.x / cellSize),
        Mathf.RoundToInt(local.y / cellSize)
    );
}

public Vector3 GridToWorld(Vector2Int gridPos)
{
    return (Vector3)(origin + new Vector2(gridPos.x, gridPos.y) * cellSize);
}
```

---

### 🔄 클릭→격자 스냅 흐름

1. **Update()** 에서 마우스 클릭 감지  
2. `Camera.ScreenToWorldPoint()` → **월드 좌표** 획득  
3. `WorldToGrid()` → 가장 가까운 **정수 격자 좌표** 계산  
4. `GridToWorld()` → 격자 중앙의 **월드 위치** 반환  
5. `Instantiate(prefab, spawnPos, Quaternion.identity)` 로 돌 생성  

---

### ✅ 테스트 확인

- Console 로그로 `(x, y)` 격자 좌표 출력 → 올바른 숫자가 찍히는지 확인  
- 클릭할 때마다 돌이 정확히 **격자 교차점 중앙**에 놓여야 함  
- 이미 돌이 있는 칸은 배치되지 않도록 배열 상태 검사  

---

### ✍️ 배운 점

| 문제 | 해결책 |
|------|---------|
| 클릭 위치 오차 | `Mathf.RoundToInt` 로 반올림 |
| 보드 이미지 크기와 좌표 불일치 | SpriteRenderer.bounds.size 사용 |
| Origin 계산 실수 | Transform.position – bounds*0.5f |

---

### 2️⃣ UIManager 스크립트 작성  
```csharp
public class UIManager : MonoBehaviour
{
    public string gameSceneName = "GameScene";
    public void StartGame() => SceneManager.LoadScene(gameSceneName);
}
```
- Button OnClick → UIManager.StartGame() 연결  

### 3️⃣ Build Profiles → Scene List 설정  
- File → Build Profiles → Scene List → Open Scene List  
- “➕” 클릭 → OpeningScene.unity, GameScene.unity 추가  
- OpeningScene(Index 0), GameScene(Index 1) 순서 정렬  

### 4️⃣ 씬 이름 변경 & 참조 업데이트  
- OpeningScene → MainMenu.unity, GameScene → PlayScene.unity  
- Scene List Editor, UIManager.gameSceneName, Button OnClick 모두 새 이름으로 재연결  

---

## ✅ 오늘 해결한 문제

| 이슈 | 원인 | 해결 |
|-------|-------|---------|
| 씬 로드 오류 | Scene List에 씬 미등록 | Scene List Editor 통해 추가 |
| Button 이벤트 누락 | UIManager 참조 없음 | Inspector에서 연결 |
| NullReferenceException | 변수 할당 누락 | Inspector 슬롯에 드래그 |

---

## ▶️ 다음 목표

1. 씬 전환 페이드 애니메이션 추가  
2. 게임 씬 내 승리 메시지 UI 구현  
3. AI 대전 로직 개발  

오늘 “메인 메뉴 → 게임 씬” 전환 기능을 완전히 완성했습니다. 내일부터는 플레이 경험 개선과 AI 완성에 집중하겠습니다!