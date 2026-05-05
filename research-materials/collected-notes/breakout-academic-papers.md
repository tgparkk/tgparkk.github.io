# 돌파 전략 관련 학술 자료 메모

## 1. FinLLM-B: When Large Language Models Meet Financial Breakout Trading (NAACL 2025 산업 트랙)
- **PDF**: `research-materials/saved-papers/FinLLM-B_When_LLM_Meet_Financial_Breakout_Trading.pdf`
- **핵심 요약**
  - S&P500 선물 발자국(footprint) 데이터를 10-shot 규모로 정제하고 S1(방향)·S2(저항)·S3(매수/매도 힘) 세부 태스크로 분리해 GPT-3.5 기반 FinLLM-B를 미세조정.
  - 멀티 스테이지 구조 + 별도 보고서 생성기를 적용해 평균 정확도 84.8%, 퍼펙션 비율 59.45%로 GPT-4 대비 42%p 이상 향상.
  - 2~10샷 데이터 증분 실험에서 정확도가 57.5%→84.8%로 증가하며 데이터 부족 환경에서도 LLM 접근이 유효함을 입증.
- **적용 포인트**
  - 국내 호가/체결 데이터를 동일한 S1~S3 태스크로 레이블링하면 “설명 가능한” 돌파 필터로 재현 가능.
  - 기존 백테스트 파이프라인에 FinLLM-B식 근거 보고서를 붙여 신호 신뢰도/감시 자동화를 도모.

## 2. Opening Range Breakout Stock Trading Algorithmic Model (IJCI, 2016)
- **PDF**: `research-materials/saved-papers/Opening_Range_Breakout_Stock_Trading_Algorithmic_Model.pdf`
- **핵심 요약**
  - 인도 BMSIT 연구팀이 단기 투자자를 위한 **Opening Range Breakout (ORB)** 추천 시스템을 제안.
  - 지표: 15분 개장 범위, 이동평균, 볼륨 스파이크, MACD 등을 조합한 하이브리드 룰 기반 엔진.
  - 목표는 **계산량 최소화 + 공간 효율성** 확보. R 프로토타입으로 시뮬레이션하며, 장 시작 직후 구간의 고/저를 중심으로 손절·익절을 자동화.
  - 리스크 관리를 위해 변동성 필터와 포지션 사이징 규칙(자본 대비 % 고정) 포함.
- **적용 포인트**
  - 기존 ORB 스크립트에 거래량 필터(개장 15분 평균 대비 X배)와 자동 리밸런싱 로직을 이 논문 구조대로 정리 가능.
  - 한국 지수선물(코스피200) 개장 시각에 맞춘 5~15분 범위로 백테스트 설계 참고.

## 3. Bootstrap Testing of Trading Strategies in Emerging Balkan Stock Markets (E+M Ekonomie a Management, 2017)
- **PDF**: `research-materials/saved-papers/Bootstrap_Trading_Rules_Balkan_Markets.pdf`
- **핵심 요약**
  - 발칸 6개 지수(BELEX15, CROBEX, SBITOP, MONEX20, MBI10 등)에 대해 **이동평균 / 필터 / TRB / 채널 돌파** 규칙을 현실 검정(Reality Check, Superior Predictive Ability)으로 평가.
  - AR(1)-GARCH(1,1) 잔차 기반 파라메트릭 부트스트랩 + Moving Block Bootstrap으로 데이터 스누핑 문제를 제어.
  - 거래 비용을 반영해도 5개 지수에서는 5% 유의수준에서 벤치마크 대비 초과수익 → **약형 효율성 기각**.
  - 다만 규칙별 승률보다 손익비 영향이 커 **거래 횟수 관리/필터링** 중요성을 강조.
- **적용 포인트**
  - Reality Check/Superior Predictive Ability 절차를 그대로 이식하면 국내 지수/섹터 돌파 전략의 **데이터 스누핑 위험**을 정량화 가능.
  - TRB 규칙별 파라미터(상·하한 % 폭)를 한국 시장에 맞추어 재현하고, bootstrap 검정 코드를 Python으로 옮길 계획.

---
- 이 파일은 학술 자료 다운로드가 완료될 때마다 추가/업데이트합니다.

