---
layout: post
title: "[4] 자동매매 프레임워크 설계 – 전략을 갈아끼우는 구조"
date: 2026-02-15
categories: [stock]
tags: [stock, auto-trading, kis-api, python, framework, template]
excerpt: "주식에는 다양한 전략이 있으니, 공통 부분은 한 번만 짜고 전략만 갈아끼우는 프레임워크를 설계했습니다. BaseStrategy 하나만 상속하면 새로운 자동매매 봇이 탄생합니다."
comments: true
---

[지난 글](/stock/2026/02/03/stock-strategy-selection-guide.html)에서 7가지 단타 전략 중 어떤 전략을 선택할지 정리했습니다. 이번 글부터는 선택한 전략을 **코드로 옮기기 전에**, 먼저 자동매매 프레임워크 구조를 설계한 과정을 다룹니다.

이번 글에서는 **왜 프레임워크가 필요한지**, **전체 구조**, 그리고 전략의 뼈대인 **BaseStrategy와 Signal**을 다룹니다. 핵심 모듈 구현이나 메인 루프 흐름은 이어지는 글에서 이어가겠습니다.

---

## 1. 왜 프레임워크인가 — 삽질의 역사

### 처음엔 전략마다 따로 만들었습니다

돌파 전략을 구현하고, ORB 전략도 구현하고, 모멘텀 전략도 해보고 싶었습니다. 처음에는 **전략마다 프로젝트를 따로** 만들었습니다.

```
D:\GIT\
├── RoboTrader/              ← 가격 위치 전략
├── RoboTrader_orb/          ← ORB 전략
├── RoboTrader_quant/        ← 퀀트 팩터 전략
└── RoboTrader_SurgePullback/ ← 급등 후 눌림 전략
```

실제로 이렇게 프로젝트가 늘어났습니다. (지금도 폴더에 남아 있습니다)

### 문제는 "전략 빼고 다 똑같다"는 것

네 개 프로젝트에서 **매번 반복한 코드**가 있었습니다:

- KIS API 인증 + 토큰 갱신
- Rate Limiting (초당 요청 제한)
- 주문 실행 + 체결 확인
- DB 연결 + 거래 기록
- 텔레그램 알림 전송
- 에러 핸들링 + 재시도 로직
- 장 시작/마감 스케줄링

버그를 하나 고치면 **네 개 프로젝트에서 같은 코드를 네 번** 고쳐야 했습니다. Rate Limiting 로직을 개선하면, RoboTrader에만 적용하고 RoboTrader_orb에는 깜빡하는 일이 생겼습니다. (그러면 API 호출 초과로 에러가 터지죠 🔥)

### 그래서 템플릿을 만들기로 했습니다

> **전략은 다른데 인프라는 같다.**

이 한 줄이 프레임워크의 출발점입니다. 공통 인프라를 한 번만 짜놓고, **전략 파일만 갈아끼우면 새로운 자동매매 봇이 탄생**하는 구조:

```
kis-trading-template/              ← 공통 프레임워크
├── RoboTrader (전략 A)            ← 전략만 다름
├── RoboTrader_orb (전략 B)        ← 전략만 다름
└── RoboTrader_quant (전략 C)      ← 전략만 다름
```

버그를 고치면 **한 번만** 고치면 됩니다. 새 전략을 테스트하고 싶으면 `strategies/` 폴더에 파일 하나만 추가하면 됩니다.

---

## 2. 전체 아키텍처 — 디렉토리별 역할

```
RoboTrader_template/
│
├── framework/              # 🔧 추상화 레이어
├── api/                    # 📡 KIS API 래퍼
├── strategies/             # 🎯 전략 모듈 (여기만 바꾸면 됨!)
├── core/                   # ⚙️ 공통 핵심 모듈
├── config/                 # ⚙️ 설정
├── db/                     # 💾 데이터베이스
├── utils/                  # 🛠️ 유틸리티
└── main.py                 # 🚀 진입점
```

전체 그림만 보면 단순해 보이지만, 각 디렉토리마다 명확한 역할이 있습니다. 하나씩 풀어보겠습니다.

### `framework/` — 추상화 레이어

```
framework/
├── broker.py          # 증권사 API 추상화
├── data.py            # 데이터 제공자 추상화
├── executor.py        # 주문 실행 추상화
└── utils.py           # 공통 유틸리티
```

**왜 추상화가 필요한가?** 지금은 한국투자증권(KIS) API만 쓰지만, 나중에 다른 증권사 API로 바꿀 수도 있습니다. `broker.py`에서 인터페이스를 정의해두면, 전략 코드는 **어떤 증권사를 쓰는지 몰라도** 됩니다.

- **`broker.py`**: 계좌 잔고 조회, 보유 종목 조회, 현재가 조회 등 증권사와 관련된 모든 것을 추상화. `KISBroker` 클래스가 실제 API를 호출하고, `FundManager`가 스레드 안전하게 자금을 추적합니다.
- **`data.py`**: 일봉·분봉·거래량 등 시장 데이터 조회를 추상화. 전략은 "삼성전자 60일치 일봉 주세요" 하면 됩니다.
- **`executor.py`**: 주문 실행을 추상화. 시장가·지정가 주문, 체결 확인, 주문 취소 등.
- **`utils.py`**: 로거 설정, 한국 장 시간 체크 등 공통 유틸리티.

### `api/` — KIS API 래퍼

```
api/
├── kis_auth.py         # 인증 + 토큰 갱신 + Rate Limiting
├── kis_order_api.py    # 주문 (시장가/지정가/정정/취소)
├── kis_chart_api.py    # 차트 (일봉/분봉 OHLCV)
├── kis_account_api.py  # 계좌 (잔고/예수금/보유종목)
├── kis_market_api.py   # 시장 정보 (종목 검색/시세)
└── circuit_breaker.py  # 서킷브레이커 (연속 실패 시 차단)
```

KIS REST API를 **기능별로 분리**했습니다. 하나의 거대한 파일에 모든 API를 넣으면 2000줄이 넘어가서 유지보수가 힘들었거든요. (RoboTrader 초기 버전이 실제로 그랬습니다 😅)

특히 `kis_auth.py`가 핵심입니다. 토큰 만료 시 자동 갱신, 초당 요청 제한(Rate Limiting), 해시키 생성까지 처리합니다. 이 부분을 전략마다 매번 구현하는 게 가장 귀찮았습니다.

`circuit_breaker.py`는 API 호출이 연속으로 실패하면 일정 시간 호출을 멈추는 안전장치입니다. 증권사 서버에 문제가 있을 때, 무한 재시도로 API 제한에 걸리는 걸 방지합니다.

### `strategies/` — 전략 모듈 (핵심!)

```
strategies/
├── base.py            # BaseStrategy 추상 클래스
├── config.py          # 전략 설정 로더 & 동적 로딩
└── sample/            # 예제 전략
    ├── strategy.py    # 전략 코드
    ├── config.yaml    # 전략 설정
    └── README.md      # 전략 설명
```

**전략 개발자가 작업하는 유일한 디렉토리**입니다. `base.py`의 `BaseStrategy`를 상속해서 `generate_signal()`만 구현하면 됩니다. 설정은 `config.yaml`(YAML 형식의 설정 파일)에 분리해서, 코드 수정 없이 파라미터를 바꿀 수 있습니다.

`config.py`의 `StrategyLoader`가 이 디렉토리를 스캔해서 전략을 자동 발견합니다. 새 전략 폴더를 추가하기만 하면, 프레임워크가 알아서 찾아 로드합니다. (플러그인 구조)

### `core/` — 공통 핵심 모듈

```
core/
├── order_manager.py          # 주문 관리 (미체결 추적, 재주문)
├── fund_manager.py           # 자금 관리 (배분, 중복 사용 방지)
├── data_collector.py         # 데이터 수집 (스크리너 연동)
└── telegram_integration.py   # 텔레그램 알림
```

전략과 API 사이에서 **비즈니스 로직**을 처리합니다:

- **`order_manager.py`**: 주문 후 체결 여부를 추적하고, 미체결 주문을 재주문하거나 취소합니다.
- **`fund_manager.py`**: 총 자금을 종목별로 배분하고, 같은 자금을 두 종목에 중복 할당하지 않도록 관리합니다. 비동기 환경에서 여러 전략이 동시에 자금을 요청할 수 있어서, 스레드 안전하게 만들었습니다.
- **`data_collector.py`**: 조건 검색(스크리너)에서 후보 종목을 가져오거나, 일봉/분봉 데이터를 수집합니다.
- **`telegram_integration.py`**: 매수/매도 체결, 에러 발생, 일일 리포트를 텔레그램으로 보내줍니다. 직장에서 폰으로 확인하려면 이게 필수입니다.

### `config/`, `db/`, `utils/`

- **`config/`**: API 키, 계좌번호, 전략 설정 등 환경 설정 파일. `.env`나 YAML(사람이 읽기 쉬운 설정 포맷)로 관리합니다. (Git에는 안 올립니다!)
- **`db/`**: SQLite 또는 PostgreSQL 연결. 거래 이력, 일일 수익, 포지션 기록 등을 저장합니다.
- **`utils/`**: 날짜 변환, 포맷팅, 한국 공휴일 체크 등 자잘한 도우미 함수.

### `main.py` — 진입점

모든 것을 엮는 파일입니다. API 인증 → 전략 로드 → 매매 루프 시작. 상세 흐름은 이어지는 글에서 다루겠습니다.

---

## 3. BaseStrategy — 전략의 뼈대

모든 전략은 `BaseStrategy`를 상속합니다. "전략을 갈아끼운다"는 건, 결국 이 클래스를 상속한 새 클래스를 만드는 것입니다.

### 라이프사이클 흐름도

전략은 **6단계 라이프사이클**을 따릅니다. 아래 흐름도가 "언제, 왜" 각 메서드가 호출되는지를 보여줍니다:

```
프로그램 시작
│
▼
┌──────────────────────────────────────────────────┐
│ 1. __init__(config)                               │
│    · config.yaml 로드                             │
│    · 파라미터 초기값 설정                           │
│    · 아직 API 연결 안 됨!                          │
└──────────────────────┬───────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────┐
│ 2. on_init(broker, data_provider, executor)       │
│    · API 연결 완료 후 1회 호출                     │
│    · broker로 잔고 확인 가능                       │
│    · data_provider로 과거 데이터 로드 가능          │
│    · 여기서 False 반환하면 전략 로드 실패 → 종료   │
└──────────────────────┬───────────────────────────┘
                       ▼
          ┌─── 09:00 장 시작 ───┐
          ▼                      │
┌────────────────────────┐       │
│ 3. on_market_open()    │       │
│    · 일일 카운터 리셋   │       │
│    · 워치리스트 준비     │       │
│    · 오버나이트 갭 확인  │       │
└──────────┬─────────────┘       │
           ▼                      │
┌────────────────────────────────────────────────┐
│ 4. generate_signal(stock_code, data)  ← 반복!  │
│    · 종목별로 주기적 호출 (예: 1분마다)           │
│    · BUY / SELL / HOLD 신호 반환                │
│    · None 반환 = 관망                            │
│    ┌──────────────────────────────────────────┐ │
│    │  BUY 신호 → 프레임워크가 주문 실행        │ │
│    │  SELL 신호 → 프레임워크가 매도 주문        │ │
│    │  None/HOLD → 아무것도 안 함               │ │
│    └──────────────────────────────────────────┘ │
└──────────┬─────────────────────────────────────┘
           ▼
┌────────────────────────────────────────────────┐
│ 5. on_order_filled(order)                       │
│    · 체결 완료 시 콜백                           │
│    · 포지션 딕셔너리 업데이트                     │
│    · 수익률 계산 & 로깅                          │
│    · 매수 체결이면 → 이후 generate_signal에서     │
│      해당 종목은 매도 판단으로 전환               │
└──────────┬─────────────────────────────────────┘
           ▼
          ┌─── 15:30 장 마감 ───┐
          ▼                      │
┌────────────────────────┐       │
│ 6. on_market_close()   │       │
│    · 일일 리포트 생성   │       │
│    · 미체결 주문 정리   │       │
│    · 통계 저장          │       │
└────────────────────────┘       │
          │                      │
          ▼                      │
     다음 거래일 ────────────────┘
```

### 왜 이런 구조인가?

각 메서드가 분리된 이유가 있습니다:

- **`__init__`과 `on_init`을 분리한 이유**: `__init__`은 설정 로드만, `on_init`은 API 연결 후 실행됩니다. API 연결 전에 전략 객체를 미리 만들어두고, 인증이 완료된 뒤에 초기화할 수 있습니다. (API 인증이 실패할 수도 있으니까요)

- **`on_market_open` / `on_market_close`를 분리한 이유**: 장 시작 때만 해야 할 일(일일 카운터 리셋, 갭 확인)과 장 마감 때만 해야 할 일(리포트, 미체결 정리)이 다릅니다. `generate_signal` 안에서 매번 "지금 장 시작 직후인가?" 체크하는 것보다 깔끔합니다.

- **`on_order_filled`를 콜백으로 만든 이유**: 주문과 체결 사이에 시간 차이가 있습니다. 지정가 주문은 몇 분~몇 시간 뒤에 체결될 수 있어요. 체결 시점에 콜백으로 알려주면, 전략이 그때 포지션을 업데이트할 수 있습니다.

### 코드로 보면

```python
class BaseStrategy(ABC):
    name: str = "BaseStrategy"
    version: str = "1.0.0"
    description: str = ""
    author: str = ""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._broker = None         # on_init에서 주입
        self._data_provider = None  # on_init에서 주입
        self._executor = None       # on_init에서 주입
        self._is_initialized = False

    @abstractmethod
    def on_init(self, broker, data_provider, executor) -> bool:
        """API 연결 후 1회 호출. False면 전략 로드 실패."""
        pass

    @abstractmethod
    def generate_signal(
        self, stock_code: str, data: pd.DataFrame, timeframe: str = 'daily'
    ) -> Optional[Signal]:
        """핵심! 종목 코드 + OHLCV → Signal(BUY/SELL/HOLD) 반환"""
        pass

    @abstractmethod
    def on_order_filled(self, order: OrderInfo) -> None:
        """체결 콜백. 포지션 관리, 수익률 기록."""
        pass

    @abstractmethod
    def on_market_open(self) -> None:
        """09:00 장 시작. 일일 초기화."""
        pass

    @abstractmethod
    def on_market_close(self) -> None:
        """15:30 장 마감. 정리 & 리포트."""
        pass
```

`generate_signal()`이 **핵심**입니다. 종목 코드와 OHLCV 데이터를 받아서, `Signal` 객체를 반환하면 됩니다. **나머지는 전부 프레임워크가 처리합니다.** API 호출, 주문 실행, 체결 확인, 에러 핸들링 — 전략 개발자는 신경 쓸 필요 없습니다.

```
┌─────────────────────────────────────────────┐
│  Your Strategy (전략만 작성)                  │
│  ├── generate_signal() → BUY / SELL / HOLD  │
│  ├── on_market_open()                        │
│  └── on_market_close()                       │
├─────────────────────────────────────────────┤
│  Framework (프레임워크가 알아서 처리)          │
│  ├── API 인증 & Rate Limiting               │
│  ├── 주문 실행 & 체결 확인                    │
│  ├── 포지션 관리 & DB 저장                    │
│  ├── 텔레그램 알림                            │
│  └── 에러 핸들링 & 재시도                     │
└─────────────────────────────────────────────┘
```

---

## 4. Signal — 매매 신호 객체

`generate_signal()`이 반환하는 `Signal`은 이렇게 생겼습니다:

```python
@dataclass
class Signal:
    signal_type: SignalType        # BUY, SELL, HOLD, STRONG_BUY, STRONG_SELL
    stock_code: str                # 종목 코드
    confidence: float = 0.0        # 확신도 (0~100)
    target_price: Optional[float] = None  # 목표가
    stop_loss: Optional[float] = None     # 손절가
    reasons: List[str] = field(default_factory=list)   # 매매 이유
    metadata: Dict[str, Any] = field(default_factory=dict)  # 추가 데이터
```

### SignalType — 5가지 신호의 차이

```python
class SignalType(Enum):
    STRONG_BUY  = "strong_buy"   # 강한 매수
    BUY         = "buy"          # 매수
    HOLD        = "hold"         # 관망
    SELL        = "sell"         # 매도
    STRONG_SELL = "strong_sell"  # 강한 매도
```

"BUY랑 STRONG_BUY가 뭐가 다른데?" 싶을 수 있습니다. 프레임워크에서 이렇게 활용합니다:

| SignalType | 의미 | 활용 예시 |
|------------|------|-----------|
| `STRONG_BUY` | 조건 3개 이상 동시 충족 | 비중 확대 (종목당 한도의 150%), 즉시 시장가 주문 |
| `BUY` | 기본 매수 조건 충족 | 기본 비중 배분, 지정가 주문 가능 |
| `HOLD` | 관망 | 아무 액션 없음. 명시적으로 "봤는데 안 산다"를 기록할 때 |
| `SELL` | 기본 매도 조건 충족 | 보유 수량 전량 매도 |
| `STRONG_SELL` | 급락·손절 조건 | 즉시 시장가 매도, 텔레그램 긴급 알림 |

**`HOLD`와 `None` 반환의 차이**: `None`은 "데이터 부족 등으로 판단 불가"이고, `HOLD`는 "판단은 했는데 매매할 이유가 없다"입니다. 로그에서 "이 종목을 분석은 했는데 안 샀구나"를 구분할 수 있습니다.

**`STRONG_BUY` / `STRONG_SELL` 실전 활용**: Sample 전략에서는 `confidence`를 조건 충족 수에 따라 계산합니다. 조건이 2개 충족되면 `BUY` + confidence 80, 3개 모두 충족되면 `STRONG_BUY` + confidence 95 같은 식입니다.

### confidence — 확신도의 의미

`confidence`는 0~100 사이 값으로, 전략이 "얼마나 확신하는지"를 나타냅니다. Sample 전략의 계산 방식을 보면:

```python
# 매수: 충족 조건 수에 따라 confidence 계산
confidence = min(95.0, 50.0 + len(reasons) * 15)
# 조건 2개 → 80, 조건 3개 → 95

# 매도: 충족 조건 수에 따라 계산
confidence = min(90.0, 50.0 + len(reasons) * 20)
# 조건 1개 → 70, 조건 2개 → 90
```

이 값은 나중에 **주문 비중 조절**에 쓸 수 있습니다. confidence 90이면 한도까지 매수, 60이면 반만 매수하는 식으로요.

### reasons — 왜 이 종목을 샀는지

`reasons`는 문자열 리스트입니다. 매매 이유를 기록해두면 두 곳에서 빛을 발합니다:

**1) 텔레그램 알림:**

```
📈 매수 신호: 삼성전자 (005930)
확신도: 80
이유:
 - 5일선이 20일선 골든크로스
 - 거래량 2.3배 급증
목표가: 75,000원 | 손절가: 68,000원
```

직장에서 폰으로 이 알림을 받으면, "아 골든크로스에 거래량도 터졌구나"를 바로 알 수 있습니다.

**2) 사후 분석:**

한 달 치 거래를 돌아볼 때, "거래량 급증"이 이유에 포함된 매매만 필터링해서 승률을 볼 수 있습니다. "거래량 조건을 빼면 오히려 승률이 높아지네?" 같은 인사이트를 얻을 수 있죠.

### metadata — 전략별 추가 데이터

`metadata`는 전략이 자유롭게 쓸 수 있는 딕셔너리입니다. Signal의 기본 필드로 부족할 때, 전략에 특화된 정보를 담습니다.

**활용 사례 1: 지표값 기록**

Sample 전략은 매수 시점의 이동평균과 RSI를 기록합니다:

```python
metadata={
    "sma_short": float(sma_short.iloc[-1]),   # 5일 이평: 72,300
    "sma_long": float(sma_long.iloc[-1]),      # 20일 이평: 71,800
    "rsi": float(rsi.iloc[-1]),                # RSI: 45.2
}
```

나중에 "RSI가 몇일 때 샀을 때 승률이 높았는가"를 분석할 수 있습니다.

**활용 사례 2: ORB 전략의 범위 정보**

```python
metadata={
    "orb_high": 52300,          # 시초가 범위 고가
    "orb_low": 51200,           # 시초가 범위 저가
    "orb_range": 1100,          # 범위 폭
    "breakout_direction": "up", # 돌파 방향
    "orb_minutes": 15,          # 몇 분 범위인지
}
```

**활용 사례 3: 매도 시 포지션 정보**

Sample 전략은 매도 신호에 기존 포지션 정보를 담습니다:

```python
metadata={"position": self.positions[stock_code]}
# → {"quantity": 10, "entry_price": 72000, "entry_time": ...}
```

프레임워크가 이 정보를 보고 "몇 주를 팔아야 하는지"를 판단합니다.

---

## 5. 실제 전략은 이렇게 생겼습니다

이론만으로는 감이 안 잡히니, Sample 전략의 핵심 부분을 보겠습니다. 이동평균 크로스 + RSI + 거래량으로 매수/매도를 판단하는 전략입니다.

### config.yaml — 코드 수정 없이 파라미터 조절

> **YAML이란?** JSON처럼 데이터를 표현하는 포맷인데, 따옴표나 중괄호 없이 **들여쓰기로 구조를 표현**합니다. 사람이 읽고 쓰기 편해서 설정 파일에 많이 씁니다. Python에서는 `PyYAML` 라이브러리로 읽으면 딕셔너리로 바뀝니다.

```yaml
parameters:
  ma_short_period: 5       # 단기 이동평균 (일)
  ma_long_period: 20       # 장기 이동평균 (일)
  rsi_period: 14           # RSI 계산 기간
  rsi_oversold: 30         # 과매도 기준선
  rsi_overbought: 70       # 과매수 기준선
  volume_multiplier: 1.5   # 평균 대비 N배 이상이면 급증
  min_buy_signals: 2       # 최소 몇 개 조건 충족 시 매수

risk_management:
  stop_loss_pct: 0.05      # 손절 5%
  take_profit_pct: 0.10    # 익절 10%
  max_position_size: 0.10  # 종목당 포트폴리오 10%
  max_daily_trades: 5      # 일일 최대 5건
```

이렇게 설정을 YAML로 분리하면, "RSI 과매도 기준을 25로 낮춰볼까?" 할 때 **코드를 안 건드려도** 됩니다.

### generate_signal() — 매수/매도 판단

```python
def generate_signal(self, stock_code, data, timeframe='daily'):
    # 데이터 부족하면 패스
    min_len = max(self._ma_long, self._rsi_period) + 2
    if data is None or len(data) < min_len:
        return None

    # 일일 거래 한도 확인
    if self.daily_trades >= self._max_daily_trades:
        return None

    # 지표 계산
    close = data["close"]
    sma_short = close.rolling(self._ma_short).mean()
    sma_long = close.rolling(self._ma_long).mean()
    rsi = self._calculate_rsi(close, self._rsi_period)

    # 보유 중이면 매도 판단, 미보유면 매수 판단
    if stock_code in self.positions:
        sell, reasons = self._check_sell(stock_code, current_price, ...)
        if sell:
            return Signal(signal_type=SignalType.SELL, ...)
    else:
        buy, reasons = self._check_buy(sma_short, sma_long, rsi, ...)
        if buy:
            return Signal(
                signal_type=SignalType.BUY,
                stock_code=stock_code,
                confidence=min(95.0, 50.0 + len(reasons) * 15),
                target_price=current_price * 1.10,  # +10% 익절
                stop_loss=current_price * 0.95,      # -5% 손절
                reasons=reasons,
                metadata={"sma_short": ..., "rsi": ...},
            )
    return None
```

매수 조건은 **3가지 중 2가지 이상** 충족 시:

1. 5일선이 20일선 **골든크로스** (상향 돌파)
2. RSI(14)가 **과매도(30) 탈출**
3. 거래량이 20일 평균의 **1.5배 이상**

매도 조건은 **1가지 이상** 충족 시:

1. 5일선이 20일선 **데드크로스** (하향 돌파)
2. RSI(14)가 **과매수(70)** 진입
3. **익절(+10%)** 또는 **손절(-5%)** 도달

이 Sample 전략은 예시일 뿐이고, 이 구조 위에 돌파 전략이든 ORB든 자유롭게 구현할 수 있습니다.

---

## 6. 프로그램이 죽으면? — 상태 복원과 포지션 동기화

자동매매에서 가장 무서운 상황은 **프로그램이 죽었을 때**입니다. 주식을 사놓고 프로그램이 꺼져버리면, 매도 타이밍을 놓치거나 보유 종목 정보 자체를 잃어버릴 수 있습니다.

데이트레이딩(당일 청산)이 아니라 **며칠 보유하는 전략**이라면 더 중요합니다. 어제 산 종목을 오늘 프로그램이 모른다면 낭패니까요.

### 두 가지 복원 경로

이 프레임워크는 **프로그램 재시작 시** 두 가지 방법으로 보유 종목을 복원합니다:

```
프로그램 재시작
│
├── 가상매매 모드 → DB에서 복원
│   └── 어제까지의 거래 기록이 DB에 남아 있으므로
│       "보유 중" 상태인 종목을 다시 불러옵니다
│
└── 실전매매 모드 → 실제 계좌에서 복원
    └── KIS API로 실제 증권 계좌의 잔고를 조회해서
        "지금 실제로 뭘 들고 있는지" 가져옵니다
```

**실전매매 모드가 더 신뢰할 수 있습니다.** 프로그램이 죽어 있는 동안 수동으로 매매했을 수도 있으니까요. 실제 계좌가 진실의 원천(Single Source of Truth)입니다.

### 실전매매: 계좌 잔고 조회

KIS API의 계좌 잔고 조회를 통해 **실제 보유 종목 목록**을 가져옵니다:

```python
# broker.get_holdings() 반환 형태
[
    {
        "stock_code": "005930",       # 종목 코드
        "stock_name": "삼성전자",      # 종목명
        "quantity": 10,               # 보유 수량
        "avg_price": 72000,           # 평균 매수가
        "current_price": 74500,       # 현재가
        "eval_amount": 745000,        # 평가 금액
        "profit_loss": 25000,         # 손익
        "profit_loss_rate": 3.47      # 수익률(%)
    },
    ...
]
```

### 불일치 감지와 긴급 동기화

프로그램이 재시작되면, **시스템이 알고 있는 보유 종목**과 **실제 계좌의 보유 종목**을 비교합니다:

```
실제 계좌: 삼성전자, SK하이닉스, NAVER
시스템 기록: 삼성전자, SK하이닉스

→ "NAVER가 계좌에 있는데 시스템에 없다!" → 긴급 동기화
```

이런 불일치가 감지되면:

1. **미관리 종목을 시스템에 추가** — 매수가·수량 등을 계좌에서 가져와 시스템에 등록
2. **손절/익절 기준 자동 설정** — 매수가 기준 기본 비율(예: 손절 -3%, 익절 +2%)로 설정
3. **텔레그램 알림** — "긴급 포지션 동기화: NAVER 외 1종목 복구 완료" 같은 알림 전송

```python
# 긴급 동기화 후 텔레그램 알림 예시
📊 긴급 포지션 동기화 완료
복구 종목: 3개
 - 005930 삼성전자: 10주 @ 72,000원 (정상)
 - 000660 SK하이닉스: 5주 @ 185,000원 (정상)
 - 035420 NAVER: 3주 @ 210,000원 (신규 추가 ⚠️)
```

이렇게 하면 **프로그램이 죽었다 살아나도**, 실제 계좌 상태를 기준으로 매매를 이어갈 수 있습니다. 스윙 트레이딩(며칠 보유)이든 데이트레이딩이든 상관없이, 프로그램 재시작 시 자동으로 포지션을 맞춰줍니다.

---

## 마무리

이번 글에서 다룬 것을 정리하면:

1. **왜 프레임워크인가**: 4개 프로젝트에서 같은 인프라 코드를 반복하는 삽질을 경험하고, "전략만 갈아끼우는 구조"를 만들기로 했습니다.
2. **아키텍처**: framework(추상화) → api(KIS 래퍼) → strategies(전략 플러그인) → core(비즈니스 로직)으로 책임을 분리했습니다.
3. **BaseStrategy**: 6단계 라이프사이클(`__init__` → `on_init` → `on_market_open` → `generate_signal` → `on_order_filled` → `on_market_close`)으로 전략의 진입/청산/정리를 구조화했습니다.
4. **Signal**: 5가지 SignalType으로 매매 강도를 표현하고, reasons로 매매 이유를 기록하고, metadata로 전략별 추가 데이터를 전달합니다.
5. **상태 복원**: 프로그램이 죽어도 실제 계좌 잔고를 기준으로 포지션을 자동 복구합니다.

다음 글에서는 이 뼈대 위에 얹히는 핵심 모듈들 — `KISBroker`, `FundManager`, `StrategyLoader` 등을 다룰 예정입니다.

이 프레임워크는 GitHub에 공개되어 있습니다: [kis-trading-template](https://github.com/tgparkk/kis-trading-template)

참고 – 블로그 내 관련 글

- [[1] 주식 자동매매 시리즈 소개](/stock/2026/02/01/stock-auto-trading-series-intro.html) – 시리즈 흐름
- [[2] 주식 단타 전략 소개 – 7가지 전략](/stock/2026/02/02/stock-short-term-strategies.html) – 전략 상세
- [[3] 단타 전략 선택 가이드](/stock/2026/02/03/stock-strategy-selection-guide.html) – 전략 비교 & 선택
