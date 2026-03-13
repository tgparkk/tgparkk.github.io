---
layout: post
title: "[6] 전략 끼워넣기 – BaseStrategy 가상함수와 샘플 전략 구현"
date: 2026-03-13
categories: [stock]
tags: [stock, auto-trading, kis-api, python, framework, template, strategy]
excerpt: "C++ 가상함수처럼, BaseStrategy의 빈 틀을 상속받아 나만의 전략을 끼워넣는 과정을 따라갑니다. 폴더 하나 만들고, 메서드 다섯 개 채우면 자동매매가 돌아갑니다."
comments: true
---

[지난 글](/stock/2026/02/21/stock-framework-core-modules.html)에서 KISBroker, FundManager, StrategyLoader를 다뤘습니다. 이번 글에서는 **실제로 전략을 하나 만들어서 프레임워크에 끼워넣는 과정**을 따라갑니다.

핵심 아이디어는 간단합니다. C++에서 가상함수를 오버라이드하듯, Python에서도 **추상 클래스의 빈 메서드를 채우면** 프레임워크가 알아서 호출해줍니다.

---

## 1. C++ 가상함수와 같은 구조

C++를 아시는 분이라면 이 패턴이 익숙할 겁니다:

```cpp
// C++ — 추상 클래스
class BaseStrategy {
public:
    virtual bool on_init() = 0;                    // 순수 가상함수
    virtual Signal generate_signal(string code) = 0;
    virtual void on_order_filled(Order order) {};  // 기본 구현 있음
    virtual void on_market_open() {};
    virtual void on_market_close() {};
};

// 상속받아서 구현
class MyStrategy : public BaseStrategy {
public:
    Signal generate_signal(string code) override {
        // 내 전략 로직
    }
};
```

Python의 ABC(Abstract Base Class)도 **똑같은 역할**입니다:

```python
# Python — 추상 클래스
class BaseStrategy(ABC):
    @abstractmethod
    def generate_signal(self, stock_code, data, timeframe='daily'):
        ...  # 순수 가상함수 — 반드시 구현해야 함

    def on_init(self, broker, data_provider, executor):
        ...  # 기본 구현 있음 — 필요하면 오버라이드

    def on_market_open(self):
        ...  # 기본 구현 있음

    def on_order_filled(self, order):
        ...  # 기본 구현 있음

    def on_market_close(self):
        ...  # 기본 구현 있음
```

| C++ | Python | 의미 |
|-----|--------|------|
| `= 0` (순수 가상함수) | `@abstractmethod` | **반드시** 자식 클래스에서 구현 |
| `virtual void f() {}` | 기본 구현이 있는 메서드 | 필요할 때만 오버라이드 |
| `override` | 그냥 같은 이름으로 정의 | 부모 메서드를 덮어씀 |

**핵심: `generate_signal()`만 필수**입니다. 나머지 네 개(`on_init`, `on_market_open`, `on_order_filled`, `on_market_close`)는 기본 구현이 있어서, 필요한 것만 오버라이드하면 됩니다.

---

## 2. 프레임워크가 호출하는 순서

전략을 끼워넣기 전에, 프레임워크가 **언제 어떤 메서드를 호출하는지** 알아야 합니다. 이것도 C++의 Template Method 패턴과 같습니다 — 프레임워크가 흐름을 제어하고, 전략은 **빈칸만 채웁니다**.

```
장 시작 전 ──▶ on_init(broker, data_provider, executor)
                 │  "브로커, 데이터, 실행기 받아서 초기화해"
                 ▼
09:00 장 시작 ──▶ on_market_open()
                 │  "오늘 하루 준비해"
                 ▼
09:00~15:20  ──▶ generate_signal(stock_code, data)  ← 3초마다 반복
                 │  "이 종목 지금 사? 팔아? 가만히 있어?"
                 │
                 │  Signal(BUY) 리턴하면 → 프레임워크가 주문
                 │                          ↓
                 │                    on_order_filled(order)
                 │                      "체결됐어, 기록해"
                 ▼
15:30 장 마감 ──▶ on_market_close()
                   "오늘 결과 정리해"
```

전략 개발자가 할 일은 **다섯 개의 메서드를 채우는 것**뿐입니다. 주문 실행, 자금 관리, API 호출은 프레임워크가 다 합니다.

---

## 3. 샘플 전략: 골든크로스 + RSI + 거래량

끼워넣을 전략을 간단히 소개합니다. 세 가지 지표를 조합한 전략입니다:

**매수 조건** (2개 이상 충족 시):
- 5일 이평선이 20일 이평선을 **상향 돌파** (골든크로스)
- RSI(14)가 과매도(30) 구간에서 **탈출**
- 거래량이 20일 평균의 **1.5배 이상** 급증

**매도 조건** (1개 이상 충족 시):
- 5일선이 20일선을 **하향 돌파** (데드크로스)
- RSI가 **70 이상** (과매수)
- 익절(+10%) 또는 손절(-5%) 도달

복잡한 전략은 아닙니다. 중요한 건 전략 자체가 아니라, **이걸 프레임워크에 어떻게 끼워넣느냐**입니다.

---

## 4. 끼워넣기 — 단계별 과정

### 4-1. 폴더와 파일 만들기

```
strategies/
├── base.py              # BaseStrategy (건드리지 않음)
├── config.py            # StrategyLoader (건드리지 않음)
└── sample/              # ← 이 폴더를 만듭니다
    ├── config.yaml      #   설정 파일
    └── strategy.py      #   전략 코드
```

[5편](/stock/2026/02/21/stock-framework-core-modules.html)에서 다뤘듯이, StrategyLoader는 `strategies/` 아래 폴더를 스캔해서 `config.yaml` + `strategy.py`가 있으면 유효한 전략으로 인식합니다.

### 4-2. config.yaml — 전략 설정

```yaml
strategy:
  name: "SampleStrategy"
  version: "1.0.0"

parameters:
  ma_short_period: 5        # 단기 이평선
  ma_long_period: 20        # 장기 이평선
  rsi_period: 14
  rsi_oversold: 30          # 과매도 기준
  rsi_overbought: 70        # 과매수 기준
  volume_multiplier: 1.5    # 거래량 배수 기준
  min_buy_signals: 2        # 매수에 필요한 최소 조건 수

risk_management:
  stop_loss_pct: 0.05       # 5% 손절
  take_profit_pct: 0.10     # 10% 익절
  max_daily_trades: 5       # 하루 최대 거래 횟수

target_stocks: []
```

숫자를 코드에 하드코딩하지 않습니다. YAML에 빼두면 **코드 수정 없이 파라미터를 바꿀 수** 있습니다. RSI 기준을 30→25로 바꾸고 싶으면 YAML만 수정하면 됩니다.

### 4-3. strategy.py — 빈 틀부터 시작

BaseStrategy를 상속받고, 클래스 이름을 `~Strategy`로 끝내면 됩니다:

```python
from strategies.base import BaseStrategy, Signal, SignalType

class SampleStrategy(BaseStrategy):
    name = "SampleStrategy"
    version = "1.0.0"
```

지금 이 상태로 실행하면 에러가 납니다. `generate_signal()`이 `@abstractmethod`이기 때문입니다. C++에서 순수 가상함수를 구현 안 하면 컴파일 에러가 나는 것과 같습니다.

이제 메서드를 하나씩 채워봅시다.

### 4-4. on_init() — 초기화

```python
def on_init(self, broker, data_provider, executor) -> bool:
    # 프레임워크가 넘겨주는 세 가지를 저장
    self._broker = broker
    self._data_provider = data_provider
    self._executor = executor

    # config.yaml에서 파라미터 로드
    params = self.config.get("parameters", {})
    self._ma_short = params.get("ma_short_period", 5)
    self._ma_long = params.get("ma_long_period", 20)
    self._rsi_period = params.get("rsi_period", 14)
    self._rsi_oversold = params.get("rsi_oversold", 30)
    self._rsi_overbought = params.get("rsi_overbought", 70)
    self._volume_multiplier = params.get("volume_multiplier", 1.5)
    self._min_buy_signals = params.get("min_buy_signals", 2)

    risk = self.config.get("risk_management", {})
    self._stop_loss_pct = risk.get("stop_loss_pct", 0.05)
    self._take_profit_pct = risk.get("take_profit_pct", 0.10)
    self._max_daily_trades = risk.get("max_daily_trades", 5)

    # 상태 변수 초기화
    self.positions = {}       # 보유 종목 추적
    self.daily_trades = 0     # 오늘 거래 횟수

    self._is_initialized = True
    return True
```

`broker`, `data_provider`, `executor`는 **프레임워크가 주입**합니다. 전략이 직접 만들 필요 없습니다. 의존성 주입(Dependency Injection)이죠.

### 4-5. generate_signal() — 핵심 로직

유일한 **필수** 메서드입니다. 프레임워크가 종목코드와 OHLCV 데이터를 넘기면, 전략은 `Signal` 객체를 리턴합니다:

```python
def generate_signal(self, stock_code, data, timeframe='daily'):
    # 데이터 부족하면 패스
    if data is None or len(data) < self._ma_long + 2:
        return None

    # 하루 거래 한도 초과
    if self.daily_trades >= self._max_daily_trades:
        return None

    close = data["close"]
    volume = data["volume"]

    # 지표 계산
    sma_short = close.rolling(self._ma_short).mean()
    sma_long = close.rolling(self._ma_long).mean()
    rsi = self._calculate_rsi(close, self._rsi_period)
    avg_volume = volume.rolling(self._ma_long).mean()

    # ── 보유 중이면 매도 조건 확인 ──
    if stock_code in self.positions:
        reasons = []
        current_price = float(close.iloc[-1])
        entry_price = self.positions[stock_code]["entry_price"]
        pnl_pct = (current_price - entry_price) / entry_price

        if sma_short.iloc[-1] < sma_long.iloc[-1] and sma_short.iloc[-2] >= sma_long.iloc[-2]:
            reasons.append("데드크로스")
        if rsi.iloc[-1] > self._rsi_overbought:
            reasons.append("RSI 과매수")
        if pnl_pct >= self._take_profit_pct:
            reasons.append(f"익절 도달 ({pnl_pct:+.1%})")
        if pnl_pct <= -self._stop_loss_pct:
            reasons.append(f"손절 도달 ({pnl_pct:+.1%})")

        if reasons:
            return Signal(
                signal_type=SignalType.SELL,
                stock_code=stock_code,
                confidence=min(90.0, 50.0 + len(reasons) * 20),
                reasons=reasons,
            )
        return None

    # ── 미보유면 매수 조건 확인 ──
    reasons = []
    if sma_short.iloc[-1] > sma_long.iloc[-1] and sma_short.iloc[-2] <= sma_long.iloc[-2]:
        reasons.append(f"{self._ma_short}일선이 {self._ma_long}일선 골든크로스")
    if rsi.iloc[-2] < self._rsi_oversold and rsi.iloc[-1] >= self._rsi_oversold:
        reasons.append("RSI 과매도 탈출")
    if volume.iloc[-1] > avg_volume.iloc[-1] * self._volume_multiplier:
        reasons.append("거래량 급증")

    if len(reasons) >= self._min_buy_signals:
        current_price = float(close.iloc[-1])
        return Signal(
            signal_type=SignalType.BUY,
            stock_code=stock_code,
            confidence=min(95.0, 50.0 + len(reasons) * 15),
            target_price=current_price * (1 + self._take_profit_pct),
            stop_loss=current_price * (1 - self._stop_loss_pct),
            reasons=reasons,
        )

    return None
```

리턴값은 세 가지입니다:
- `Signal(BUY)` → 프레임워크가 FundManager에서 자금 예약 후 주문
- `Signal(SELL)` → 프레임워크가 매도 주문
- `None` → 아무것도 안 함

**전략은 주문을 직접 넣지 않습니다.** "사고 싶다"는 신호만 보내면, 자금 확인·주문 실행·체결 확인은 프레임워크가 합니다.

### 4-6. on_order_filled() — 체결 알림

주문이 체결되면 프레임워크가 이 메서드를 호출합니다:

```python
def on_order_filled(self, order) -> None:
    self.daily_trades += 1

    if order.is_buy:
        self.positions[order.stock_code] = {
            "quantity": order.quantity,
            "entry_price": order.price,
            "entry_time": order.filled_at,
        }
    elif order.is_sell:
        if order.stock_code in self.positions:
            entry = self.positions[order.stock_code]["entry_price"]
            pnl_pct = (order.price - entry) / entry * 100
            self.logger.info(f"{order.stock_code} 매도 완료: {pnl_pct:+.1f}%")
            del self.positions[order.stock_code]
```

매수 체결이면 보유 목록에 추가, 매도 체결이면 수익률 기록 후 제거. 이 정보가 있어야 `generate_signal()`에서 보유 여부를 판단할 수 있습니다.

### 4-7. on_market_open() / on_market_close() — 하루의 시작과 끝

```python
def on_market_open(self) -> None:
    self.daily_trades = 0
    self.daily_profit = 0.0
    self.logger.info("장 시작 — 일일 카운터 초기화")

def on_market_close(self) -> None:
    self.logger.info(
        f"장 마감 — 거래 {self.daily_trades}건, "
        f"잔여 포지션 {len(self.positions)}개"
    )
```

필수는 아니지만, 일일 카운터 초기화나 마감 리포트에 유용합니다.

---

## 5. 끼워넣기 완료 — 전체 흐름

폴더와 파일을 만들었으면, **프레임워크를 실행하기만 하면 됩니다**:

```python
# main.py — 이 코드는 수정할 필요 없음
strategies = StrategyLoader.discover_strategies()
# → {'sample': Path('strategies/sample')} 자동 발견

strategy = StrategyLoader.load_strategy('sample')
# → config.yaml 로드 → SampleStrategy 클래스 찾기 → 인스턴스 생성

strategy.on_init(broker, data_provider, executor)
# → 프레임워크가 모듈 주입

# 매매 루프 시작
# → generate_signal()이 3초마다 호출됨
```

다시 C++ 비유로 돌아가면:

```
┌─────────────────────────────────────────────────┐
│  프레임워크 (변경 X)          전략 (내가 작성)    │
│                                                  │
│  BaseStrategy* s;            SampleStrategy      │
│  s = load("sample");      ┌──────────────────┐  │
│  s->on_init(b, d, e);     │ on_init()        │  │
│  s->on_market_open();      │ on_market_open() │  │
│  sig = s->generate_signal()│ generate_signal()│  │
│  s->on_order_filled(ord);  │ on_order_filled()│  │
│  s->on_market_close();     │ on_market_close()│  │
│                            └──────────────────┘  │
│  ↑ 호출하는 쪽                 ↑ 구현하는 쪽      │
└─────────────────────────────────────────────────┘
```

프레임워크는 `BaseStrategy*` 포인터로 호출하고, 실제로는 `SampleStrategy`의 구현이 실행됩니다. **다형성(polymorphism)**입니다.

---

## 6. 새 전략 추가는 복사 + 수정

다른 전략을 만들고 싶으면, `sample/` 폴더를 복사해서 `generate_signal()`만 바꾸면 됩니다:

```bash
cp -r strategies/sample strategies/my_momentum
```

```python
# strategies/my_momentum/strategy.py
class MyMomentumStrategy(BaseStrategy):
    name = "MyMomentum"
    version = "1.0.0"

    def generate_signal(self, stock_code, data, timeframe='daily'):
        # 5일 연속 양봉이면 매수
        close = data["close"]
        consecutive_up = all(
            close.iloc[-i] > close.iloc[-i-1] for i in range(1, 6)
        )
        if consecutive_up:
            return Signal(
                signal_type=SignalType.BUY,
                stock_code=stock_code,
                confidence=80.0,
                reasons=["5일 연속 상승"],
            )
        return None
```

`config.yaml`의 `strategy.name`만 바꾸고, 나머지 파라미터는 전략에 맞게 조정하면 됩니다. **main.py는 건드리지 않습니다.**

---

## 마무리

이번 글의 핵심을 정리하면:

1. **BaseStrategy = 추상 클래스**: C++의 순수 가상함수처럼, `generate_signal()`은 반드시 구현해야 합니다. 나머지 네 개는 필요할 때만 오버라이드.
2. **끼워넣기 = 폴더 + 파일 2개**: `strategies/이름/` 아래에 `config.yaml` + `strategy.py`만 있으면 StrategyLoader가 자동 발견.
3. **전략은 신호만 보낸다**: 주문 실행, 자금 관리는 프레임워크가 처리. 전략은 `Signal(BUY/SELL)` 또는 `None`만 리턴.
4. **다형성으로 교체 가능**: 프레임워크는 `BaseStrategy` 인터페이스만 보기 때문에, 전략을 바꿔도 프레임워크 코드는 변경 없음.

이 프레임워크는 GitHub에 공개되어 있습니다: [kis-trading-template](https://github.com/tgparkk/kis-trading-template)

참고 – 블로그 내 관련 글

- [[1] 주식 자동매매 시리즈 소개](/stock/2026/02/01/stock-auto-trading-series-intro.html) – 시리즈 흐름
- [[2] 주식 단타 전략 소개 – 7가지 전략](/stock/2026/02/02/stock-short-term-strategies.html) – 전략 상세
- [[3] 단타 전략 선택 가이드](/stock/2026/02/03/stock-strategy-selection-guide.html) – 전략 비교 & 선택
- [[4] 자동매매 프레임워크 설계](/stock/2026/02/15/stock-auto-trading-framework-design.html) – 전체 구조, BaseStrategy, Signal
- [[5] 핵심 모듈 구현](/stock/2026/02/21/stock-framework-core-modules.html) – KISBroker, FundManager, StrategyLoader
