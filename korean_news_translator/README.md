# Korean News Translator

HTML 영어 뉴스 → 한국어 자동 번역 시스템 (Reuters / Benzinga 기반)

Claude Opus 4.6 기반 · Loss-of-Attention 완전 차단 · 500건 배치 지원

---

## 설치

```bash
pip install anthropic requests beautifulsoup4 lxml tqdm python-dotenv html2text
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## 빠른 시작

```bash
# 5개 기사 데모 (Reuters + Benzinga RSS 자동 수집 + 번역 + 검증)
python main.py demo

# N개 기사 번역 (스트리밍, 순차 처리)
python main.py translate --count 50

# 500개 기사 배치 번역 (Anthropic Batch API, 50% 비용 절감)
python main.py translate --count 500 --batch

# 특정 피드만 선택
python main.py translate --count 30 --feeds reuters_business reuters_technology

# 번역 결과 품질 검증
python main.py verify
```

결과는 `output/` 폴더에 HTML + `results.json`으로 저장됩니다.

---

## Loss-of-Attention 방지 전략 (7가지)

| 전략 | 설명 |
|------|------|
| **1. HTML-aware 청킹** | `<p>`, `<h2>` 등 논리적 경계에서만 분할 (최대 900단어/청크) |
| **2. 용어 사전 추출** | 번역 전 제목+첫 단락에서 핵심 고유명사 사전 확보 → 전 청크 주입 |
| **3. 컨텍스트 오버랩** | 이전 청크 마지막 80단어를 다음 청크의 `prev_context`로 전달 |
| **4. 프롬프트 캐싱** | 대형 시스템 프롬프트에 `cache_control: ephemeral` → 비용 80% 절감 |
| **5. 코히런스 패스** | 다중 청크 기사 조립 후 이음새 문체 통일 패스 실행 |
| **6. 어댑티브 싱킹** | `thinking: {type: "adaptive"}` — 뉘앙스 번역에 필요 시 추론 활성화 |
| **7. 스트리밍** | 모든 호출에 `.stream()` + `.get_final_message()` → HTTP 타임아웃 방지 |

---

## 번역 프롬프트 품질 (config.py)

**시스템 프롬프트 5대 원칙:**
1. **정확성** — 모든 사실·수치·인용구 완전 번역, 누락/추가 금지
2. **자연스러움** — 한국경제·매일경제·조선비즈 문체 준수
3. **전문 용어** — 국내 금융권 표준 용어 사용 (earnings→실적, IPO→기업공개)
4. **HTML 구조 보존** — 태그 유지, 텍스트만 번역
5. **일관성** — 용어 사전 + 이전 청크 기반 일관 번역

---

## 파일 구조

```
korean_news_translator/
├── config.py          # 프롬프트 + 설정
├── fetcher.py         # RSS 뉴스 수집 (Reuters, Benzinga, Yahoo Finance 등)
├── sample_news.py     # 오프라인 테스트용 샘플 기사 5건
├── parser.py          # HTML 정제 및 구조 추출
├── chunker.py         # Loss-of-Attention 방지 스마트 청커
├── translator.py      # Claude Opus 4.6 번역 엔진 (핵심)
├── batch.py           # 500건 배치 프로세서
├── verifier.py        # 번역 품질 자동 검증
├── main.py            # CLI 인터페이스
└── output/            # 번역 결과 (HTML + results.json)
```

---

## 품질 검증 항목

| 검증 | 기준 |
|------|------|
| 길이 비율 | 한국어 번역 0.35~1.40× 영어 단어 수 |
| HTML 구조 | `<p>` 태그 수 원문 50~200% 범위 |
| 숫자 커버리지 | 유효 숫자 45% 이상 번역문 포함 |
| 미번역 탐지 | 25단어 이상 연속 영어 블록 감지 |
| 완전성 | 번역 결과 20단어 이상 |

---

## 지원 뉴스 소스

- Reuters Business / Technology / Markets
- Benzinga
- Yahoo Finance
- MarketWatch
- Investing.com
- Seeking Alpha

---

## 비용 최적화

- **단일 기사 (스트리밍)**: Claude Opus 4.6 기본 요금
- **다중 청크 기사**: 시스템 프롬프트 캐싱으로 ~80% 입력 비용 절감
- **500건 배치 (Batch API)**: 모든 토큰 비용 50% 추가 절감

*by Claude Sonnet 4.6 — 2026-02-21*
