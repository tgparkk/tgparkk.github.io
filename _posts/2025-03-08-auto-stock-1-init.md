---
layout: post
title: "한국투자증권 API로 자동 매매 시스템 개발하기 – 1:튜토리얼과 개발 경험"
date: 2025-03-08
categories: stock
tags: [stock, python]
excerpt: "직장에서 근무하다 보면 주식 시장을 실시간으로 지켜보기 어렵고, 일일이 수동으로 주문을 넣는 것도 한계가 있습니다. 저 역시 이런 고민 끝에 자동 매매 시스템에 관심을 갖게 되었습니다. 마침 한국투자증권에서 2022년 국내 증권사 최초로 REST 기반 OpenAPI 서비스를 시작하면서​, 개인 개발자도 손쉽게 주식 매매 프로그램을 만들 수 있는 길이 열렸습니다. 기존 키움증권 등 타 증권사의 API는 윈도우 기반 COM API라 Python과 연동하기 번거롭고 32비트 환경 제약이 있었지만, 한투 OpenAPI는 운영체제 제한 없이 REST/웹소켓 방식이라 접근성이 훨씬 뛰어났죠​. 이러한 배경에서 저는 한국투자증권 API를 활용한 자동 매매 봇 개발에 도전하게 되었습니다. 이 포스팅에서는 제가 개발한 자동 매매 시스템의 과정을 공유하려 합니다. 단순한 기술적 튜토리얼을 넘어, 실제 개발하면서 겪은 고민과 노하우도 함께 담았습니다. 개발 개요, 구성 요소, 동작 방식, 매매 전략, 실행 방법부터 테스트 경험과 개선점까지 차례로 살펴보겠습니다.
"
---

# 한국투자증권 API로 자동매매 시스템 구축하기: 개발 환경부터 인증 모듈까지

안녕하세요! 오늘부터 한국투자증권 API를 이용한 자동매매 시스템 개발 과정을 공유하려고 합니다. IT 직장인으로서 월급 외 추가 수입을 위한 재테크 방법으로 주식 자동매매 시스템을 구축하는 여정을 함께해주세요.

## 들어가며: 왜 주식 자동매매 시스템인가?

IT 직장인으로 일하면서 월급만으로는 자산 형성에 한계를 느끼게 되었습니다. 직업적 역량을 활용해 부수입을 만들 수 있는 방법을 고민하다가, 프로그래밍 기술을 활용한 주식 자동매매 시스템 개발을 시작하게 되었습니다.

여러 증권사 API 중에서도 한국투자증권 API를 선택한 이유는:
1. **소켓 방식 지원**: 실시간 데이터 처리에 유리
2. **문서화가 잘 되어 있음**: 개발 난이도 감소
3. **모의투자 환경 제공**: 실제 투자 전 안전하게 테스트 가능

이 포스트에서는 개발 환경 설정부터 시작해 API 인증 모듈 개발까지, 자동매매 시스템의 기초를 다지는 단계를 다루겠습니다.

## Part 1: 개발 환경 설정

### 1. 한국투자증권 API 개요

한국투자증권에서 제공하는 'KIS Developers' API는 개인 투자자와 개발자들이 자동화된 트레이딩 시스템을 구축할 수 있도록 다양한 기능을 제공합니다.

#### 1.1 API 주요 특징

- **실시간 소켓 통신 지원**: 빠른 데이터 전송과 실시간 주문 처리 가능
- **RESTful API**: HTTP 요청을 통한 간편한 데이터 조회 및 주문 처리
- **국내주식, 해외주식, 선물/옵션 등 다양한 상품 지원**
- **모의투자 환경**: 실제 계좌 없이도 테스트 가능

#### 1.2 API 신청 방법

1. 한국투자증권 계좌 개설 (없는 경우)
2. [KIS Developers 웹사이트](https://apiportal.koreainvestment.com/) 접속
3. 회원가입 및 로그인
4. API 신청 메뉴에서 "오픈API 이용 신청" 클릭
5. 약관 동의 및 필요 정보 입력
6. 신청 완료 후 승인 대기 (보통 1~2일 소요)
7. 승인 후 앱키(APP Key)와 비밀키(APP Secret) 발급

### 2. 파이썬 개발 환경 구축

이 프로젝트는 Python을 기반으로 개발할 예정입니다. 필요한 개발 환경을 설정해 보겠습니다.

#### 2.1 파이썬 설치

최신 버전의 Python(3.8 이상)을 [공식 웹사이트](https://www.python.org/downloads/)에서 다운로드하여 설치합니다.

#### 2.2 가상환경 설정

프로젝트 의존성을 관리하기 위해 가상환경을 생성합니다.

```bash
# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 2.3 필요 패키지 설치

프로젝트에 필요한 주요 패키지들을 설치합니다.

```bash
pip install requests pandas numpy matplotlib pyyaml websocket-client jupyter

# requests: HTTP 요청 처리  
# pandas: 데이터 분석 및 처리  
# numpy: 수치 계산  
# matplotlib: 데이터 시각화
# pyyaml: 설정 파일 관리
# websocket-client: 실시간 데이터 수신
# jupyter: 코드 테스트 및 분석
```


### 3. 프로젝트 구조 설계

체계적인 개발을 위해 다음과 같은 프로젝트 구조를 사용할 예정입니다:

```
kis-autotrading/
│
├── config/                  # 설정 파일
│   ├── api_config.yaml      # API 키, 계좌번호 등 설정
│   ├── trading_config.yaml  # 매매 전략 파라미터
│   ├── token_info.json      # 토큰 정보 (접속에 필요)
│   └── target_stocks.txt    # 대상 종목 리스트
│
├── src/                     # 소스 코드
│   ├── api/                 # API 관련 모듈
│   │   ├── __init__.py
│   │   ├── auth.py          # 인증 모듈
│   │   ├── market_data.py   # 시장 데이터 조회
│   │   └── order.py         # 주문 실행
│   │
│   ├── strategy/            # 매매 전략
│   │   ├── __init__.py
│   │   └── basic_strategy.py # 기본 매매 전략
│   │
│   ├── utils/               # 유틸리티 함수
│   │   ├── __init__.py
│   │   ├── data_utils.py    # 데이터 처리 유틸리티
│   │   └── logger.py        # 로깅 유틸리티
│   │
│   └── main.py              # 메인 실행 파일
│
├── logs/                    # 로그 파일 저장 디렉토리
├── venv/                    # 가상환경 (git에서 제외)
├── requirements.txt         # 의존성 파일
└── README.md                # 프로젝트 설명
```

### 4. 설정 파일 준비

#### 4.1 API 설정 파일 (config/api_config.yaml)

API 키와 계좌 정보를 저장할 설정 파일을 생성합니다:

```yaml
api:
  base_url: "https://openapi.koreainvestment.com:9443"
  app_key: "YOUR_APP_KEY"    # 발급받은 앱키 입력
  app_secret: "YOUR_APP_SECRET"  # 발급받은 시크릿키 입력
  account_no: "12345678901234"  # 계좌번호 (앞 8자리 + 뒷 번호)
```

#### 4.2 매매 전략 설정 (config/trading_config.yaml)

전략 파라미터를 저장할 설정 파일:

```yaml
strategy:
  ma_short: 5             # 단기 이동평균선 기간
  ma_long: 20             # 장기 이동평균선 기간
  rsi_period: 14          # RSI 계산 기간
  rsi_oversold: 30        # RSI 과매도 기준
  rsi_overbought: 70      # RSI 과매수 기준
  bb_period: 20           # 볼린저 밴드 기간
  bb_std: 2               # 볼린저 밴드 표준편차
  stop_loss: 0.03         # 손절 기준 (3%)
  take_profit: 0.05       # 익절 기준 (5%)
  max_position: 5         # 최대 포지션 개수
  position_size: 0.2      # 포지션 크기 (자본금 대비 %)
```

#### 4.3 타겟 종목 리스트 (config/target_stocks.txt)

분석할 종목 코드를 한 줄에 하나씩 작성합니다:

```
005930  # 삼성전자
035420  # NAVER
000660  # SK하이닉스
035720  # 카카오
051910  # LG화학
```

### 5. .gitignore 설정

버전 관리 시 민감한 정보나 불필요한 파일을 제외하기 위한 `.gitignore` 파일을 생성합니다:

```
# 가상환경
venv/
__pycache__/
*.py[cod]
*$py.class

# 민감한 설정 파일
config/api_config.yaml

# 로그 파일
logs/

# 토큰 파일
token_info.json

# IDE 관련 파일
.idea/
.vscode/
*.swp
```

## Part 2: API 인증 모듈 개발

이제 한국투자증권 API와 통신하기 위한 인증 모듈을 개발해 보겠습니다.

### 1. 한국투자증권 API 인증 이해하기

한국투자증권 API는 OAuth 2.0 기반의 인증 방식을 사용합니다. 주요 인증 과정은 다음과 같습니다:

1. 앱키(APP Key)와 비밀키(APP Secret)를 이용해 **액세스 토큰** 발급
2. 발급받은 액세스 토큰으로 API 요청 시 인증
3. 토큰 만료 시 새로운 토큰 발급

액세스 토큰은 일반적으로 24시간 동안 유효하며, 만료 전에 갱신해야 합니다. 우리는 이 인증 과정을 체계적으로 관리할 모듈을 만들어야 합니다.

### 2. 인증 모듈 설계

`auth.py` 파일에 구현할 `KoreaInvestmentAuth` 클래스는 다음 기능을 제공할 예정입니다:

1. 액세스 토큰 발급 및 관리
2. 토큰 만료 시간 추적
3. 토큰 정보 파일 저장/로드 (프로그램 재시작 시 재사용)
4. API 요청에 필요한 인증 헤더 생성
5. 해시키(HASH) 생성 (일부 API에 필요)

### 3. 로깅 유틸리티 구현

인증 모듈에서 사용할 로깅 기능을 먼저 구현해 보겠습니다. `src/utils/logger.py` 파일을 다음과 같이 작성합니다:

```python
import logging
import os
from datetime import datetime

def setup_logger(log_file=None, log_level=logging.INFO):
    """로깅 설정 함수
    
    Args:
        log_file (str, optional): 로그 파일 경로
        log_level (int, optional): 로그 레벨
        
    Returns:
        logging.Logger: 설정된 로거 객체
    """
    # 루트 로거 설정
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 포맷 설정
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 추가 (지정된 경우)
    if log_file:
        # 디렉토리가 없는 경우 생성
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
```

### 4. 인증 모듈 구현

이제 `src/api/auth.py` 파일을 작성해 보겠습니다:

```python
import requests
import yaml
import json
import time
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class KoreaInvestmentAuth:
    def __init__(self, config_path="config/api_config.yaml"):
        """한국투자증권 API 인증 클래스 초기화
        
        Args:
            config_path (str): API 설정 파일 경로
        """
        # 설정 파일 로드
        with open(config_path, 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file)['api']
        
        self.base_url = self.config['base_url']
        self.app_key = self.config['app_key']
        self.app_secret = self.config['app_secret']
        
        # 토큰 파일 경로
        token_dir = os.path.dirname(os.path.abspath(config_path))
        self.token_file = os.path.join(token_dir, "token_info.json")
        
        # 토큰 정보 초기화
        self.access_token = None
        self.token_issued_at = None
        self.token_expired_at = None
        
        # 저장된 토큰 정보 로드
        self._load_token_info()
    
    def _load_token_info(self):
        """저장된 토큰 정보 로드"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    token_info = json.load(f)
                    
                    self.access_token = token_info.get('access_token')
                    self.token_issued_at = token_info.get('issued_at')
                    self.token_expired_at = token_info.get('expired_at')
                    
                    logger.info("토큰 정보를 파일에서 로드했습니다.")
                    
                    # 토큰 유효성 검증
                    current_time = time.time()
                    if self.token_expired_at and current_time >= self.token_expired_at:
                        logger.info("로드한 토큰이 만료되었습니다.")
                        self.access_token = None
                        self.token_expired_at = None
            except Exception as e:
                logger.error(f"토큰 정보 로드 중 오류 발생: {str(e)}")
                # 오류 발생 시 토큰 정보 초기화
                self.access_token = None
                self.token_issued_at = None
                self.token_expired_at = None

    def _save_token_info(self):
        """토큰 정보 저장"""
        token_info = {
            'access_token': self.access_token,
            'issued_at': self.token_issued_at,
            'expired_at': self.token_expired_at
        }
        
        try:
            # 디렉토리 확인
            token_dir = os.path.dirname(self.token_file)
            os.makedirs(token_dir, exist_ok=True)
            
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(token_info, f, indent=2)
            logger.info(f"토큰 정보를 파일에 저장했습니다: {self.token_file}")
        except Exception as e:
            logger.error(f"토큰 정보 저장 중 오류 발생: {str(e)}")

    def get_access_token(self, force_new=False):
        """액세스 토큰 발급 또는 캐시된 토큰 반환
        
        Args:
            force_new (bool): 강제로 새 토큰 발급 여부
            
        Returns:
            str: 액세스 토큰
        """
        current_time = time.time()
        
        # 토큰 유효성 확인
        token_is_valid = (
            self.access_token is not None and
            not force_new and
            self.token_expired_at is not None and
            current_time < self.token_expired_at
        )
        
        if token_is_valid:
            logger.debug("캐시된 토큰을 사용합니다.")
            return self.access_token
        
        # 하루에 한 번만 토큰 발급 (강제 갱신 제외)
        if self.token_issued_at and not force_new:
            issued_date = datetime.fromtimestamp(self.token_issued_at).date()
            today = datetime.now().date()
            
            if issued_date == today:
                logger.warning("오늘 이미 토큰이 발급되었습니다. 기존 토큰을 사용합니다.")
                if self.access_token:
                    return self.access_token
                else:
                    logger.warning("기존 토큰이 유효하지 않습니다. 새 토큰을 발급합니다.")
        
        # 토큰 발급 API 엔드포인트
        url = f"{self.base_url}/oauth2/tokenP"
        
        # 요청 헤더와 데이터
        headers = {
            "content-type": "application/json"
        }
        
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        try:
            # API 호출
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()  # 오류가 있는 경우 예외 발생
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            
            # 토큰 만료 시간 설정
            expires_in = token_data.get('expires_in', 86400)  # 기본값 24시간
            self.token_issued_at = current_time
            self.token_expired_at = current_time + expires_in - 300  # 5분 여유
            
            # 토큰 정보 저장
            self._save_token_info()
            
            logger.info(f"새 액세스 토큰이 발급되었습니다. 만료 시간: {expires_in}초")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"토큰 발급 중 오류 발생: {str(e)}")
            if response:
                logger.error(f"응답: {response.text}")
            raise
    
    def get_hashkey(self, data):
        """데이터로부터 해시키 생성
        
        Args:
            data (dict): 해시키를 생성할 데이터
            
        Returns:
            str: 생성된 해시키
        """
        url = f"{self.base_url}/uapi/hashkey"
        
        headers = {
            "content-type": "application/json",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            
            hashkey = response.json()['HASH']
            return hashkey
        except requests.exceptions.RequestException as e:
            logger.error(f"해시키 생성 중 오류 발생: {str(e)}")
            if response:
                logger.error(f"응답: {response.text}")
            raise
    
    def get_auth_headers(self, include_hashkey=False, body=None):
        """인증 헤더 생성
        
        Args:
            include_hashkey (bool): 해시키 포함 여부
            body (dict): 해시키 생성에 사용할 요청 바디
            
        Returns:
            dict: 인증 헤더
        """
        token = self.get_access_token()
        
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "",  # 필요에 따라 설정
        }
        
        if include_hashkey and body:
            headers["hashkey"] = self.get_hashkey(body)
        
        return headers
```

### 5. 인증 모듈 설명

위 코드는 한국투자증권 API 인증을 위한 `KoreaInvestmentAuth` 클래스를 구현한 것입니다. 주요 기능별로 자세히 살펴보겠습니다:

#### 5.1 초기화 및 토큰 관리

- `__init__`: 설정 파일에서 API 키 정보를 로드하고 토큰 상태를 초기화합니다.
- `_load_token_info`: 이전에 저장된 토큰 정보가 있다면 파일에서 로드합니다.
- `_save_token_info`: 토큰 정보를 파일에 저장하여 프로그램 재시작 시 재사용할 수 있게 합니다.

#### 5.2 액세스 토큰 발급

- `get_access_token`: 기존 토큰이 유효하면 재사용하고, 아니면 새 토큰을 발급합니다.
- 토큰 만료 5분 전에 갱신하도록 설정하여 안전성을 높였습니다.
- 하루에 한 번만 토큰을 발급하도록 제한하여 API 호출을 최소화했습니다. (잦은 토큰 발급 발생 시 이용 제한 될 수 있음 )

<div style="display: flex; gap: 10px;">
  <img src="/assets/images/stock/warningKISToken.jpg" width="600" alt="이미지 1">
</div>

#### 5.3 해시키 및 인증 헤더

- `get_hashkey`: 일부 API(주로 주문 관련)에 필요한 해시키를 생성합니다.
- `get_auth_headers`: API 요청에 필요한 인증 헤더를 생성합니다.


## 다음 단계

이제 주식 자동매매 시스템의 핵심 기반이 되는 개발 환경 구축과 API 인증 모듈 개발을 완료했습니다! 다음 포스트에서는 시장 데이터 조회 모듈과 기술적 분석 도구를 개발하여, 실제 주가 데이터를 분석하고 매매 신호를 생성하는 기능을 구현해보겠습니다.

지금까지의 내용을 요약하면:
1. 한국투자증권 API 신청 및 개발 환경 구축
2. 프로젝트 구조 설계 및 설정 파일 준비
3. 로깅 유틸리티 구현
4. API 인증 모듈 개발 (토큰 발급, 관리, 헤더 생성)

재테크를 위한 자동매매 시스템 개발 여정, 앞으로도 계속 공유해 나가겠습니다. 질문이나 의견은 댓글로 남겨주세요! 😊

---

#### 코드 저장소

이 프로젝트의 전체 소스 코드는 [GitHub 저장소](https://github.com/tgparkk/autoStockTrading)에서 확인하실 수 있습니다.