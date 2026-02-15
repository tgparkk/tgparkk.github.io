---
layout: post
title: "[2] 주식 단타 전략 소개 – 한국인 독자를 위한 짧은 매매"
date: 2026-02-02
categories: [stock]
tags: [stock, 주식, 단타, 전략, 스캘핑, 돌파, 갭, 모멘텀, 볼륨, VWAP, 평균회귀, ORB]
excerpt: "단타에 초점을 두고, 웹에서 전략을 탐색하고 KIS API로 구현 가능한지 확인하는 방식으로 정리했습니다. 돌파·갭·모멘텀·볼륨·VWAP·평균 회귀·시초가 범위 돌파(ORB) 요약과 구현 가능 여부 표를 담았습니다."
comments: true
---

[지난 글](/stock/2026/02/01/stock-auto-trading-series-intro.html)에서 자동매매 시리즈 흐름을 소개했습니다. 이번 글에서는 첫 번째 주제인 **전략 종류**를 다룹니다.

**단타**에 초점을 두고, **두 가지 방식**으로 정리했습니다. 하나는 웹에서 단타·스캘핑 전략을 탐색한 것이고, 다른 하나는 각 전략이 **한국투자증권(KIS) API**로 구현 가능한지 확인한 것입니다.

---

## 왜 단타인가?

**단타**는 짧은 기간 안에 사고 파는 매매를 통틀어 이르는 말입니다. 보유 기간에 따라 **며칠 단위**, **하루 안에 청산하는 당일매매**, **수 분~수 초처럼 아주 잠깐 보유하는 스캘핑** 등 여러 형태가 있습니다. 스캘핑은 구조가 너무 복잡해서 이 글에서는 제외하겠습니다.

한국인 투자자 중에는 "빨리 결과를 보고 싶다"는 성향이 있습니다. 장기 투자보다 **짧은 기간 안에 매매를 마치는 단타**에 관심을 갖는 분이 많죠.

- **장점**: 자금 회전이 빠르고, 당일 손절·익절로 리스크를 끊을 수 있습니다.
- **주의점**: 수수료·세 부담이 상대적으로 크고, 감정과 욕심에 휘둘리기 쉽습니다. 원칙대로 손절·익절하는 습관이 중요합니다.

---

## 단타 전략 소개 (웹 탐색 결과 반영)

웹에서 단타·스캘핑 관련 자료를 탐색해, 자주 쓰이는 전략 일곱 가지를 골라 요약했습니다.

**차트 보는 법**

- **녹색 ▲ + "매수"**: 진입 시점
- **빨간 ▼ + "매도"**: 청산 시점
- **파란 실선**: 진입가
- **초록 실선**: 목표가 (익절 케이스)
- **빨간 실선**: 손절가

전략마다 **익절 케이스**와 **손절 케이스** 두 개의 차트로 나누었습니다.

---

### 1. 돌파 전략 (Breakout)

주가가 **저항선** 또는 **지지선**을 **거래량과 함께** 넘어설 때 진입합니다. 진입 시그널 예: 종가 기준 저항선 돌파, 돌파일 거래량이 평소 대비 20% 이상 증가. 가짜 돌파(False Breakout)에 유의하고, 손절선을 정해 두는 것이 좋습니다.

**차트에서 보면** – **빨간 점선(저항선)**과 **초록 점선(지지선)** 사이에서 가격이 움직이다가 저항을 뚫고 올라가는 흐름과, 그때 거래량이 늘어나는지 확인하면 됩니다.

- **왜 매수했는지**: 횡보 구간에서 저항선을 **거래량 증가와 함께** 상향 돌파한 봉에서 매수 신호가 났기 때문입니다.
- **왜 익절했는지** (아래 익절 차트): 돌파 후 상승이 이어져 목표가 또는 이익 실현 구간에 도달했기 때문에 청산했습니다.
- **왜 손절했는지** (아래 손절 차트): 돌파 직후 가격이 다시 저항 아래로 떨어지는 **가짜 돌파**가 되어, 미리 정한 손절선에 걸려 청산했습니다.

**익절 케이스**

![돌파 – 익절](/assets/images/stock/strategy-breakout-tp.png)

**손절 케이스**

![돌파 – 손절](/assets/images/stock/strategy-breakout-sl.png)

> **익절/손절 기준 예시**
> - **손절**: 돌파 레벨 바로 아래(매수) 또는 위(매도), 직전 지지·저항선 기준 -2% 내외
> - **익절**: 패턴 높이(채널 폭)만큼 투영, 또는 R:R 최소 1:2 이상
> - **확인**: 거래량이 평균 대비 20% 이상 증가할 때만 "진짜" 돌파로 간주
> - 참고: [Investopedia](https://www.investopedia.com/articles/trading/08/trading-breakouts.asp), [Axi](https://www.axi.com/int/blog/education/breakout-trading-strategy)

### 2. 갭 전략 (Gap)

**전일 종가와 당일 시가** 사이에 벌어진 갭을 이용합니다. 갭 메우기(시가~전일 종가 구간에서 반등) 또는 갭 돌파(갭 방향으로 추가 상승·하락) 시 진입합니다. 갭의 원인(호재·악재)을 확인하는 것이 중요합니다.

**차트에서 보면** – **회색 점선**으로 표시한 **갭 구간**(전일 종가~당일 시가) 위·아래로 가격이 움직일 때를 노립니다.

- **왜 매수했는지**: 갭 상승으로 전일 대비 시가가 크게 올랐고, 갭 위쪽으로 가격이 이어져 나가 **갭 돌파**가 확인되어 매수했습니다.
- **왜 익절했는지** (아래 익절 차트): 갭 돌파 후 상승이 지속되어 목표 수익 구간에 도달했기 때문에 익절했습니다.
- **왜 손절했는지** (아래 손절 차트): 갭 후 반등이 오지 않고 가격이 갭 구간 아래로 무너지며 **갭 메우기 실패**로 보였기 때문에 손절선에서 청산했습니다.

**익절 케이스**

![갭 – 익절](/assets/images/stock/strategy-gap-tp.png)

**손절 케이스**

![갭 – 손절](/assets/images/stock/strategy-gap-sl.png)

> **익절/손절 기준 예시**
> - **손절**: 갭 구간 안쪽(갭 상승 시 갭 저점 아래), trailing stop -8% (숏은 -4%)
> - **익절**: R:R 1:2~1:3 목표, 또는 모멘텀 지표(RSI 등) 약해질 때
> - **진입 타이밍**: 장 시작 후 1시간 대기 → 범위 형성 후 돌파 시 진입
> - 참고: [StockCharts](https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/gap-trading-strategies), [Capital.com](https://capital.com/en-int/learn/trading-strategies/gap-trading)

### 3. 모멘텀 전략 (Momentum)

**추세의 지속성**을 활용합니다. 강한 상승·하락 흐름이 이어질 것이라 보고, 이동평균 기울기·RSI·MACD 같은 지표로 과열 구간을 확인한 뒤 진입합니다. 추세 반전 시 손실이 커질 수 있으므로 이탈 타이밍을 정해 두는 것이 좋습니다.

**차트에서 보면** – **보라색 추세선**(저점 연결)을 따라 가격이 한 방향으로 이어질 때 진입합니다.

- **왜 매수했는지**: 상승 추세가 이어지는 구간에서 **추세 지속**을 전제로, 저점을 이은 추세선 위에서 매수했습니다.
- **왜 익절했는지** (아래 익절 차트): 추세가 계속 올라 목표 구간에 도달했거나, 일정 수익을 확보한 뒤 청산했습니다.
- **왜 손절했는지** (아래 손절 차트): 추세가 꺾이면서 **추세 반전**이 보였고, 손절선 또는 추세선 이탈 구간에서 청산했습니다.

**익절 케이스**

![모멘텀 – 익절](/assets/images/stock/strategy-momentum-tp.png)

**손절 케이스**

![모멘텀 – 손절](/assets/images/stock/strategy-momentum-sl.png)

> **익절/손절 기준 예시**
> - **손절**: 직전 스윙 저점 아래, 또는 ATR 2배, 넓게는 -15~20%
> - **익절**: ATR 1.5배 도달, 직전 고점 도달, 또는 절반 익절 후 trailing stop
> - **R:R**: 최소 2:1 목표, 모멘텀 캔들 극단점에 손절 설정
> - 참고: [ForexTester](https://forextester.com/blog/momentum-trading-strategies/), [WarriorTrading](https://www.warriortrading.com/momentum-day-trading-strategy/)

### 4. 거래량 급증 전략 (Volume Spike)

**평소 대비 거래량이 급증**한 구간을 신호로 씁니다. 볼륨 스파이크 후 가격이 돌파하거나 반전 패턴을 보일 때, 다른 지표(OBV, VWAP 등)와 함께 확인하며 진입합니다. 일시적 대량 거래에 속지 않도록 패턴을 꼭 확인하는 것이 좋습니다.

**차트에서 보면** – **주황 점선**이 거래량 급증(스파이크) 봉을 가리킵니다. 그때 가격 방향을 확인하며 진입합니다.

- **왜 매수했는지**: 평소보다 **거래량이 급증**한 봉에서 가격이 상승 방향으로 움직여, 돌파 또는 반전 신호로 보고 매수했습니다.
- **왜 익절했는지** (아래 익절 차트): 스파이크 이후 가격이 상승을 이어가 목표 수익에 도달했기 때문에 익절했습니다.
- **왜 손절했는지** (아래 손절 차트): 거래량 급증 후 가격이 **역방향으로 급락**해 일시적 대량 매도로 보였고, 손절선에서 청산했습니다.

**익절 케이스**

![거래량 급증 – 익절](/assets/images/stock/strategy-volume-spike-tp.png)

**손절 케이스**

![거래량 급증 – 손절](/assets/images/stock/strategy-volume-spike-sl.png)

> **익절/손절 기준 예시**
> - **손절**: 스파이크 봉 저점 아래, 또는 지지선 아래 (ATR 기반도 가능)
> - **익절**: 다음 저항선 도달, R:R 1:2 목표
> - **확인**: 거래량이 20일 평균 대비 50% 이상 증가 + 가격 방향 일치 시 신뢰도 ↑
> - 참고: [Luxalgo](https://www.luxalgo.com/blog/volume-spikes-timing-trades-with-precision/), [DotNetTutorials](https://dotnettutorials.net/lesson/volume-spike-trading-strategy/)

### 5. VWAP 전략 (VWAP)

**당일 거래량 가중 평균 가격(VWAP)**을 기준선으로 삼습니다. 가격이 VWAP을 상향 돌파하며 모멘텀이 확인될 때, 또는 VWAP으로 되돌림 후 지지가 확인될 때 진입합니다. 장 마감에 가까울수록 VWAP이 왜곡될 수 있어, 단타 위주로 쓰는 것을 권합니다.

**차트에서 보면** – **청록색 실선(VWAP)**을 기준으로 가격이 VWAP 위로 올라가며 터치 후 지지받을 때 매수 구간으로 봅니다.

- **왜 매수했는지**: 가격이 **VWAP을 상향 돌파**한 뒤, VWAP 근처로 되돌아왔다가 다시 지지받으며 올라가는 모습을 보고 매수했습니다.
- **왜 익절했는지** (아래 익절 차트): VWAP 위에서 상승이 이어져 목표가에 도달했기 때문에 익절했습니다.
- **왜 손절했는지** (아래 손절 차트): VWAP 위 구간이 깨지고 가격이 **VWAP 아래로 이탈**하며 하락이 이어져, 손절선에서 청산했습니다.

**익절 케이스**

![VWAP – 익절](/assets/images/stock/strategy-vwap-tp.png)

**손절 케이스**

![VWAP – 손절](/assets/images/stock/strategy-vwap-sl.png)

> **익절/손절 기준 예시**
> - **손절**: VWAP 바로 아래/위 (ATR 0.5배 또는 호가 단위 2~3틱), 너무 타이트하면 조기 청산 위험
> - **익절**: VWAP 편차 밴드(±1~2 표준편차), 직전 고점/저점, 또는 trailing stop
> - **진입**: VWAP 상향 돌파 후 되돌림 → 지지 확인 시, 거래량 동반 필수
> - 참고: [Luxalgo](https://www.luxalgo.com/blog/vwap-entry-strategies-for-day-traders/), [Schwab](https://www.schwab.com/learn/story/how-to-use-volume-weighted-indicators-trading)

### 6. 평균 회귀 (Mean Reversion)

가격이 **이동평균이나 일정 구간 평균에서 너무 멀어지면 다시 평균 쪽으로 돌아온다**는 가정으로 매매합니다. 과매수·과매도 구간(예: RSI 70 이상, 30 이하)에서 반대 방향으로 진입하거나, Bollinger Bands 상·하단 터치 후 평균선 복귀를 노립니다. 추세가 강할 때는 평균으로 돌아오기 전에 더 멀어질 수 있으므로, 횡보 구간에서 쓰는 것이 유리합니다.

**차트에서 보면** – **주황색 실선(이동평균)**에서 가격이 벗어났다가 다시 평균선 쪽으로 되돌아오는 구간에서 복귀 방향으로 진입합니다.

- **왜 매수했는지**: 가격이 이동평균선 **아래로 크게 떨어진 구간**에서, 평균선까지 **반등할 것**을 기대하며 매수했습니다. (평균 회귀는 "너무 떨어지면 반등, 너무 오르면 하락"을 노리는 전략입니다.)
- **왜 익절했는지** (아래 익절 차트): 가격이 평균선 근처로 복귀하며 목표 수익 구간에 도달했기 때문에 익절했습니다.
- **왜 손절했는지** (아래 손절 차트): 평균선으로의 **복귀 없이 추가 하락**이 이어져 평균 회귀 가정이 깨졌고, 손절선에서 청산했습니다.

**익절 케이스**

![평균 회귀 – 익절](/assets/images/stock/strategy-mean-reversion-tp.png)

**손절 케이스**

![평균 회귀 – 손절](/assets/images/stock/strategy-mean-reversion-sl.png)

> **익절/손절 기준 예시**
> - **손절**: 넓게 설정 (ATR 1~2배, 스윙 고점/저점 바깥) – 타이트하면 승률 급락
> - **익절**: 이동평균선 도달 시 절반 익절, 나머지는 평균선 돌파 시 청산
> - **주의**: 평균 회귀는 "손실을 버티고, 이익을 빨리 확정"하는 구조 – 추세장에서는 위험
> - 참고: [TradingWithRayner](https://www.tradingwithrayner.com/mean-reversion-trading-strategy/), [QuantifiedStrategies](https://www.quantifiedstrategies.com/mean-reversion-trading-strategy/)

### 7. 시초가 범위 돌파 (ORB, Opening Range Breakout)

**장 시작 후 일정 시간**(예: 9:00~9:30) 동안 형성된 **고가·저가 범위**를 위나 아래로 이탈할 때 진입합니다. 그 구간을 당일의 첫 지지·저항으로 보고, 돌파 방향으로 추세가 이어질 것이라 보는 방식입니다. 단타·데이트레이딩에서 자주 쓰이며, 거래량이 함께 증가할 때 신호를 더 신뢰합니다.

**차트에서 보면** – **남색 점선**이 시초가 구간의 **고가·저가(ORB 범위)**를 나타냅니다. 그 박스를 위나 아래로 뚫고 나갈 때 진입합니다.

- **왜 매수했는지**: 장 초반 형성된 **시초가 범위(ORB)**를 **상단으로 돌파**했고, 돌파와 함께 거래량이 늘어나 추세 지속을 기대하며 매수했습니다.
- **왜 익절했는지** (아래 익절 차트): ORB 상단 돌파 후 상승이 이어져 목표가에 도달했기 때문에 익절했습니다.
- **왜 손절했는지** (아래 손절 차트): ORB 돌파 직후 가격이 **범위 안으로 다시 들어오는 가짜 돌파**가 되어, 손절선에서 청산했습니다.

**익절 케이스**

![ORB – 익절](/assets/images/stock/strategy-orb-tp.png)

**손절 케이스**

![ORB – 손절](/assets/images/stock/strategy-orb-sl.png)

> **익절/손절 기준 예시**
> - **손절**: 범위 반대쪽 끝 (보수적), 또는 범위 50% 지점 (공격적)
> - **익절**: 손절 거리의 1.5~2배, 또는 trailing stop
> - **범위 설정**: 장 시작 후 5분/15분/30분 중 선택 (한국 시장은 9:00~9:15 또는 9:00~9:30 권장)
> - **승률**: S&P100 5만 건 분석 결과 약 52~53% – 필터링이 중요
> - 참고: [FluxCharts](https://www.fluxcharts.com/articles/trading-strategies/common-strategies/opening-range-breakout), [TradeThatSwing](https://tradethatswing.com/opening-range-breakout-strategy-up-400-this-year/)

---

## KIS API로 구현 가능 여부 (API 확인 결과 반영)

각 전략이 **한국투자증권 API**로 구현 가능한지, 필요한 데이터·주문과 API 제공 기능을 맞춰 보았습니다. 인증(토큰·해시키)과 개발 환경은 [한국투자증권 API로 자동 매매 시스템 개발하기 – 1](/stock/2025/03/08/auto-stock-1-init.html) 게시글을 참고하면 됩니다.

| 전략 | 필요한 것 (요약) | KIS API 구현 가능 여부 |
|------|------------------|------------------------|
| 돌파 | 일봉·분봉(고점·저점), 거래량, 주문(시장가/지정가) | **가능** – 일봉·분봉·거래량 조회 API, 국내주식 주문 API로 구현 가능 |
| 갭 | 전일 종가, 당일 시가, 주문 | **가능** – 일봉(종가), 당일 시세·시가 조회, 주문 API로 구현 가능 |
| 모멘텀 | 일봉·분봉(이동평균·RSI·MACD 계산용), 주문 | **가능** – 일봉·분봉 조회 후 지표 계산, 주문 API로 구현 가능 |
| 거래량 급증 | 일봉·분봉(거래량·가격), 주문 | **가능** – 일봉·분봉·거래량 조회, 주문 API로 구현 가능 |
| VWAP | 당일 분봉 또는 실시간(거래량·가격), 주문 | **가능** – 분봉·거래량 조회로 VWAP 계산, 실시간은 웹소켓 활용 시 가능(제한 있음) |
| 평균 회귀 | 일봉·분봉(가격·이동평균·RSI·볼린저 등), 주문 | **가능** – 일봉·분봉 조회 후 지표 계산, 주문 API로 구현 가능 |
| 시초가 범위 돌파 (ORB) | 당일 분봉(시초가 후 N분 고·저), 주문 | **가능** – 당일 분봉 조회로 시초가 구간 고·저 산출, 돌파 시 주문 API로 구현 가능 |

**공통**: 국내주식 **일봉·분봉·거래량**은 REST API로 조회할 수 있고, **주문**은 국내주식 주문 API(시장가·지정가 등)와 해시키로 처리할 수 있습니다. **실시간 시세**가 필요하면 웹소켓을 쓰면 되고, **Rate Limit**과 인증(토큰·해시키)은 KIS 문서와 위 1편 글을 참고해 지키면 됩니다.

**스캘핑(초단타)**처럼 **호가창·체결강도**를 쓰는 전략은, KIS API에서 호가·체결 관련 데이터 제공 범위에 따라 **일부 제한**이 있을 수 있습니다. 일봉·분봉 기반 단타는 위 표처럼 모두 구현 가능합니다.

---

## 마무리

이번 글에서는 단타에 초점을 두고, **웹에서 전략을 탐색**한 결과와 **KIS API로 구현 가능한지 확인**한 결과를 합쳐 일곱 가지 전략(돌파, 갭, 모멘텀, 거래량 급증, VWAP, 평균 회귀, 시초가 범위 돌파)을 소개했습니다. 다음 편에서는 **전략을 고르는 방법**(백테스트, 리스크, 자신의 스타일)과 **자동매매 기초·구현**으로 이어질 예정입니다.

**참고 – 블로그 내 글**

- [주식 자동매매 시리즈 소개 – 한국투자증권 API](/stock/2026/02/01/stock-auto-trading-series-intro.html) – 시리즈 흐름
- [초단기 매매 5종 전략 총정리](/stock/2025/05/11/five-strategies.html) – 돌파·갭·모멘텀·볼륨·VWAP 상세
- [돌파 전략 실전 정리](/stock/2026/01/31/breakout-strategy-practical-summary.html) – 돌파 전략 이론·진입·청산
- [한국투자증권 API로 자동 매매 시스템 개발하기 – 1](/stock/2025/03/08/auto-stock-1-init.html) – 개발 환경, API 인증(토큰·해시키)

**참고 – 외부 자료 (전략별 익절/손절 기준)**

- **돌파**: [Investopedia – Trading Breakouts](https://www.investopedia.com/articles/trading/08/trading-breakouts.asp), [Axi – Breakout Strategy](https://www.axi.com/int/blog/education/breakout-trading-strategy)
- **갭**: [StockCharts – Gap Trading](https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/gap-trading-strategies), [Capital.com – Gap Trading](https://capital.com/en-int/learn/trading-strategies/gap-trading)
- **모멘텀**: [ForexTester – Momentum Strategies](https://forextester.com/blog/momentum-trading-strategies/), [WarriorTrading – Momentum Day Trading](https://www.warriortrading.com/momentum-day-trading-strategy/)
- **거래량 급증**: [Luxalgo – Volume Spikes](https://www.luxalgo.com/blog/volume-spikes-timing-trades-with-precision/), [DotNetTutorials – Volume Spike](https://dotnettutorials.net/lesson/volume-spike-trading-strategy/)
- **VWAP**: [Luxalgo – VWAP Entry](https://www.luxalgo.com/blog/vwap-entry-strategies-for-day-traders/), [Schwab – Volume-Weighted Indicators](https://www.schwab.com/learn/story/how-to-use-volume-weighted-indicators-trading)
- **평균 회귀**: [TradingWithRayner – Mean Reversion](https://www.tradingwithrayner.com/mean-reversion-trading-strategy/), [QuantifiedStrategies – Mean Reversion](https://www.quantifiedstrategies.com/mean-reversion-trading-strategy/)
- **ORB**: [FluxCharts – Opening Range Breakout](https://www.fluxcharts.com/articles/trading-strategies/common-strategies/opening-range-breakout), [TradeThatSwing – ORB Strategy](https://tradethatswing.com/opening-range-breakout-strategy-up-400-this-year/)

**참고 – 학술 자료**

- *FinLLM-B: When Large Language Models Meet Financial Breakout Trading* (NAACL 2025) – LLM 기반 돌파 신호 분석
- *Opening Range Breakout Stock Trading Algorithmic Model* (IJCI, 2016) – ORB 알고리즘 설계
- *Bootstrap Testing of Trading Strategies in Emerging Balkan Stock Markets* (E+M, 2017) – 돌파/채널 규칙 통계 검정
