---
layout: post
title: "트레이딩 시스템에 머신러닝을 적용한 기술 여정"
date: 2025-11-30
categories: machine-learning
tags: [machine-learning, trading, python, lightgbm, 머신러닝, 트레이딩, kis, 한국투자증권]
excerpt: "한국투자증권 KIS API를 활용한 자동화 트레이딩 시스템 개발 경험을 공유합니다. 초기에는 기술적 지표와 패턴 분석만으로 신호를 생성했지만, 시뮬레이션 결과 정확도가 50%대에 머물렀습니다. 머신러닝을 도입하여 신호 정확도를 70%대까지 개선한 기술적 구현 과정을 다룹니다."
comments: true
---

한국투자증권 KIS API로 자동매매 시스템을 만들면서 겪은 시행착오를 공유합니다. 처음에는 기술적 지표와 패턴 분석으로 신호를 생성했는데, 백테스팅 결과가... **정확도 50%대**였어요. 동전 던지기랑 비슷한 수준이더라고요. ㅠㅠ

그래서 머신러닝을 도입했고, 정확도를 **70%대까지** 올릴 수 있었습니다. 어떻게 했는지 공유할게요!

> ⚠️ **주의**: 이 글은 ML 기술 개발 경험을 공유하는 것이며, 투자 권유나 수익 보장이 아닙니다.

---

## 왜 ML이 필요했나?

### 패턴 기반 시스템의 한계

제가 만든 시스템은 이런 패턴을 찾아요:

```
1️⃣ 상승 구간: 가격 상승 + 거래량 감소 추세
2️⃣ 하락 구간: 이등분선 위에서 조정
3️⃣ 지지 구간: 거래량 급감, 캔들 크기 축소
4️⃣ 돌파 구간: 거래량 증가 + 양봉 돌파 → 신호 생성
```

이론적으로는 괜찮아 보이는데, 실제로 돌려보니 **정확도가 50~60%**밖에 안 나왔어요.

#### 규칙 기반 시스템의 문제점

기존에는 이렇게 하드코딩된 규칙을 사용했습니다:

```python
# 기존 방식: 하드코딩된 규칙
def should_signal(pattern):
    if (pattern.uptrend_gain > 3.0 and
        pattern.volume_ratio < 0.5 and
        pattern.breakout_volume > threshold):
        return True  # 신호 생성
    return False
```

**문제가 뭐였냐면:**
- ❌ **정량화의 어려움**: "상승률 3% 이상"이 모든 상황에 맞을까?
- ❌ **복합 변수 미반영**: 시간대, 시장 상황, 여러 비율의 조합을 고려 불가
- ❌ **False Positive 과다**: 패턴은 맞는데 실제론 안 먹히는 신호가 너무 많음
- ❌ **개선의 한계**: 규칙을 하나씩 수정하는 방식은 너무 느리고 비효율적

### ML 도입하기

핵심 질문은 이거였어요: **"패턴은 맞는데, 어떤 패턴이 실제로 먹히는 거지?"**

이 질문에 답하기 위해 머신러닝을 도입했습니다:

```python
# ML 방식: 데이터 기반 학습
def evaluate_signal(pattern_features) -> (bool, float):
    """
    26개의 패턴 특성을 입력받아 신호 유효성 예측

    Returns:
        (신호 허용 여부, 예측 정확도)
    """
    ml_prob = model.predict(pattern_features)  # 0.0 ~ 1.0
    return ml_prob >= 0.5, ml_prob  # 50% 이상이면 허용
```

**ML의 장점:**
- ✅ **자동 패턴 발견**: 사람이 못 찾은 복합 규칙을 학습
- ✅ **확률적 판단**: 신호 강도를 수치로 평가 가능
- ✅ **데이터 기반 개선**: 새로운 데이터로 자동 성능 향상
- ✅ **빠른 의사결정**: 실시간 추론 속도 < 0.001초

### 결과 비교

| 지표 | 규칙 기반 | ML 기반 | 개선율 |
|------|-----------|---------|--------|
| **정확도** | 50.6% | **72.9%** | +44% |
| **평균 성능** | 기준 | **1.87배** | +87% |
| **오류 감소** | 49.4% | **27.1%** | -45% |

정확도가 50%에서 73%로 올라갔어요. 체감상 완전히 달라지더라고요!

---

## LightGBM을 선택한 이유

트레이딩 시스템에는 여러 ML 기법을 적용할 수 있는데요. 저는 **LightGBM**을 선택했습니다.

### 왜 LightGBM?

여러 모델을 테스트해봤어요:

| 모델 | 정확도 | 학습 시간 | 추론 속도 | 해석성 | 평가 |
|------|------|----------|----------|--------|------|
| **LightGBM** | **72%** | **1분** | **0.001초** | ⭐⭐⭐ | ✅ **선택** |
| XGBoost | 71% | 3분 | 0.002초 | ⭐⭐⭐ | ⚠️ 근소한 차이 |
| Random Forest | 68% | 5분 | 0.01초 | ⭐⭐ | ❌ 느림 |
| Neural Network | 65% | 10분 | 0.001초 | ⭐ | ❌ 과적합 |
| Logistic Regression | 58% | 10초 | 0.0001초 | ⭐⭐⭐⭐ | ❌ 성능 부족 |

**LightGBM 선택 이유:**

**1. 표 형태 데이터에 최적화**

제 데이터는 이런 구조예요:

| uptrend_gain | decline_pct | breakout_volume | hour | ... | label |
|--------------|-------------|-----------------|------|-----|-------|
| 3.52 | 1.23 | 162154 | 9 | ... | 1 (성공) |
| 2.87 | 0.95 | 98432 | 10 | ... | 0 (실패) |

Tree 기반 모델이 이런 데이터에 강하거든요!

**2. 실시간 추론 속도**

```python
# 속도 비교 (1000회 추론)
LightGBM:      0.12초  ✅
XGBoost:       0.18초
Random Forest: 1.20초  ❌ (실시간 사용 불가)
LSTM:          0.50초
```

장중에 초단위로 판단해야 하니까 속도가 정말 중요했어요.

**3. 해석 가능성**

```python
# 어떤 특성이 중요한지 분석 가능
feature_importance = model.feature_importance()

결과:
1. volume_ratio_support_to_uptrend: 0.18  ← 가장 중요!
2. breakout_body: 0.15
3. hour: 0.12  ← 시간대도 중요
4. uptrend_gain: 0.10
```

모델이 왜 이렇게 판단했는지 알 수 있으니 디버깅하기도 좋았어요.

**4. 과적합 방지**

```python
# Early Stopping으로 과적합 방지
model = lgb.train(
    params,
    train_set,
    num_boost_round=1000,
    valid_sets=[valid_set],
    callbacks=[lgb.early_stopping(50)]  # 50라운드 개선 없으면 중단
)
```

딥러닝보다 과적합 위험이 훨씬 낮더라고요.

---

## 데이터 수집과 특성 설계

### 자동 데이터 수집 시스템

ML 모델의 성능은 **데이터 품질**에 달려있어요. 그래서 자동 수집 시스템을 만들었습니다:

```python
# 1. 실시간 패턴 로깅
class PatternDataLogger:
    """시스템 동작 중 발생한 패턴을 DB에 자동 저장"""

    def log_pattern(self, code, signal_strength):
        pattern_data = {
            'stage_1': {...},    # 1단계 특성
            'stage_2': {...},    # 2단계 특성
            'stage_3': {...},    # 3단계 특성
            'stage_4': {...}     # 4단계 특성
        }
        self.db.insert(pattern_data)
```

```python
# 2. 일일 결과 데이터 생성 (매일 자동 실행)

1. DB에서 당일 패턴 추출
2. 시뮬레이션으로 성공/실패 여부 계산
3. CSV 파일로 저장

결과 예시:
code, time, feature_1, feature_2, ..., label
XXXX, 09:30, 3.52, 1.23, ..., 1 (성공)
YYYY, 10:15, 2.87, 0.95, ..., 0 (실패)
```

**핵심**: 패턴만 저장하는 게 아니라, **실제 결과(성공/실패)**를 함께 기록하는 게 중요해요!

### 특성 엔지니어링

패턴의 4단계 구조를 **26개 숫자**로 변환했습니다.

**주요 특성 설계:**

**1. 상승 구간 특성 (5개)**

```python
features = {
    'uptrend_candles': 7,           # 상승 봉 개수
    'uptrend_gain': 3.52,           # 상승률 (%)
    'uptrend_max_volume': 250000,   # 최대 거래량
    'uptrend_avg_body': 0.85,       # 평균 몸통 크기 (%)
    'uptrend_total_volume': 1500000 # 총 거래량
}
```

**2. 비율 특성 (5개) - 가장 중요!**

절대값보다 **비율**이 훨씬 중요하더라고요:

```python
features = {
    # 하락 시 거래량이 상승 대비 얼마나 줄었는가?
    'volume_ratio_decline_to_uptrend': 0.48,  # ← 높으면 위험

    # 지지 시 거래량이 상승 대비 얼마나 줄었는가?
    'volume_ratio_support_to_uptrend': 0.32,  # ← 낮을수록 좋음!

    # 돌파 시 거래량이 상승 대비 얼마나 증가했는가?
    'volume_ratio_breakout_to_uptrend': 0.65,  # ← 높을수록 좋음

    # 상승 대비 하락이 얼마나 완만했는가?
    'price_gain_to_decline_ratio': 2.86,

    # 지지 기간이 하락 대비 얼마나 길었는가?
    'candle_ratio_support_to_decline': 1.25
}
```

**3. 시간 특성 (6개)**

```python
features = {
    'hour': 9,                      # 시간
    'minute': 30,                   # 분
    'time_in_minutes': 570,         # 분 단위 시간
    'is_morning': 1,                # 오전 여부
    'signal_type': 1,               # STRONG_BUY=1
    'confidence': 85                # 신뢰도
}
```

분석해보니 **오전(9~11시) 신호가 더 정확**하더라고요!

---

## 가장 큰 도전과제

### 실시간 vs 시뮬레이션 불일치

**문제**: 시뮬레이션에서는 잘 작동하는데, 실시간 시스템에서 예측값이 달라지는 거예요!

```
실시간 시스템: ML 39.9% → 차단
시뮬레이션:   ML 52.3% → 통과

🔍 원인: 특성 추출 로직의 미묘한 차이
```

#### 원인 찾기

디버깅 스크립트로 추적했더니:

```python
# 발견된 차이점:
실시간: uptrend_gain = 3.52  (percentage)
시뮬:   uptrend_gain = 352000 (원 단위)

# → 단위 불일치!
```

아... 단위를 다르게 쓰고 있었던 거죠. ㅠㅠ

#### 해결 방법

특성 추출 로직을 완전히 통일했어요:

```python
def extract_features_from_pattern(self, pattern: Dict) -> pd.DataFrame:
    """
    시뮬레이션과 실시간 거래 양쪽 데이터 구조 지원

    지원 구조:
    1. pattern_stages: {1_uptrend, 2_decline, 3_support, 4_breakout}
    2. debug_info: {uptrend, decline, support, breakout}
    """

    # 🔄 두 구조 모두 지원
    pattern_stages = pattern.get('pattern_stages', {})
    debug_info = pattern.get('debug_info', {})

    # 상승 구간: 우선순위로 탐색
    uptrend = pattern_stages.get('1_uptrend', debug_info.get('uptrend', {}))

    # 필드명 통일 (gain_pct vs price_gain)
    uptrend_gain = self._safe_float(
        uptrend.get('gain_pct', uptrend.get('price_gain', 0.0))
    )

    # 안전한 형변환
    def _safe_float(self, value, default=0.0):
        if isinstance(value, str):
            # "3.52%" → 3.52, "162,154" → 162154
            value = value.replace(',', '').replace('%', '')
        return float(value) if value else default
```

### 메모리 리플레이로 검증

완벽한 재현성을 위해, 실시간 메모리 데이터를 덤프해서 재실행했어요:

```python
# 1. 실시간 시스템 동작 중: 메모리 데이터 덤프
# memory_data_YYYYMMDD_HHMMSS.txt

# 2. 이후: 덤프 데이터로 시뮬 재실행
python replay_from_memory.py memory_data_YYYYMMDD_HHMMSS.txt

# 3. 결과 비교
실시간 시스템: 09:30 → ML 39.9% (차단)
리플레이:      09:30 → ML 39.9% (차단) ✅ 완전 일치!
```

**검증 결과:**
- ✅ 실시간 vs 시뮬 예측값 일치율: **100%**
- ✅ 오차 범위: **±0.1% 이내**
- ✅ 실제 시스템에서 ML 필터 **정상 작동 확인**

이거 해결하는 데 이틀 걸렸어요... ㅎ

---

## 모델 관리 전략

ML 모델은 **시장 상황이 바뀌면** 성능이 떨어질 수 있어요. 그래서 관리 시스템을 만들었습니다.

### 일일 자동 업데이트

```bash
# 매일 장 마감 후 자동 실행 (Cron)
# 0 16 * * 1-5 /path/to/daily_update.sh

Step 1: 당일 패턴 데이터 수집
→ 데이터 수집 스크립트 실행
→ CSV 파일 생성

Step 2: 최근 60일 데이터로 재학습
→ 학습 스크립트 실행
→ 60일치 데이터 통합 → 학습

Step 3: 새 모델 검증
→ 테스트셋 정확도 > 65% 확인
→ Feature Importance 분석

Step 4: 모델 배포 여부 결정
→ 통과: 새 모델로 업데이트
→ 실패: 이전 모델 유지 + 알림
```

### 모델 버전 관리

```python
# 모델 저장 시 메타데이터 포함
model_data = {
    'model': lgb_model,
    'label_encoder': le,
    'feature_names': feature_names,
    'version': f'v_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
    'train_score': 0.756,
    'test_score': 0.729,
    'train_date': datetime.now().strftime("%Y-%m-%d"),
    'data_days': 60
}

with open('model.pkl', 'wb') as f:
    pickle.dump(model_data, f)
```

버전별로 백업을 남겨두니까 문제 생기면 바로 롤백할 수 있어서 좋더라고요.

### 성능 모니터링

```python
# 매 실행 후 정확도 계산
class MLPerformanceTracker:
    def __init__(self):
        self.predictions = []
        self.actuals = []

    def log_result(self, ml_prob, success):
        self.predictions.append(ml_prob)
        self.actuals.append(1 if success else 0)

    def get_weekly_stats(self):
        """주간 성능 리포트"""
        return {
            'accuracy': accuracy_score(self.actuals,
                                      [1 if p >= 0.5 else 0 for p in self.predictions]),
            'avg_prob_success': np.mean([p for p, a in zip(self.predictions, self.actuals) if a == 1]),
            'avg_prob_fail': np.mean([p for p, a in zip(self.predictions, self.actuals) if a == 0])
        }
```

```python
# 성능 저하 시 텔레그램 알림
if weekly_accuracy < 0.60:
    send_telegram_alert(
        f"⚠️ ML 모델 성능 저하 감지!\n"
        f"주간 정확도: {weekly_accuracy:.1%}\n"
        f"재학습 권장"
    )
```

알림 시스템 덕분에 성능 저하를 바로 알 수 있어요.

---

## 배운 점들

### 1. 데이터 파이프라인이 80%

> "Garbage In, Garbage Out"

좋은 모델보다 **좋은 데이터**가 훨씬 중요하더라고요:

- ✅ 실시간 시스템 동작 중 패턴 데이터 자동 수집
- ✅ 성공/실패 결과 정확히 라벨링
- ✅ 60일 이상의 충분한 학습 데이터 확보
- ✅ 데이터 품질 검증 자동화

### 2. 실전 환경 검증 필수

시뮬레이션 성능 ≠ 실전 성능

- ✅ 메모리 데이터 리플레이로 100% 재현성 확보
- ✅ 실시간 vs 시뮬 특성 추출 로직 완전 통일
- ✅ 단위 불일치, 필드명 차이 등 세밀한 디버깅

이거 안 했으면 큰일 날 뻔했어요...

### 3. 단순함의 힘

복잡한 딥러닝보다 **LightGBM + 잘 설계된 특성**이 나았어요:

- ✅ 학습 시간: 1분
- ✅ 추론 속도: 0.001초/샘플
- ✅ 해석 가능성: 특성 중요도 분석 가능
- ✅ 유지보수 용이

처음엔 LSTM도 시도했는데, 과적합되고 학습도 느려서 포기했습니다. ㅎ

### 4. 지속적인 개선

시장은 계속 변하니까 모델도 함께 진화해야 해요:

- ✅ 일일 자동 재학습
- ✅ 성능 모니터링 및 알림
- ✅ 모델 버전 관리
- ✅ A/B 테스팅 및 롤백 전략

---

## 향후 개선 계획

### 1. 앙상블 모델

여러 모델의 예측을 결합해서 안정성을 높이려고 해요:

```python
# LightGBM + XGBoost + CatBoost 앙상블
lgb_prob = lgb_model.predict(features)
xgb_prob = xgb_model.predict(features)
cat_prob = cat_model.predict(features)

final_prob = (lgb_prob * 0.5 + xgb_prob * 0.3 + cat_prob * 0.2)
```

### 2. 온라인 학습 (Online Learning)

실시간으로 모델을 업데이트하는 것도 시도해볼 예정이에요:

```python
# 실행 결과를 즉시 학습 데이터에 추가
from river import linear_model

model = linear_model.LogisticRegression()

# 스트리밍 학습
for features, result in system_results:
    prediction = model.predict_one(features)
    model.learn_one(features, result)  # 즉시 업데이트!
```

---

## 마무리

트레이딩 시스템에 머신러닝을 적용하면서 얻은 성과:

1. ✅ **신호 정확도를 50% → 73%로 향상**
2. ✅ **실시간 vs 시뮬레이션 동기화**
3. ✅ **자동 데이터 수집 및 학습 파이프라인**

가장 중요한 교훈은:

> **"ML 모델보다 데이터 파이프라인이 더 중요하다"**

좋은 데이터 수집 시스템만 있으면, 모델은 자연스럽게 성능이 좋아지더라고요!

---

**⚠️ 면책 조항**

이 글은 ML 기술 개발 경험을 공유하는 **교육 목적**의 기술 블로그입니다.
- 특정 투자 종목이나 전략을 추천하는 것이 아닙니다
- 수익을 보장하거나 투자를 권유하지 않습니다
- 실제 투자 시 발생하는 손실에 대해 책임지지 않습니다
- 투자 판단과 책임은 투자자 본인에게 있습니다

---

## 기술 스택

**개발 환경:**
- Python 3.10+
- 한국투자증권 KIS API
- LightGBM 4.0+
- scikit-learn 1.3+
- pandas, numpy

**주요 컴포넌트:**
- ML 예측기 (특성 추출 및 추론)
- 모델 학습 파이프라인 (Stratified K-Fold)
- 실시간 데이터 로거
- 일일 데이터 수집 스크립트
- 메모리 리플레이 검증 도구
- 자동 업데이트 시스템
