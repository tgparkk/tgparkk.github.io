# Blog Content Discovery Redesign

**Date**: 2026-04-01
**Status**: Approved
**Goal**: 과거 좋은 글이 묻히지 않도록 콘텐츠 탐색/발견 경험을 개선한다

---

## Problem

- 홈페이지에 최신 글 6개만 노출되어, 과거에 작성된 양질의 글이 묻힘
- 방문자가 관심 있는 글을 발견할 경로가 부족
- 시리즈/연재물인지 인지하기 어려워 중간에 이탈

## Design Decision

Designer B(포스트 내 컨텍스트 내비게이션) + Designer C(좋아요 기반 자동 큐레이션 패널)를 조합한다.

---

## 1. Post Page Changes (1순위)

### 1.1 Series Banner

- **위치**: 포스트 제목 바로 위
- **형태**: `"C++ 비동기 서버 시리즈 — 3편 / 총 7편"` 배너
- **조건**: frontmatter에 `series` 필드가 있는 포스트에만 표시
- **반응형**: PC/모바일 모두 표시
- **구현**: Jekyll Liquid로 같은 series 값을 가진 포스트를 수집하여 순서 계산

**Frontmatter 예시:**
```yaml
series: "C++ 비동기 서버"
series_order: 3
```

### 1.2 Sticky Table of Contents Sidebar

- **위치**: 포스트 본문 우측, sticky (top: 80px)
- **내용**: H2/H3 기반 자동 생성 목차
- **인터랙션**: 스크롤 시 현재 섹션 하이라이트 (Intersection Observer)
- **레이아웃**: `grid-template-columns: 1fr 260px` (본문 + 사이드바)
- **조건**: H2+H3 합계 3개 이상인 경우에만 표시
- **모바일 (768px 미만)**: 사이드바 숨김, 제목 아래 접힘 토글(`<details>`)로 대체

### 1.3 "Next Read" Cards

- **위치**: 포스트 하단, 기존 "Related Posts" 섹션을 대체
- **레이아웃**: 2열 카드
  - 왼쪽: 같은 시리즈 이전/다음 글 (series가 없으면 같은 카테고리 이전/다음)
  - 오른쪽: 태그 기반 다른 카테고리 추천 1개
- **구현**: Jekyll Liquid로 빌드 타임에 생성 (API 호출 없음)

---

## 2. Homepage Changes (2순위)

### 2.1 Curation Panel (Sidebar)

- **위치**: 홈 메인 콘텐츠 우측
- **표시 조건**: 뷰포트 1100px 이상
- **레이아웃**: `grid-template-columns: 1fr 300px`
- **구성**: 3개 탭 (JS 탭 전환, 페이지 이동 없음)

**탭 1: 인기글 (기본 선택)**
- 좋아요 수 Top 5 자동 정렬
- 각 항목: 순위 뱃지 + 제목 + 좋아요 수 + 카테고리
- 데이터: GitHub Gist 좋아요 데이터를 JS 비동기 fetch
- 로딩 중 스켈레톤 UI 표시

**탭 2: 시리즈**
- `series` frontmatter가 있는 포스트를 그룹화
- 시리즈명 + 총 편수 + 누적 좋아요
- "1편부터 시작하기" 링크

**탭 3: 주제별**
- 카테고리 아이콘 + 이름 + 글 수
- 클릭 시 카테고리 페이지 이동

### 2.2 Mobile (1100px 미만)

- 사이드바 숨김
- 포스트 그리드 아래에 전체폭 섹션으로 배치
- 탭 UI 유지, 가로 전체폭

---

## 3. Changes NOT Made

- 히어로 섹션: 현행 유지
- 카테고리 아이콘 네비게이션: 현행 유지
- 헤더/푸터: 현행 유지
- 검색 모달 (Ctrl+K): 현행 유지
- 다크/라이트 모드: 현행 유지 (새 컴포넌트도 CSS 변수 활용)

---

## 4. Technical Notes

### Jekyll/Liquid Constraints
- 모든 시리즈/카테고리 데이터는 빌드 타임에 Liquid로 생성
- 인기글 순위만 런타임 JS (Gist API fetch)
- 새 Liquid 데이터: `series` frontmatter 기반 그룹핑

### CSS
- 기존 CSS 변수 체계 (`--primary-color`, `--card-bg` 등) 활용
- 다크모드 자동 대응 (`[data-theme="dark"]`)
- 브레이크포인트: 1100px (홈 사이드바), 768px (포스트 사이드바/모바일)

### New Files Expected
- `_includes/series-banner.html` — 시리즈 배너 partial
- `_includes/toc-sidebar.html` — 목차 사이드바 partial
- `_includes/next-read.html` — 다음 읽을 글 카드 partial
- `_includes/curation-panel.html` — 홈 큐레이션 패널 partial
- `assets/js/toc.js` — 목차 스크롤 추적
- `assets/js/curation.js` — 큐레이션 패널 탭 전환 + Gist fetch

### Modified Files Expected
- `_layouts/post.html` — 사이드바 레이아웃 + 시리즈 배너 + next-read 카드
- `_layouts/home.html` — 사이드바 레이아웃 + 큐레이션 패널
- `assets/css/main.css` — 새 컴포넌트 스타일 추가

---

## 5. Implementation Priority

| Phase | Scope | Complexity |
|-------|-------|------------|
| 1 | 포스트: 시리즈 배너 + sticky 목차 사이드바 | Medium |
| 2 | 홈: 3탭 큐레이션 패널 (Gist 연동) | Medium-High |
| 3 | 포스트: "다음 읽을 글" 하단 카드 | Low |
