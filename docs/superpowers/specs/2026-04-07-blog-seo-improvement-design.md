# Blog SEO Improvement Design

**Date:** 2026-04-07
**Status:** Approved
**Goal:** 기술 블로그 정체성을 유지하면서 SEO/기술적 개선으로 자연 성장, $100/월 목표

## 현황

- 8개월 운영, 53개 포스트, 월 ~249 사용자 / ~500 PV
- AdSense 수익: 총 $4 (8개월)
- 유입: Direct 45%, Google Organic 31%, Naver 12%, Bing 4%, AI검색 4%
- 킬러 콘텐츠: 주식 자동매매 관련 글이 전체 트래픽의 ~50%
- SEO 기본기는 갖춰져 있으나 canonical 태그, 구조화 데이터 등 누락

## Part A: 즉시 코드 수정

### A-1. _config.yml author 정보 추가
- `author`, `avatar`, `github` 필드 추가
- jekyll-seo-tag 플러그인이 자동 활용

### A-2. header.html 메타 태그 보강
- canonical 태그 추가 (중복 콘텐츠 방지)
- `og:site_name`, `og:locale`, `article:published_time` 추가
- `twitter:site`, `twitter:creator` 추가

### A-3. 스크립트 defer 최적화
- AOS, Simple Jekyll Search 등 비필수 스크립트에 `defer` 추가
- Core Web Vitals 개선 → 검색 순위 영향

### A-4. 구조화 데이터 보강
- BlogPosting 스키마에 `mainEntityOfPage` 추가
- 홈페이지에 `WebSite` 스키마 + `SearchAction` 추가

## Part B: 콘텐츠 전략 가이드 (문서)

### B-1. 기존 글 개선
- 대표이미지 없는 36개 포스트 이미지 추가 우선순위
- excerpt 최적화 가이드

### B-2. 신규 글 작성 체크리스트
- 검색량 있는 기술 키워드 찾는 방법
- SEO 효과 높은 포스트 포맷/구조

### B-3. 내부 링크 전략
- 관련 포스트 간 상호 링크 강화
- 시리즈 기능 활용 극대화

### B-4. 검색엔진 등록 체크리스트
- Google Search Console 최적화
- 네이버 서치어드바이저 RSS 등록
- 색인 요청 방법

## 변경하지 않는 것
- 광고 슬롯 수 (현재 3개 유지)
- 블로그 디자인/레이아웃
- 기존 포스트 내용
