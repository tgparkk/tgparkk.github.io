# 조사 자료 수집 도구

## 사용 방법

### 1. 자료 다운로드 스크립트

**파일**: `collect-sources.py`

**설치**:
```bash
pip install requests beautifulsoup4
```

**실행**:
```bash
python research-tools/collect-sources.py
```

**기능**:
- Investopedia, Axi, IG International 등 주요 온라인 자료 자동 다운로드
- 텍스트 파일로 저장 (메타데이터 포함)
- `research-materials/saved-articles/` 폴더에 저장

**결과**:
- 각 자료가 개별 텍스트 파일로 저장됨
- 파일명: `[제목].txt`
- 내용: URL, 다운로드 날짜, 본문

### 2. 수동 다운로드 방법

스크립트가 작동하지 않을 경우:

1. **브라우저에서 직접 접속**
   - 각 URL을 브라우저에서 열기
   - Ctrl+S (또는 Cmd+S)로 저장
   - PDF 또는 HTML 형식으로 저장

2. **브라우저 확장 프로그램 사용**
   - "SingleFile" 확장 프로그램 (Chrome/Firefox)
   - 웹 페이지를 단일 HTML 파일로 저장

3. **인쇄 → PDF**
   - Ctrl+P (또는 Cmd+P)
   - "PDF로 저장" 선택

### 3. 자료 정리 방법

다운로드한 자료는 다음 형식으로 정리:

```
research-materials/
├── saved-articles/          # 온라인 글
│   ├── The_Anatomy_of_Trading_Breakouts.txt
│   └── ...
├── saved-papers/            # 학술 논문 PDF
│   └── ...
└── notes/                   # 읽은 내용 요약
    └── ...
```

### 4. 읽기 체크리스트

각 자료를 읽을 때:

- [ ] 핵심 내용 3-5줄 요약
- [ ] 인용할 만한 문구 기록
- [ ] 수치/통계 기록 (승률, 수익률 등)
- [ ] 실전 팁 정리
- [ ] 조사 노트에 기록

---

## 다음 단계

1. 자료 다운로드 완료 후
2. 각 자료 읽기
3. `research-notes/breakout-strategy-research.md`에 정리
4. 핵심 내용과 인용구 기록

