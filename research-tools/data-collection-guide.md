# 주식 전략 조사를 위한 데이터 수집 가이드

## 🎯 데이터 수집 목표

주식 전략 조사를 위해 필요한 데이터:
1. **가격 데이터**: 일봉, 분봉, 틱 데이터
2. **거래량 데이터**: 일별, 시간별 거래량
3. **재무 데이터**: 재무제표, 재무 비율
4. **시장 데이터**: 시가총액, 거래대금, 외국인/기관 매매동향

---

## 📊 데이터 소스

### 1. 한국투자증권 API (KIS API)

**장점:**
- 실시간 데이터 제공
- 정확한 거래 데이터
- API 호출 제한 있지만 충분함

**사용 방법:**
```python
# 예시: 일봉 데이터 조회
from kis_api import KISAPI

api = KISAPI()
data = api.get_daily_price('005930', '20240101', '20241220')
```

**필요한 데이터:**
- 일봉: 시가, 고가, 저가, 종가, 거래량
- 분봉: 1분, 5분, 15분, 30분, 60분
- 현재가: 실시간 호가 정보

### 2. FinanceDataReader

**장점:**
- 무료
- 사용 간편
- 과거 데이터 제공

**설치:**
```bash
pip install finance-datareader
```

**사용 예시:**
```python
import FinanceDataReader as fdr

# 코스피 전체 종목
kospi = fdr.StockListing('KOSPI')

# 특정 종목 일봉 데이터
df = fdr.DataReader('005930', '2024-01-01', '2024-12-20')
```

**제공 데이터:**
- 일봉: Open, High, Low, Close, Volume
- 종목 리스트: 코스피, 코스닥

### 3. KRX 정보데이터시스템

**장점:**
- 공식 데이터
- 상세한 시장 정보
- 무료

**사용 방법:**
- 웹사이트: http://data.krx.co.kr
- CSV 다운로드 가능
- API 제공 (제한적)

**제공 데이터:**
- 일별 시세
- 거래량 상위
- 외국인/기관 매매동향

### 4. DART (전자공시시스템)

**장점:**
- 재무 데이터
- 공시 정보
- 무료

**사용 방법:**
- 웹사이트: https://dart.fss.or.kr
- OpenDART API 사용 가능

**제공 데이터:**
- 재무제표
- 주요 재무 비율
- 공시 정보

---

## 💻 데이터 수집 스크립트 예시

### 1. 일봉 데이터 수집

```python
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
import os

def collect_daily_data(stock_code, start_date, end_date, save_path='data'):
    """
    일봉 데이터 수집 및 저장
    
    Parameters:
    -----------
    stock_code : str
        종목 코드 (예: '005930' - 삼성전자)
    start_date : str
        시작일 (YYYY-MM-DD)
    end_date : str
        종료일 (YYYY-MM-DD)
    save_path : str
        저장 경로
    """
    try:
        # 데이터 수집
        df = fdr.DataReader(stock_code, start_date, end_date)
        
        # 데이터 정리
        df.reset_index(inplace=True)
        df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        
        # 저장
        os.makedirs(save_path, exist_ok=True)
        file_path = f"{save_path}/{stock_code}_daily_{start_date}_{end_date}.csv"
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        
        print(f"✅ 데이터 수집 완료: {file_path}")
        print(f"   기간: {start_date} ~ {end_date}")
        print(f"   총 {len(df)}일 데이터")
        
        return df
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

# 사용 예시
if __name__ == "__main__":
    # 삼성전자 일봉 데이터 수집 (최근 1년)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    df = collect_daily_data('005930', start_date, end_date)
```

### 2. 여러 종목 일괄 수집

```python
def collect_multiple_stocks(stock_codes, start_date, end_date, save_path='data'):
    """
    여러 종목의 일봉 데이터 일괄 수집
    
    Parameters:
    -----------
    stock_codes : list
        종목 코드 리스트
    start_date : str
        시작일
    end_date : str
        종료일
    save_path : str
        저장 경로
    """
    results = {}
    
    for code in stock_codes:
        print(f"\n📊 {code} 데이터 수집 중...")
        df = collect_daily_data(code, start_date, end_date, save_path)
        if df is not None:
            results[code] = df
        else:
            print(f"⚠️ {code} 데이터 수집 실패")
    
    print(f"\n✅ 총 {len(results)}개 종목 데이터 수집 완료")
    return results

# 사용 예시
if __name__ == "__main__":
    # 코스피 상위 10개 종목
    top_stocks = ['005930', '000660', '035420', '005380', '051910',
                  '006400', '035720', '028260', '105560', '096770']
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    results = collect_multiple_stocks(top_stocks, start_date, end_date)
```

### 3. 데이터 품질 검증

```python
def validate_data(df, stock_code):
    """
    수집한 데이터의 품질 검증
    
    Parameters:
    -----------
    df : DataFrame
        검증할 데이터프레임
    stock_code : str
        종목 코드
    """
    issues = []
    
    # 1. 결측치 확인
    missing = df.isnull().sum()
    if missing.sum() > 0:
        issues.append(f"⚠️ 결측치 발견: {missing[missing > 0].to_dict()}")
    
    # 2. 가격 데이터 이상치 확인
    if (df['close'] <= 0).any():
        issues.append("❌ 종가가 0 이하인 데이터 존재")
    
    if (df['high'] < df['low']).any():
        issues.append("❌ 고가가 저가보다 낮은 데이터 존재")
    
    if (df['high'] < df['close']).any() or (df['high'] < df['open']).any():
        issues.append("❌ 고가가 종가/시가보다 낮은 데이터 존재")
    
    if (df['low'] > df['close']).any() or (df['low'] > df['open']).any():
        issues.append("❌ 저가가 종가/시가보다 높은 데이터 존재")
    
    # 3. 거래량 확인
    if (df['volume'] < 0).any():
        issues.append("❌ 거래량이 음수인 데이터 존재")
    
    # 4. 날짜 연속성 확인
    df['date'] = pd.to_datetime(df['date'])
    date_diff = df['date'].diff().dt.days
    if (date_diff > 5).any():
        issues.append("⚠️ 날짜가 5일 이상 건너뛴 구간 존재")
    
    # 결과 출력
    if issues:
        print(f"\n🔍 {stock_code} 데이터 검증 결과:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"✅ {stock_code} 데이터 검증 통과")
    
    return len(issues) == 0

# 사용 예시
if __name__ == "__main__":
    df = collect_daily_data('005930', '2024-01-01', '2024-12-20')
    if df is not None:
        validate_data(df, '005930')
```

---

## 📁 데이터 저장 구조

```
data/
├── daily/              # 일봉 데이터
│   ├── 005930_daily_2024-01-01_2024-12-20.csv
│   ├── 000660_daily_2024-01-01_2024-12-20.csv
│   └── ...
├── intraday/          # 분봉 데이터
│   ├── 005930_1min_2024-12-20.csv
│   └── ...
├── financial/         # 재무 데이터
│   └── ...
└── market/            # 시장 데이터
    └── ...
```

---

## ⚠️ 주의사항

### 1. API 호출 제한
- 한국투자증권 API: 분당/일일 호출 제한 확인
- FinanceDataReader: 과도한 호출 시 IP 차단 가능
- **해결책**: 요청 간 딜레이 추가, 캐싱 활용

### 2. 데이터 정합성
- 스플릿/배당 조정 확인
- 결측치 처리 (공휴일, 상장폐지 등)
- 시간대 확인 (UTC vs KST)

### 3. 저장 공간
- 장기 데이터는 용량이 큼
- 압축 저장 고려 (parquet, hdf5)
- 정기적인 백업

---

## 🔗 유용한 링크

- FinanceDataReader 문서: https://github.com/FinanceData/FinanceDataReader
- 한국투자증권 API 문서: https://apiportal.koreainvestment.com/
- KRX 정보데이터시스템: http://data.krx.co.kr
- DART API: https://opendart.fss.or.kr/

---

**마지막 업데이트**: 2025-12-20

