# 돌파 전략 조사 실행 계획

## 🎯 조사 목표

돌파 전략에 대한 심층 조사를 통해:
1. 이론적 배경 완전히 이해
2. 실전 적용 가능한 구체적 진입/청산 조건 수립
3. 한국 시장 특화 분석
4. 백테스팅을 통한 성과 검증
5. 실전 적용 방안 도출

---

## 📅 조사 일정 (2주 계획)

### 1주차: 이론 및 자료 수집

#### Day 1-2: 학술 자료 조사
- [x] Google Scholar/OpenAlex에서 "breakout trading strategy" 검색 (FinLLM-B 포함 20편 메타데이터 확보)
- [x] OA 논문 PDF 3건 다운로드 (FinLLM-B, ORB 알고리즘 모델, 발칸 Bootstrap 검정)
- [ ] 최근 5년 논문 10개 이상 수집
- [ ] 핵심 논문 3-5개 선별하여 상세 읽기
- [ ] 주요 발견사항 조사 노트에 기록
- [x] arXiv:2402.07536 (FinLLM-B) 다운로드 및 요약

#### Day 3-4: 서적 및 전문 자료
- [ ] "Technical Analysis of the Financial Markets" (John J. Murphy) 읽기
- [ ] "Encyclopedia of Chart Patterns" (Thomas Bulkowski) 관련 부분 읽기
- [ ] "트레이딩 전략서 태쏘의 주식 실전단타" 재검토
- [ ] Investopedia, TradingView 등 온라인 자료 정리
  - [x] Investopedia: The Anatomy of Trading Breakouts 요약
  - [ ] Investopedia: Breakout Trader (유형별 정리)
  - [x] Axi: What is a Breakout Trading Strategy? 요약

#### Day 5: 한국 시장 특화 자료
- [ ] 국내 학위 논문 검색 (RISS, KCI)
- [ ] 증권사 리서치 리포트 검색 (한국시장 기술적 분석)
- [ ] 네이버 카페, 블로그 등 실전 경험담 수집

### 2주차: 데이터 수집 및 분석

#### Day 6-7: 데이터 수집
- [ ] FinanceDataReader로 코스피 상위 100개 종목 일봉 데이터 수집
- [ ] 최근 3년 데이터 확보
- [ ] 데이터 품질 검증

#### Day 8-10: 백테스팅 구현
- [ ] 돌파 전략 백테스팅 코드 작성
- [ ] 다양한 파라미터 테스트
- [ ] 성과 지표 계산

#### Day 11-12: 분석 및 정리
- [ ] 결과 분석 및 해석
- [ ] 조사 노트 업데이트
- [ ] 최종 보고서 작성

---

## 📚 구체적 조사 자료 목록

### 학술 논문 (우선순위 순)

#### 1순위: 필수 읽기
1. **"Breakout Trading Strategies: Evidence from Stock Markets"**
   - 검색: Google Scholar → "breakout strategy stock market"
   - 예상 저널: Journal of Financial Markets, Review of Finance
   - 조사 포인트: 승률, 수익률, 거래량 영향

2. **"Volume-Confirmed Breakouts: A Statistical Analysis"**
   - 검색: Google Scholar → "volume breakout trading"
   - 조사 포인트: 거래량 기준, 최적 비율

3. **"Support and Resistance Levels in Technical Analysis"**
   - 검색: Google Scholar → "support resistance levels trading"
   - 조사 포인트: 지지/저항선 유효성, 돌파 확률

#### 2순위: 참고 자료
4. **"False Breakouts in Stock Trading"**
   - 검색: Google Scholar → "false breakout trading"
   - 조사 포인트: 가짜 돌파 패턴, 대응 방법

5. **"Momentum and Breakout Strategies: A Comparative Study"**
#### 추가 확보 논문 (2026-01-04)
- **"FinLLM-B: When Large Language Models Meet Financial Breakout Trading"** (NAACL 2025) – 돌파 감지용 LLM, 발자국 데이터셋 아이디어 확보.
- **"Opening Range Breakout Stock Trading Algorithmic Model"** (IJCI 2016) – ORB 기술지표 결합 모델, 개장 범위 기반 리스크 룰 참고.
- **"Bootstrap Testing of Trading Strategies in Emerging Balkan Stock Markets"** (E+M 2017) – TRB/채널 돌파 룰 Reality Check + SPA 부트스트랩 절차 확보.
   - 검색: Google Scholar → "momentum breakout comparison"
   - 조사 포인트: 모멘텀과 돌파 전략 비교

### 국내 학위 논문

#### 검색 사이트
- **RISS (Research Information Sharing Service)**: http://www.riss.kr
- **KCI (Korean Citation Index)**: https://www.kci.go.kr

#### 검색 키워드
- "돌파 전략"
- "기술적 분석 전략"
- "차트 패턴 분석"
- "지지 저항선"

#### 예상 논문 주제
- "한국 주식시장에서의 기술적 분석 전략 수익성 연구"
- "차트 패턴 기반 매매 전략의 효과성 분석"
- "코스피와 코스닥의 기술적 분석 전략 비교"

### 전문 서적

#### 필수 읽기
1. **"Technical Analysis of the Financial Markets" - John J. Murphy**
   - Chapter: Chart Patterns, Support and Resistance
   - 페이지: [확인 필요]
   - 핵심 내용: 돌파 패턴, 지지/저항 이론

2. **"Encyclopedia of Chart Patterns" - Thomas N. Bulkowski**
   - Chapter: Triangle Patterns, Rectangle Patterns
   - 핵심 내용: 패턴별 돌파 승률 통계

3. **"트레이딩 전략서 태쏘의 주식 실전단타" - 태쏘**
   - 재검토: 돌파 전략 관련 부분
   - 실전 팁 정리

#### 참고 서적
4. **"Algorithmic Trading" - Ernest P. Chan**
   - Chapter: Breakout Strategies Implementation
   - 핵심 내용: 백테스팅 방법론

5. **"Quantitative Trading" - Ernest P. Chan**
   - Chapter: Technical Analysis Strategies
   - 핵심 내용: 정량적 분석 방법

### 온라인 리소스

#### Investopedia
- [x] "The Anatomy of Trading Breakouts"
  - URL: https://www.investopedia.com/articles/trading/08/trading-breakouts.asp
  - 조사 포인트: 기본 개념, 진입/청산 조건

- [ ] "Breakout Trader: Overview, Types, and Example"
  - URL: https://www.investopedia.com/terms/b/breakouttrader.asp
  - 조사 포인트: 돌파 트레이더 유형

#### Axi
- [x] "What is a Breakout Trading Strategy & How to Trade It?"
  - URL: https://www.axi.com/int/blog/education/breakout-trading-strategy
  - 조사 포인트: 보조 지표 활용, 리스크 관리, 리테스트 전략

#### IG International
- [ ] "Breakout Trading Strategy: A Guide for Traders"
  - URL: https://www.ig.com/en/trading-strategies/what-is-a-breakout-trading-strategy-and-how-do-you-trade-with-it-230619
  - 조사 포인트: 단계별 프로세스, 차트 예시, 실전 적용

#### TradingView
- [ ] 커뮤니티에서 "breakout strategy" 검색
- [ ] 실제 차트 예시 수집
- [ ] 트레이더 경험담 정리

#### QuantConnect
- [ ] 오픈소스 돌파 전략 코드 검토
- [ ] 백테스팅 결과 분석

#### YouTube / 강의
- [ ] "Breakout Trading Strategy" 검색
- [ ] 실전 예시 영상 시청
- [ ] 핵심 내용 정리

### 한국 시장 특화 자료

#### 증권사 리서치 리포트
- **키움증권**: 기술적 분석 리포트
- **NH투자증권**: 차트 분석 리포트
- **한국투자증권**: 기술적 지표 분석

#### 커뮤니티
- **네이버 카페**: 주식 관련 카페에서 "돌파" 검색
- **디스코드/텔레그램**: 트레이더 그룹 경험담
- **블로그**: 개인 투자자 실전 경험

---

## 🔍 조사 시 체크리스트

### 각 자료를 읽을 때 확인할 사항

#### 논문/서적
- [ ] 전략의 정의와 원리
- [ ] 진입/청산 조건 (구체적 수치)
- [ ] 성과 지표 (승률, 수익률, 샤프비율)
- [ ] 리스크 분석
- [ ] 실전 적용 팁
- [ ] 한국 시장 관련 언급 여부

#### 온라인 자료
- [ ] 실전 사례
- [ ] 차트 예시
- [ ] 트레이더 경험담
- [ ] 실패 사례 및 교훈

#### 데이터/백테스팅
- [ ] 테스트 기간
- [ ] 테스트 종목
- [ ] 파라미터 설정
- [ ] 성과 결과
- [ ] 한계점

---

## 📝 조사 노트 작성 방법

### 자료별 기록 형식

#### 논문
```markdown
### [논문 제목] - [저자] ([연도])
- **저널**: [저널명]
- **핵심 내용**: [3-5줄 요약]
- **주요 발견**:
  1. [발견 1]
  2. [발견 2]
- **인용할 만한 내용**: "[인용구]"
- **한국 시장 적용 가능성**: [예/아니오/부분적] - [이유]
- **평가**: ⭐⭐⭐⭐⭐
```

#### 서적
```markdown
### [서적명] - [저자]
- **출판사**: [출판사]
- **관련 챕터**: [챕터명]
- **핵심 내용**: [요약]
- **실전 팁**: [팁 1, 팁 2]
- **평가**: ⭐⭐⭐⭐⭐
```

#### 온라인 자료
```markdown
### [제목] - [사이트명]
- **URL**: [링크]
- **핵심 내용**: [요약]
- **차트/예시**: [설명]
- **저장 위치**: [파일명/스크린샷]
```

---

## 🎯 다음 단계

### 즉시 시작할 수 있는 작업

1. **Investopedia 2편 완독 마무리**
   - "Breakout Trader: Overview, Types, and Example" 요약
   - 돌파 유형별 장단점 표 작성

2. **IG International 가이드 정리**
   - 단계별 프로세스/차트 캡처
   - 국내 장세 적용 시 주의점 메모

3. **RISS에서 국내 논문 검색**
   ```
   검색어: "돌파 전략" OR "기술적 분석 전략"
   필터: 최근 5년
   목표: 한국 시장 특화 논문 2-3개 찾기
   ```

4. **TradingView 커뮤니티 탐색**
   - "breakout strategy" 검색
   - 실제 차트 예시 수집
   - 트레이더 경험담 정리

5. **FinLLM-B 후속 실험 아이디어 작성**
   - 한국 호가 데이터 수집 범위 정의
   - S1/S2/S3 태스크 라벨링 방법 초안

---

## ✅ 주간 체크리스트

### 1주차 말 검토
- [ ] 학술 논문 5개 이상 읽기
- [ ] 전문 서적 2권 이상 읽기
- [ ] 온라인 자료 10개 이상 수집
- [ ] 조사 노트에 핵심 내용 기록
- [ ] 한국 시장 특화 자료 수집

### 2주차 말 검토
- [ ] 데이터 수집 완료
- [ ] 백테스팅 코드 작성 완료
- [ ] 성과 지표 계산 완료
- [ ] 최종 조사 노트 업데이트
- [ ] 블로그 포스트 작성 준비

---

**시작일**: 2025-12-20  
**목표 완료일**: 2026-01-03 (2주 후)

