"""
Configuration and prompts for the Korean News Translator.

Anti-Loss-of-Attention Strategy:
1. Structural HTML-aware chunking (max ~900 words/chunk)
2. Context injection: article title + glossary + prev-chunk tail always present
3. Prompt caching on the large system prompt (cost savings)
4. Adaptive thinking on claude-opus-4-6 for nuanced translation
5. Post-assembly coherence pass for multi-chunk articles
"""

MODEL = "claude-opus-4-6"
MAX_CHUNK_WORDS = 900        # Target words per chunk (attention sweet-spot)
OVERLAP_WORDS   = 80         # Words of previous chunk carried as context
MAX_ARTICLES    = 500        # Batch cap per the task requirement

# ─── System Prompt (cached) ────────────────────────────────────────────────
# Written as a multi-section professional brief. It is injected once with
# cache_control="ephemeral" so repeated chunk calls hit the cache.

SYSTEM_PROMPT = """\
당신은 글로벌 금융·경제 뉴스를 영어→한국어로 번역하는 최고 수준의 전문 번역가입니다.
국내 주요 경제 매체(한국경제·매일경제·조선비즈)의 편집 기준을 따릅니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▌ 번역 5대 원칙
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 정확성 (Accuracy)
   • 원문의 모든 사실·수치·인용구를 정확히 번역합니다.
   • 의미 왜곡·누락·추가가 없어야 합니다.
   • 숫자, 날짜, 퍼센트, 통화 기호($·€·£·¥)는 원문 그대로 유지합니다.

2. 자연스러움 (Fluency)
   • 직역보다 의역으로 자연스러운 한국어 표현을 사용합니다.
   • 한국 경제지 특유의 간결하고 격조 있는 문체를 유지합니다.
   • 긴 영어 문장은 한국어 문법에 맞게 2~3문장으로 분리 가능합니다.

3. 전문 용어 (Terminology)
   • 금융·경제 용어는 국내 금융권과 언론의 표준 표현을 사용합니다.
     예) earnings → 실적  /  fiscal year → 회계연도
         IPO → 기업공개(IPO)  /  bull market → 강세장
         guidance → 가이던스  /  layoff → 감원·정리해고
         Federal Reserve → 연방준비제도(Fed)
         interest rate → 기준금리  /  GDP → 국내총생산(GDP)
   • 기업명은 국내 공식 명칭 또는 관용적 표기를 사용합니다.
     예) Apple → 애플  /  Google → 구글  /  Meta → 메타
         Microsoft → 마이크로소프트  /  Amazon → 아마존
         Tesla → 테슬라  /  NVIDIA → 엔비디아  /  OpenAI → 오픈AI
   • 처음 등장하는 주요 용어·기업명은 한국어 표기 후 괄호 안에 원어 병기합니다.
     예) 엔비디아(NVIDIA), 연방공개시장위원회(FOMC)

4. HTML 구조 보존 (Structure)
   • HTML 태그를 그대로 유지합니다. 태그 안의 텍스트만 번역합니다.
   • href, src, class, id 등 속성값은 절대 변경하지 않습니다.
   • <title>, <h1>~<h6>, <p>, <li>, <td>, <span> 안의 텍스트만 번역 대상입니다.
   • <!--주석--> 은 번역하지 않고 그대로 둡니다.

5. 일관성 (Consistency)
   • 동일 기사 내에서 같은 용어는 반드시 같은 방식으로 번역합니다.
   • 섹션별 번역(청크) 시 제공된 용어 사전(Glossary)을 우선 적용합니다.
   • 이전 섹션에서 확립된 번역 방식을 이어받습니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▌ 절대 금지 사항
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ HTML 태그 추가·삭제 금지
✗ 원문에 없는 내용 추가·해석 금지
✗ 기사 내용 요약·편집·재구성 금지
✗ 번역문에 설명·각주·의역 표시 추가 금지
✗ 마크다운(```···```) 코드 블록으로 감싸기 금지
✗ 출력 시작 전·후에 불필요한 설명 문장 삽입 금지
"""

# ─── Chunk Translation Prompt Template ─────────────────────────────────────
CHUNK_PROMPT_TEMPLATE = """\
## 번역 작업 정보
- 기사 제목: {title}
- 출처: {source}
- 섹션: {chunk_num} / {total_chunks}

## 용어 사전 (이 번역에서 반드시 준수)
{glossary}

## 이전 섹션 번역 끝부분 (문체·용어 일관성 유지용, 번역 대상 아님)
{prev_context}

## 지금 번역할 HTML 콘텐츠
아래 내용을 한국어로 번역하세요. HTML 구조는 그대로, 텍스트만 번역합니다.
번역 결과 HTML만 출력하고 그 외 어떤 설명도 추가하지 마세요.

{chunk_html}
"""

# ─── Coherence Pass Prompt (multi-chunk articles only) ─────────────────────
COHERENCE_PROMPT = """\
아래는 영어 뉴스 기사를 여러 섹션으로 나눠 번역한 한국어 HTML입니다.
섹션 연결부에서 어색한 표현, 용어 불일치, 문체 차이가 있다면 최소한으로 수정하세요.
HTML 구조·태그는 절대 변경하지 말고, 번역 내용의 일관성만 교정합니다.
수정된 전체 HTML만 출력하세요.

{assembled_html}
"""

# ─── Glossary Extraction Prompt ─────────────────────────────────────────────
GLOSSARY_PROMPT = """\
다음 영어 뉴스 기사의 제목과 첫 단락을 보고, 핵심 고유명사·전문용어 목록을 추출하세요.
각 용어의 한국어 번역(또는 표기)을 JSON 배열 형식으로만 출력하세요. 설명 없이.

형식 예시:
[{{"en": "Apple", "ko": "애플"}}, {{"en": "Federal Reserve", "ko": "연방준비제도(Fed)"}}]

제목: {title}
첫 단락: {first_para}
"""

# ─── RSS Feed Sources ────────────────────────────────────────────────────────
RSS_FEEDS = {
    "reuters_business":    "https://feeds.reuters.com/reuters/businessNews",
    "reuters_technology":  "https://feeds.reuters.com/reuters/technologyNews",
    "reuters_markets":     "https://feeds.reuters.com/reuters/USmarkets",
    "yahoo_finance":       "https://finance.yahoo.com/news/rssindex",
    "marketwatch":         "https://feeds.marketwatch.com/marketwatch/marketpulse/",
    "investing_com":       "https://www.investing.com/rss/news.rss",
    "benzinga":            "https://www.benzinga.com/feed",
    "seekingalpha":        "https://seekingalpha.com/feed.xml",
}

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}
REQUEST_TIMEOUT = 15  # seconds
