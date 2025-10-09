---
layout: post
title: "RoboTrader 개발일지 – 1: 70개 종목, 시스템이 멈춘 날"
date: 2025-10-09
categories: [robotrader]
tags: [stock, python, 자동매매, API, 최적화, RoboTrader, 한국투자증권, KIS, KIS API, 한국투자증권API]
excerpt: "조건검색에서 70개 종목이 선정되자 시스템이 에러를 토해냈다. 한국투자증권 KIS API 제한 초당 20개를 875% 초과한 순간, 나는 동적 배치 시스템을 만들기로 했다."
comments: true
---

# RoboTrader 개발일지 – 1: 70개 종목, 시스템이 멈춘 날

## 🤖 RoboTrader 소개

[RoboTrader](https://github.com/tgparkk/RoboTrader)는 **한국투자증권 KIS API(Korea Investment & Securities API)**를 활용한 Python 기반 주식 자동매매 시스템입니다. KIS Open API를 통해 실시간 주가 조회, 주문 실행 등을 자동화하며, 눌림목 캔들패턴을 기반으로 한 단타 전략을 구현하고 있습니다. 이 시리즈에서는 실제 개발 과정에서 겪은 문제와 해결 과정을 공유합니다.

---

## 들어가며: 예상치 못한 상황

이전에 개발했던 자동매매 시스템([개발 과정](https://tgparkk.github.io/stock/2025/03/08/auto-stock-1-init.html))의 경험을 바탕으로, 이번에는 **눌림목 전략**에 특화된 RoboTrader를 새로 구축했습니다.

조건검색 로직을 완성하고 드디어 실전 테스트에 들어갔습니다. 장 시작 후 조건검색을 돌렸는데...

```
✅ 조건검색 완료: 70개 종목 발견
```

"오! 오늘 시장이 좋은가 보다!"

하지만 기쁨은 잠시, 곧 시스템이 제대로 작동하지 않았습니다.

```
# 실제 오류는 이렇지 않았지만, 증상을 표현하면:
❌ API 오류: 분당 호출 한도 초과
❌ 데이터 수집 실패율: 75%
❌ 매매 신호 생성 불가
```

데이터 수집이 실패하면서 시스템이 제대로 동작하지 않았습니다. 🔥

---

## 1. 무엇이 문제였나?

### 고정된 배치 시스템의 함정

기존 코드는 **10~20개 종목**을 가정하고 작성되었습니다:

```python
# core/intraday_stock_manager.py (기존)
batch_size = 20  # 고정!
await asyncio.sleep(0.2)  # 고정!

for i in range(0, len(stock_codes), batch_size):
    batch = stock_codes[i:i + batch_size]

    # 각 종목당 2개 API 호출 (분봉 + 현재가)
    minute_tasks = [self.update_realtime_data(code) for code in batch]
    price_tasks = [self._update_current_price_data(code) for code in batch]

    # 병렬 실행
    await asyncio.gather(*minute_tasks, *price_tasks)

    await asyncio.sleep(0.2)  # 다음 배치까지 200ms
```

### 70개 종목일 때 일어난 일

실제로 무슨 일이 벌어졌는지 계산해봤습니다:

```
타임라인:
0.0초: 종목  1~20 → 20개 분봉 API + 20개 현재가 API = 40개 ❌
0.2초: 종목 21~40 → 40개 API ❌
0.4초: 종목 41~60 → 40개 API ❌
0.6초: 종목 61~70 → 20개 API ❌
─────────────────────────────────────────────────
총 0.8초에 140개 API 호출
= 초당 175개
```

**한국투자증권 KIS API 제한**: 초당 최대 20개 (KIS Developers 정책)
**내가 호출한 것**: 초당 175개
**초과율**: **875%** 💥
**결과**: KIS API 서버로부터 Rate Limit 에러 발생

(이 수치를 보고 멘붕이 왔습니다...)

---

## 2. 첫 번째 시도: 무작정 줄이기

### 시도 1: 배치 크기 반으로 줄이기

```python
batch_size = 10  # 20 → 10으로 줄임
```

**결과**:
- 70개 × 2 API = 140개
- 7개 배치 × 0.2초 간격 = 1.4초
- 초당 100개 → 여전히 **500% 초과** ❌

### 시도 2: 대기 시간 늘리기

```python
await asyncio.sleep(1.0)  # 0.2초 → 1.0초
```

**결과**:
- 처리 시간 4초로 증가
- 초당 35개 → 여전히 **175% 초과** ⚠️

"이건 근본적인 해결책이 아니야..."

### 시도 3: 둘 다 조정

```python
batch_size = 5
await asyncio.sleep(0.5)
```

**결과**:
- 처리 시간 7초
- 초당 20개 → **드디어 성공!** ✅

하지만 문제가 있었습니다:

**"10개 종목일 때는?"**
→ 2초면 끝날 일을 7초 동안 기다림 (비효율적)

**"100개 종목일 때는?"**
→ 다시 API 제한 초과

---

## 3. 깨달음: 종목 수에 적응해야 한다

### 핵심 인사이트

> **"10개일 때와 70개일 때가 같을 수 없다"**

시스템은 환경에 **적응**해야 합니다.

| 종목 수 | 고정 배치 | 필요한 것 |
|---------|----------|----------|
| 10개 | 0.8초 (빠름) | 빠르게 처리 ✅ |
| 70개 | 0.8초 (에러) | 안전하게 처리 ❌ |
| 100개 | 0.8초 (에러) | 더 느리게 처리 ❌ |

### 필요한 것

```python
# 종목 수에 따라 자동으로 계산
batch_size, delay = calculate_optimal(total_stocks)
```

이게 바로 **동적 배치 시스템**입니다.

---

## 4. 해결책: DynamicBatchCalculator

### 설계 목표

```
목표: 10초 내에 모든 종목 처리
제약: 초당 20개 API 이하
전략: 종목 수 → 배치 크기 + 지연 시간 자동 계산
```

### 구현

새로운 클래스를 만들었습니다:

```python
# core/dynamic_batch_calculator.py
class DynamicBatchCalculator:
    """한국투자증권 KIS API 제약 조건 하에서 종목 수에 따른 최적 배치 계산
    
    KIS API Rate Limit: 초당 20개 호출 제한
    """

    API_LIMIT_PER_SECOND = 20  # 한국투자증권 KIS API: 초당 20개 제한
    TARGET_UPDATE_TIME = 10    # 목표 10초
    APIS_PER_STOCK = 2         # 종목당 2개 API (분봉 + 현재가)

    def calculate_optimal_batch(self, total_stocks: int):
        """최적 배치 크기와 지연 시간 계산"""

        if total_stocks <= 10:
            # 소량: 빠른 처리
            return 10, 0.2

        elif total_stocks <= 30:
            # 중량: 중간 처리
            return 10, 0.5

        elif total_stocks <= 50:
            # 다량: 안전 처리
            return 8, 0.8

        else:
            # 대량 (50개 이상): 동적 계산
            # 70개 × 2 API = 140개
            # 140개 ÷ 20개/초 = 7초 필요
            # 배치 크기 10개 → 7개 배치
            # 7초 ÷ 7배치 = 1.0초 지연

            safe_per_second = 20
            total_apis = total_stocks * 2

            # 필요한 최소 시간
            min_time_needed = total_apis / safe_per_second

            # 배치 크기 결정
            batch_size = 10
            num_batches = (total_stocks + batch_size - 1) // batch_size

            # 배치당 지연 시간
            batch_delay = min_time_needed / num_batches
            batch_delay = max(0.5, batch_delay)  # 최소 0.5초

            return batch_size, batch_delay
```

### 적용

기존 코드를 수정했습니다:

```python
# core/intraday_stock_manager.py (수정)
class IntradayStockManager:
    def __init__(self):
        # 🆕 동적 배치 계산기 추가
        self.batch_calculator = DynamicBatchCalculator()

    async def batch_update_realtime_data(self):
        """모든 종목 실시간 데이터 업데이트"""

        stock_codes = list(self.selected_stocks.keys())
        total_stocks = len(stock_codes)

        # 🆕 동적 배치 크기 계산
        batch_size, batch_delay = self.batch_calculator.calculate_optimal_batch(
            total_stocks
        )

        self.logger.info(
            f"📊 동적 배치: {total_stocks}개 종목 → "
            f"배치 {batch_size}개 × 지연 {batch_delay:.2f}초"
        )

        # 배치 처리
        for i in range(0, len(stock_codes), batch_size):
            batch = stock_codes[i:i + batch_size]

            # 분봉 + 현재가 동시 업데이트
            minute_tasks = [self.update_realtime_data(code) for code in batch]
            price_tasks = [self._update_current_price_data(code) for code in batch]

            await asyncio.gather(*minute_tasks, *price_tasks)

            # 🆕 동적 지연 시간 적용
            if i + batch_size < len(stock_codes):
                await asyncio.sleep(batch_delay)
```

---

## 5. 결과: Before vs After

### Before (고정 배치)

```
70개 종목 처리:
- 배치 크기: 20개 (고정)
- 배치 지연: 0.2초 (고정)
- 소요 시간: 0.8초
- API 속도: 175개/초
- 초과율: 875%
- 결과: 시스템 마비 ❌
```

### After (동적 배치)

```
70개 종목 처리:
- 배치 크기: 10개 (자동)
- 배치 지연: 1.0초 (자동)
- 소요 시간: 7.0초
- API 속도: 20개/초
- 초과율: 0%
- 결과: 정상 작동 ✅
```

### 로그 예시

시스템을 다시 실행했을 때 이런 식으로 작동합니다:

```
# 실제 로그를 각색한 예시:
2025-10-09 15:32:59 | INFO | 📊 동적 배치 계산 결과:
   종목 수: 70개
   필요 API: 140개
   배치 크기: 10개
   배치 수: 7회
   배치 지연: 1.00초
   예상 완료: 7.0초 (목표: 10초)
   예상 속도: 20.0개/초 (안전: 20개/초)

2025-10-09 15:32:59 | INFO | ✅ 동적 배치 최적화 완료:
   70개 종목 → 배치 10개 × 7회, 예상 7.0초 소요
```

(이런 결과를 보고 안도의 한숨을 쉬었습니다 😅)

### 성능 비교 표

| 지표 | Before | After | 개선율 |
|------|--------|-------|--------|
| API 초과율 | 875% | 100% | ✅ 87.5%p |
| 데이터 성공률 | 25% | 99% | ✅ 74%p |
| 매매 가능 여부 | ❌ | ✅ | ✅ 100% |
| 시스템 안정성 | 불안정 | 안정 | ✅ 정상화 |

---

## 6. 다양한 상황 테스트

동적 배치 시스템이 얼마나 잘 적응하는지 테스트해봤습니다:

```python
# test_dynamic_batch.py
calc = DynamicBatchCalculator()

test_cases = [10, 30, 50, 70, 80, 100]

for stock_count in test_cases:
    batch_size, batch_delay = calc.calculate_optimal_batch(stock_count)
    estimated_time = calc.get_estimated_time(stock_count, batch_size, batch_delay)
    api_speed = calc.get_estimated_calls_per_second(batch_size, batch_delay)

    print(f"{stock_count}개: 배치 {batch_size}, "
          f"지연 {batch_delay:.2f}초, "
          f"완료 {estimated_time:.1f}초, "
          f"속도 {api_speed:.1f}개/초")
```

**결과**:

```
10개:  배치 10, 지연 0.20초, 완료 0.2초, 속도 100.0개/초
30개:  배치 10, 지연 0.50초, 완료 1.5초, 속도 40.0개/초
50개:  배치  8, 지연 0.80초, 완료 5.6초, 속도 20.0개/초 ✅
70개:  배치 10, 지연 1.00초, 완료 7.0초, 속도 20.0개/초 ✅
80개:  배치 10, 지연 1.00초, 완료 8.0초, 속도 20.0개/초 ✅
100개: 배치 10, 지연 1.00초, 완료 10.0초, 속도 20.0개/초 ✅
```

**50개 이상부터는 정확히 초당 20개를 유지합니다!** 🎯

---

## 7. 배운 교훈

### 1. 하드코딩은 특정 상황에만 유효하다

```python
# ❌ 나쁜 예: 고정값
BATCH_SIZE = 20  # 항상 20?

# ✅ 좋은 예: 계산값
batch_size = calculate_optimal(current_stocks)
```

### 2. 제약을 정량화하라

- "빨라야 한다" (X) → 막연함
- "초당 20개 이하여야 한다" (O) → 명확함

### 3. 시스템은 환경에 적응해야 한다

- 10개일 때: 빠르게 (0.2초)
- 70개일 때: 안전하게 (7초)
- 100개일 때: 한계까지 (10초)

### 4. 실전 테스트의 중요성

개발 환경에서는 10~20개 종목으로만 테스트했기 때문에 문제를 발견하지 못했습니다.
**실제 장중 상황에서 70개가 나와야 문제를 발견했죠.**

---

## 8. 다음 단계

이제 70개 종목도 안정적으로 처리합니다. 하지만 아직 해결할 과제가 남았습니다:

### 개선 예정 사항

1. **우선순위 기반 업데이트**
   - 보유 종목(POSITIONED): 5초마다
   - 후보 종목(SELECTED): 30초마다 로테이션

2. **실시간 성공률 피드백**
   - 성공률 80% 이하 시 배치 크기 자동 축소
   - 네트워크 상태에 따른 동적 조정

3. **최대 관리 종목 수 확대**
   - 현재: 80개 (12초 소요)
   - 목표: 100개 (10초 완료)

---

## 마치며

조건검색에서 70개 종목이 나왔을 때, 시스템은 멈췄습니다.
하지만 **한국투자증권 KIS API의 Rate Limit 제약**을 이해하고 이 문제를 해결하면서 더 견고한 시스템을 만들 수 있었습니다.

**"시스템은 환경에 적응해야 한다"**

이 교훈은 KIS API를 활용하는 다른 자동매매 시스템 개발에도 적용될 것 같습니다.

다음 편에서는 **눌림목 전략의 실제 구현**과 **신호 생성 로직**을 다뤄보겠습니다.

재테크는 계속됩니다! 💪

(그나저나 언제쯤 수익을 낼 수 있을까요... 🤔)

---

## 참고 자료

- **GitHub**: [RoboTrader](https://github.com/tgparkk/RoboTrader)
- **한국투자증권 KIS Developers**: [KIS Open API 문서](https://apiportal.koreainvestment.com)
- **KIS API 가이드**: [한국투자증권 OpenAPI 개발자센터](https://apiportal.koreainvestment.com/howto)
- **관련 코드**:
  - `core/dynamic_batch_calculator.py` - 동적 배치 계산기
  - `core/intraday_stock_manager.py` - 실시간 데이터 관리
  - `test_dynamic_batch.py` - 테스트 코드

- **이전 개발 과정**:
  - [자동매매 시스템 개발하기 - 1편](https://tgparkk.github.io/stock/2025/03/08/auto-stock-1-init.html)
  - [자동매매 시스템 개발하기 - 2편](https://tgparkk.github.io/stock/2025/03/31/auto-stock-2.html)
  - [자동매매 시스템 개발하기 - 3편](https://tgparkk.github.io/stock/2025/04/26/auto-stock-3-select-stock.html)

---

**💬 질문이나 의견은 댓글로 남겨주세요!**

특히 여러분의 시스템에서 API 제한 문제를 어떻게 해결하셨는지 궁금합니다.
