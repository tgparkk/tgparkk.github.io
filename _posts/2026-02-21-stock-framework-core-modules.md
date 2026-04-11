---
layout: post
title: "[5] 핵심 모듈 구현 – KISBroker, FundManager, StrategyLoader"
date: 2026-02-21
categories: [stock]
tags: [stock, auto-trading, kis-api, python, framework, template]
excerpt: "프레임워크의 핵심 모듈 세 가지를 구현합니다. 증권사 API를 하나로 감싸는 KISBroker, 자금 중복 사용을 막는 FundManager, 전략을 자동으로 찾아 로드하는 StrategyLoader."
comments: true
image: /assets/images/auto-stock-thumbnails/stock-auto-trading.svg
---

[지난 글](/stock/2026/02/15/stock-auto-trading-framework-design.html)에서 프레임워크의 전체 구조와 BaseStrategy, Signal을 다뤘습니다. 이번 글에서는 그 뼈대 위에 얹히는 **핵심 모듈 세 가지**를 구현합니다.

- **KISBroker** — 증권사 API를 하나로 감싸기
- **FundManager** — 자금 중복 사용 방지
- **StrategyLoader** — 전략 플러그인 시스템

---

## 1. KISBroker — 증권사 API를 하나로 감싸기

### 문제: API 파일이 5개

4편에서 `api/` 디렉토리를 소개했습니다. 인증, 주문, 차트, 계좌, 시장 정보가 각각 다른 파일에 있습니다:

```
api/
├── kis_auth.py         # 인증
├── kis_order_api.py    # 주문
├── kis_chart_api.py    # 차트
├── kis_account_api.py  # 계좌
└── kis_market_api.py   # 시장 정보
```

전략에서 이걸 직접 쓰면 어떻게 될까요?

```python
# ❌ 전략이 API를 직접 호출하면...
from api import kis_auth, kis_account_api, kis_market_api, kis_order_api

class MyStrategy:
    def generate_signal(self, stock_code, data):
        # 잔고 확인하려면 어떤 모듈이지?
        balance = kis_account_api.get_balance()  # 아 이거였나?
        # 아니면 이건가?
        balance = kis_market_api.get_account_balance()  # 이건가?
        # 현재가는?
        price = kis_market_api.get_current_price(stock_code)
        # 주문은?
        kis_order_api.place_order(...)
```

전략을 만들 때마다 "이 기능이 어떤 API 파일에 있더라?" 하고 찾아야 합니다. 게다가 API 모듈 구조가 바뀌면 **모든 전략을 수정**해야 하죠.

### 해결: KISBroker가 다 감싼다

```python
# ✅ KISBroker를 통해 호출
class MyStrategy:
    def generate_signal(self, stock_code, data):
        balance = self._broker.get_account_balance()
        holdings = self._broker.get_holdings()
        cash = self._broker.get_available_cash()
```

전략은 `self._broker`만 알면 됩니다. 내부에서 어떤 API 모듈을 호출하는지, 인증 토큰은 어떻게 관리되는지 **전략은 모릅니다**. (알 필요도 없습니다)

### KISBroker 구조

```python
class KISBroker(BaseBroker):
    """한국투자증권 API 래퍼"""

    async def connect(self) -> bool:
        """API 인증 + 초기화"""
        from api import kis_auth, kis_account_api, kis_market_api

        if not kis_auth.auth():
            return False

        self._connected = True
        return True

    def get_account_balance(self) -> dict:
        """계좌 잔고 조회"""
        balance_info = self._kis_market_api.get_account_balance()
        return {
            'total_balance': balance_info.get('total_value', 0),
            'available_cash': balance_info.get('available_amount', 0),
            'invested_amount': balance_info.get('purchase_amount', 0),
            'total_profit_loss': balance_info.get('total_profit_loss', 0),
            # ...
        }

    def get_holdings(self) -> List[dict]:
        """보유 종목 조회"""
        return self._kis_market_api.get_existing_holdings()

    def get_available_cash(self) -> float:
        """주문 가능 금액 조회"""
        # ...
```

`connect()`가 호출되면 내부에서 `kis_auth.auth()`로 토큰을 발급받고, 이후 모든 API 호출에 이 토큰을 자동으로 사용합니다. 전략은 `connect()` 이후에 `get_account_balance()`, `get_holdings()` 같은 메서드만 호출하면 됩니다.

### BaseBroker — 추상화의 이유

`KISBroker`는 `BaseBroker`라는 추상 클래스를 상속합니다:

```python
class BaseBroker(ABC):
    @abstractmethod
    async def connect(self) -> bool: ...

    @abstractmethod
    def get_account_balance(self) -> dict: ...

    @abstractmethod
    def get_holdings(self) -> List[dict]: ...

    @abstractmethod
    def get_available_cash(self) -> float: ...
```

"지금 한국투자증권만 쓰는데 왜 추상화하나?" 싶을 수 있습니다. 하지만 나중에 **다른 증권사 API**로 바꿀 때 빛을 발합니다:

```python
# 한국투자증권
broker = KISBroker()

# 나중에 다른 증권사로 바꾸고 싶으면?
# broker = KiwoomBroker()  # 인터페이스가 같으니 전략 코드 변경 없음
```

전략 코드는 `BaseBroker` 인터페이스만 알기 때문에, 증권사를 바꿔도 전략을 수정할 필요가 없습니다.

---

## 2. FundManager — 자금 중복 사용 방지

### 문제: 같은 돈을 두 번 쓸 뻔 했다

이건 실제로 겪은 문제입니다. 자동매매 루프에서 종목 A와 종목 B에 거의 동시에 매수 신호가 나왔습니다:

```
10:01:03.100  종목 A 매수 신호! 가용 자금: 1,000,000원 → 500,000원 매수
10:01:03.150  종목 B 매수 신호! 가용 자금: 1,000,000원 → 500,000원 매수
                                         ↑ 아직 A 주문이 반영 안 됨!
```

0.05초 차이로 두 종목이 같은 자금을 봤습니다. 결과: **100만 원으로 100만 원어치를 주문**하는 상황. (실제로는 두 번째 주문이 증거금 부족으로 실패하지만, 주문 실패 처리 로직이 복잡해집니다)

### 해결: reserve → confirm → release

FundManager는 **예약 시스템**으로 이 문제를 해결합니다. 식당 좌석 예약과 비슷합니다:

```
┌──────────────────────────────────────────────────────┐
│ 총 자금: 1,000,000원                                  │
│                                                       │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│ │  가용 자금   │  │  예약 자금   │  │  투자 자금   │   │
│ │  500,000원  │  │  500,000원  │  │     0원     │   │
│ └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                       │
│ 종목 A 주문 → 50만원 "예약" → 가용에서 예약으로 이동   │
│ 종목 B 주문 → 50만원 남음 → 정확한 잔고로 판단         │
└──────────────────────────────────────────────────────┘
```

코드로 보면:

```python
class FundManager:
    def __init__(self, initial_funds=0, max_position_count=20):
        self._lock = threading.RLock()  # 스레드 안전!

        self.total_funds = initial_funds
        self.available_funds = initial_funds
        self.reserved_funds = 0.0
        self.invested_funds = 0.0

        # 주문별 예약 추적
        self.order_reservations: Dict[str, float] = {}
```

핵심은 `threading.RLock()`입니다. 여러 종목의 매수 신호가 동시에 들어와도, **한 번에 하나의 스레드만** 자금을 건드릴 수 있습니다.

### 3단계 자금 흐름

**1단계: reserve (예약)**

```python
def reserve_funds(self, order_id: str, amount: float) -> bool:
    with self._lock:
        if self.available_funds < amount:
            return False  # 자금 부족

        self.available_funds -= amount
        self.reserved_funds += amount
        self.order_reservations[order_id] = amount
        return True
```

주문을 넣기 **전에** 자금을 예약합니다. 이 순간부터 다른 종목은 이 금액을 사용할 수 없습니다.

**2단계: confirm (체결 확인)**

```python
def confirm_order(self, order_id: str, actual_amount: float) -> None:
    with self._lock:
        reserved = self.order_reservations[order_id]
        self.reserved_funds -= reserved
        self.invested_funds += actual_amount
        del self.order_reservations[order_id]

        # 예약과 실제 체결 금액의 차액 정산
        diff = reserved - actual_amount
        if diff > 0:
            self.available_funds += diff  # 남은 돈 환불
```

주문이 체결되면 예약 → 투자로 전환합니다. 지정가 주문은 예약 금액과 실제 체결 금액이 다를 수 있어서, 차액을 자동으로 정산합니다.

**3단계: release (매도 회수) 또는 cancel (주문 취소)**

```python
def release_investment(self, amount: float, stock_code: str = "") -> None:
    with self._lock:
        self.invested_funds -= amount
        self.available_funds += amount

def cancel_order(self, order_id: str) -> None:
    with self._lock:
        reserved = self.order_reservations[order_id]
        self.reserved_funds -= reserved
        self.available_funds += reserved
        del self.order_reservations[order_id]
```

매도하면 투자 → 가용으로, 주문 취소하면 예약 → 가용으로 돌려줍니다.

### 추가 안전장치들

FundManager에는 자금 관리 외에도 몇 가지 안전장치가 있습니다:

**종목당 투자 한도:**

```python
def get_max_buy_amount(self, stock_code: str) -> float:
    with self._lock:
        max_per_stock = self.total_funds * self.max_position_ratio  # 9%
        max_total = self.total_funds * self.max_total_investment_ratio  # 90%
        remaining = max_total - self.invested_funds - self.reserved_funds

        return min(max_per_stock, remaining, self.available_funds)
```

총 자금 1,000만 원이면 종목당 최대 90만 원(9%), 전체 투자는 최대 900만 원(90%)까지. 세 가지 한도 중 가장 작은 값을 사용합니다.

**동시 보유 종목 수 제한:**

```python
def can_add_position(self, stock_code: str) -> bool:
    with self._lock:
        if stock_code in self.current_position_codes:
            return True  # 이미 보유 중이면 분할매수 허용
        return len(self.current_position_codes) < self.max_position_count
```

**매도 후 재매수 쿨다운:**

```python
# 매도 후 30분간 같은 종목 재매수 금지
self._sell_cooldowns: Dict[str, datetime] = {}
self.sell_cooldown_minutes = 30
```

급하게 손절했는데 바로 다시 사는 "복수 매매"를 방지합니다. (경험에서 나온 기능입니다 😅)

---

## 3. StrategyLoader — 전략 플러그인 시스템

### 문제: 전략을 추가할 때마다 코드를 수정해야 한다

프레임워크 없이 전략을 추가하면 이런 식입니다:

```python
# ❌ 전략을 추가할 때마다 main.py를 수정
from strategies.breakout import BreakoutStrategy
from strategies.orb import ORBStrategy
from strategies.momentum import MomentumStrategy  # 새로 추가

strategy = MomentumStrategy()  # 매번 직접 연결
```

전략이 10개가 되면 import 10줄, 초기화 10줄... 그리고 전략 이름을 오타 내면 런타임 에러.

### 해결: 폴더만 추가하면 자동 발견

StrategyLoader는 `strategies/` 디렉토리를 스캔해서 **유효한 전략 폴더를 자동으로 찾아** 로드합니다:

```
strategies/
├── base.py                 # BaseStrategy (건드리지 않음)
├── config.py               # StrategyLoader (건드리지 않음)
├── sample/                 # ← 폴더만 추가하면 됨!
│   ├── config.yaml         #   필수: 전략 설정
│   └── strategy.py         #   필수: 전략 코드
└── my_new_strategy/        # ← 새 전략도 폴더만 추가!
    ├── config.yaml
    └── strategy.py
```

### 전략 발견: discover_strategies()

```python
class StrategyLoader:
    STRATEGIES_DIR = Path("strategies")

    @staticmethod
    def discover_strategies() -> Dict[str, Path]:
        strategies_dir = StrategyLoader.STRATEGIES_DIR
        discovered = {}

        for path in strategies_dir.iterdir():
            # 폴더이고, _로 시작하지 않고, 필수 파일이 있으면 전략
            if path.is_dir() and not path.name.startswith('_'):
                if StrategyLoader.validate_strategy(path):
                    discovered[path.name] = path

        return discovered
```

`strategies/` 아래의 모든 폴더를 돌면서, `config.yaml`과 `strategy.py`가 있으면 유효한 전략으로 인식합니다. `_`로 시작하는 폴더(예: `__pycache__`)는 무시합니다.

### 전략 검증: validate_strategy()

```python
@staticmethod
def validate_strategy(strategy_path: Path) -> bool:
    if not strategy_path.is_dir():
        return False

    config_file = strategy_path / "config.yaml"
    strategy_file = strategy_path / "strategy.py"

    return config_file.exists() and strategy_file.exists()
```

두 파일이 모두 있어야 유효한 전략입니다. 하나라도 없으면 무시됩니다. 실수로 빈 폴더를 만들어도 에러가 나지 않습니다.

### 전략 로드: load_strategy()

```python
@staticmethod
def load_strategy(strategy_name: str) -> BaseStrategy:
    # 1. 설정 로드
    config_loader = StrategyConfig(strategy_name)
    config = config_loader.load()  # config.yaml → dict

    # 2. 전략 클래스 동적 로드
    strategy_class = StrategyLoader._load_strategy_class(strategy_name)

    # 3. 인스턴스 생성 (설정 주입)
    return strategy_class(config)
```

세 단계로 이루어집니다:

1. `config.yaml`을 읽어서 딕셔너리로 변환
2. `strategy.py`에서 `BaseStrategy`를 상속한 클래스를 **동적으로** 찾아 로드
3. 설정을 넣어서 인스턴스 생성

"동적으로 찾는다"는 건, strategy.py 안에서 **클래스 이름이 `Strategy`로 끝나고 `BaseStrategy`를 상속한 클래스**를 자동으로 찾는다는 뜻입니다:

```python
# strategy.py 안에서 이런 클래스를 자동 발견
class SampleStrategy(BaseStrategy):   # ✅ 이름이 Strategy로 끝남 + BaseStrategy 상속
    ...

class Helper:                          # ❌ Strategy로 안 끝남 → 무시
    ...
```

### StrategyConfig — YAML을 딕셔너리로

```python
class StrategyConfig:
    def load(self) -> Dict[str, Any]:
        with open(self._config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default=None):
        """점(.) 표기법으로 중첩 키 접근"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
```

YAML 파일을 Python 딕셔너리로 변환하고, `'risk_management.stop_loss_pct'`처럼 **점 표기법**으로 중첩된 값에 접근할 수 있습니다:

```python
config.get('risk_management.stop_loss_pct', 0.05)
# config.yaml의 risk_management: → stop_loss_pct: 값을 가져옴
# 없으면 기본값 0.05
```

### 새 전략 추가하기 — 실제 순서

새 전략을 추가하는 전체 순서입니다:

```bash
# 1. 폴더 생성
mkdir strategies/my_breakout

# 2. config.yaml 작성
cat > strategies/my_breakout/config.yaml << 'EOF'
strategy:
  name: "MyBreakout"
  version: "1.0.0"

parameters:
  breakout_period: 20
  volume_threshold: 1.5

risk_management:
  stop_loss_pct: 0.03
  take_profit_pct: 0.05
EOF

# 3. strategy.py 작성
```

```python
# strategies/my_breakout/strategy.py
from strategies.base import BaseStrategy, Signal, SignalType

class MyBreakoutStrategy(BaseStrategy):
    name = "MyBreakout"
    version = "1.0.0"

    def on_init(self, broker, data_provider, executor):
        self._broker = broker
        self._data_provider = data_provider
        self._executor = executor
        self._is_initialized = True
        return True

    def generate_signal(self, stock_code, data, timeframe='daily'):
        # 여기에 돌파 로직 작성
        ...

    def on_order_filled(self, order): ...
    def on_market_open(self): ...
    def on_market_close(self): ...
```

```bash
# 4. 끝! 프레임워크가 자동으로 발견합니다
```

main.py를 수정할 필요 없습니다. StrategyLoader가 알아서 찾아줍니다.

---

## 4. 모든 것이 연결되는 순간

프로그램이 시작되면 이 세 모듈이 이런 순서로 엮입니다:

```
프로그램 시작 (main.py)
│
▼
┌────────────────────────────────────────┐
│ 1. KISBroker 연결                       │
│    broker = KISBroker()                 │
│    await broker.connect()               │
│    → API 인증, 토큰 발급                │
└──────────────────┬─────────────────────┘
                   ▼
┌────────────────────────────────────────┐
│ 2. FundManager 초기화                   │
│    fund_manager = FundManager()         │
│    balance = broker.get_account_balance()│
│    fund_manager.update_total_funds(     │
│        balance['available_cash'])       │
│    → 실제 계좌 잔고로 자금 설정          │
└──────────────────┬─────────────────────┘
                   ▼
┌────────────────────────────────────────┐
│ 3. StrategyLoader로 전략 발견 & 로드     │
│    strategies = StrategyLoader          │
│        .discover_strategies()           │
│    strategy = StrategyLoader            │
│        .load_strategy('sample')         │
│    → config.yaml 로드 + 클래스 인스턴스화│
└──────────────────┬─────────────────────┘
                   ▼
┌────────────────────────────────────────┐
│ 4. 전략에 모듈 주입                     │
│    strategy.on_init(                    │
│        broker=broker,                   │
│        data_provider=data_provider,     │
│        executor=executor                │
│    )                                    │
│    → 전략이 broker, data를 사용 가능     │
└──────────────────┬─────────────────────┘
                   ▼
            매매 루프 시작! 🚀
```

이 흐름이 4편에서 설명한 BaseStrategy 라이프사이클의 **1~2단계**(`__init__` → `on_init`)에 해당합니다. 이후 장 시작(`on_market_open`) → 신호 생성(`generate_signal`) → 체결(`on_order_filled`) → 장 마감(`on_market_close`)으로 이어집니다.

---

## 마무리

이번 글에서 다룬 것을 정리하면:

1. **KISBroker**: 5개 API 모듈을 하나의 인터페이스로 감싸서, 전략은 `self._broker`만 호출하면 됩니다. `BaseBroker` 추상화로 나중에 증권사를 바꿔도 전략 코드는 수정할 필요 없습니다.
2. **FundManager**: reserve → confirm → release 3단계로 자금 중복 사용을 방지합니다. 스레드 락으로 동시 매수 신호에도 안전하고, 종목당 한도·전체 한도·재매수 쿨다운까지 관리합니다.
3. **StrategyLoader**: `strategies/` 폴더에 `config.yaml` + `strategy.py`만 넣으면 자동 발견·로드됩니다. main.py 수정 없이 새 전략을 추가할 수 있습니다.

이 세 모듈이 4편의 BaseStrategy와 만나면, **전략만 갈아끼우는 자동매매 프레임워크**가 완성됩니다.

이 프레임워크는 GitHub에 공개되어 있습니다: [kis-trading-template](https://github.com/tgparkk/kis-trading-template)

참고 – 블로그 내 관련 글

- [[1] 주식 자동매매 시리즈 소개](/stock/2026/02/01/stock-auto-trading-series-intro.html) – 시리즈 흐름
- [[2] 주식 단타 전략 소개 – 7가지 전략](/stock/2026/02/02/stock-short-term-strategies.html) – 전략 상세
- [[3] 단타 전략 선택 가이드](/stock/2026/02/03/stock-strategy-selection-guide.html) – 전략 비교 & 선택
- [[4] 자동매매 프레임워크 설계](/stock/2026/02/15/stock-auto-trading-framework-design.html) – 전체 구조, BaseStrategy, Signal
