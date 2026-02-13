# codex_play

## Python 개발자를 위한 Rust 4주 학습 로드맵

### 목표
- Python의 생산성 감각을 유지하면서 Rust의 성능/안전성 모델에 익숙해진다.
- 4주 후에는 작은 CLI 또는 간단한 웹 API를 Rust로 단독 구현할 수 있다.

---

### 1주차: 문법 + 소유권(Ownership) 기초

#### 학습 주제
- 변수/불변성(`let`, `mut`)
- 함수, 제어문, `match`
- 소유권/빌림/참조(`&`, `&mut`)
- `String` vs `&str`

#### Python 관점 포인트
- Python의 참조/GC와 달리 Rust는 소유권 규칙으로 메모리를 추적한다.
- "왜 이 코드가 컴파일 에러인지"를 이해하는 과정이 핵심이다.

#### 실습
- 문자열 처리 CLI 2개 만들기
  - 파일에서 줄 읽어 단어 빈도 집계
  - 간단한 로그 필터링 도구

#### 체크리스트
- `borrow checker` 오류 메시지를 스스로 해석 가능
- `clone`을 무작정 쓰지 않고 참조로 해결 시도 가능

#### 체크리스트 해설 (무슨 뜻인지 + 어떤 코드 볼지)
- `borrow checker` 해석 가능:
  - 의미: 컴파일 에러에서 "누가 소유하고(ownership), 어디서 빌렸는지(borrow), 언제까지 유효한지(lifetime)"를 읽고 수정 방향을 잡을 수 있다는 뜻.
  - 먼저 볼 코드: `week1_compare/rust/src/main.rs`의 `normalize_words`, `top_words`, `filter_lines`. (`&str` 입력과 `String` 소유권 생성 흐름 확인)
- `clone` 남발하지 않기:
  - 의미: 에러를 피하려고 복제를 습관적으로 쓰기보다, `&str`/`&String` 같은 참조 전달로 해결을 먼저 시도하라는 뜻.
  - 먼저 볼 코드: `top_words(&file, top_n)`, `filter_lines(&file, &keyword)`처럼 값 소유권을 옮기지 않고 참조로 호출하는 부분.

#### 1주차에 실제로 해볼 미니 연습
1. `main.rs`에서 `top_words(&file, top_n)`를 `top_words(file, top_n)`로 바꿔 컴파일 에러를 확인한다.
2. 에러 메시지를 읽고 왜 `file`이 move되는지 이해한 뒤 다시 `&file`로 고친다.
3. `contains = Some(value.clone())` 줄을 보고, 왜 여기서는 clone이 필요한지(소유권 보존) 스스로 설명해본다.
4. 같은 요구사항의 Python 코드(`week1_compare/python/word_count.py`)와 비교해 "왜 Python에서는 같은 종류의 에러가 컴파일 단계에 안 보이는지"를 정리한다.

---

### 2주차: 컬렉션, 에러 처리, 모듈화

#### 학습 주제
- `Vec`, `HashMap`, 반복자(`iter`, `map`, `filter`)
- 에러 처리(`Result`, `Option`, `?`)
- 패키지/모듈 구조(`mod`, `pub`)
- 테스트 기초(`cargo test`)

#### Python 관점 포인트
- 예외 중심 흐름 대신 `Result`를 타입으로 다루는 사고에 익숙해지기
- list/dict comprehension 감각을 iterator 체인으로 옮겨보기

#### 실습
- CSV 파서 미니 프로젝트
  - 파일 로드 → 유효성 검사 → 요약 통계 출력
  - 잘못된 입력은 에러 메시지로 반환

#### 체크리스트
- `unwrap()` 남발하지 않고 의미 있는 에러 처리 가능
- 최소 5개 이상의 단위 테스트 작성

---

### 3주차: Trait, 제네릭, 비동기 기초

#### 학습 주제
- `trait`, 제네릭, 라이프타임 개념 맛보기
- `serde`로 JSON 직렬화/역직렬화
- 비동기 기초(`tokio`, `async/await`)

#### Python 관점 포인트
- duck typing 대신 "trait 경계"로 동작 계약을 명시하는 감각 익히기
- `asyncio` 경험이 있다면 Rust의 `Future` 실행 모델 차이 이해하기

#### 실습
- 외부 API 호출기
  - HTTP 요청 → JSON 파싱 → 결과 캐시(메모리)
  - 동시 요청 처리(비동기)

#### 체크리스트
- trait 기반으로 코드 분리(예: 저장소 인터페이스)
- 동시 요청 처리 시 데이터 경쟁 없이 구현 가능

---

### 4주차: 작은 프로덕션 스타일 프로젝트

#### 학습 주제
- 프로젝트 구조화(도메인/인프라 분리)
- 로깅(`tracing`), 설정 파일, CLI 인자 처리(`clap`)
- 릴리즈 빌드/성능 점검(`cargo build --release`, `criterion` 맛보기)

#### 실습(택1)
1. TODO CLI
   - CRUD, 파일 저장(JSON), 테스트 포함
2. 간단한 REST API (`axum`)
   - 메모리 저장소 + 기본 검증 + 에러 응답 통일

#### 체크리스트
- README에 실행 방법/설계 요약 작성
- 테스트 + lint + format 자동화

---

## 매주 공통 루틴
- 포맷: `cargo fmt`
- 린트: `cargo clippy -- -D warnings`
- 테스트: `cargo test`
- 회고: "Python이라면 어떻게 짰을까? Rust에서는 왜 다르게 짜야 할까?" 3줄 기록

## 추천 학습 순서(도구)
1. `rustup`, `cargo` 기본
2. `clippy`, `rustfmt`
3. `serde`, `reqwest`, `tokio`
4. `axum` 또는 `clap`

## 학습 팁
- 초반 2주는 "속도"보다 "컴파일 에러 이해"에 집중하는 편이 장기적으로 빠르다.
- 막히면 코드를 줄여 최소 재현 예제로 바꿔서 원인을 먼저 확인하자.
- Rust는 "한 번 맞게 설계하면 유지보수가 쉬워지는" 언어에 가깝다.

## 1주차 비교 실습: Rust vs Python

아래 예제는 같은 요구사항(단어 빈도 집계 + 키워드 포함 줄 필터링)을 Python과 Rust로 각각 구현한 것입니다.

### 파일 구조
- `week1_compare/sample_input.txt`
- `week1_compare/python/word_count.py`
- `week1_compare/rust/src/main.rs`

### 실행 방법

#### Python 버전
```bash
python3 week1_compare/python/word_count.py week1_compare/sample_input.txt --top 5 --contains rust
```

#### Rust 버전
```bash
cd week1_compare/rust
cargo run -- ../sample_input.txt --top 5 --contains rust
```

#### Windows에서 `link.exe not found` 오류가 날 때
- 원인: Rust 코드 문제가 아니라, **MSVC C/C++ 링커(`link.exe`)가 설치/환경등록되지 않은 상태**입니다.
- 빠른 해결(권장):
  1. Visual Studio Installer 실행
  2. **Build Tools for Visual Studio 2019/2022** 설치(또는 Visual Studio Community)
  3. 워크로드에서 **Desktop development with C++** 선택
  4. 설치 후 **x64 Native Tools Command Prompt for VS** 또는 새 PowerShell/CMD에서 다시 실행

```bash
cd week1_compare/rust
cargo run -- ../sample_input.txt --top 5 --contains rust
```

- 대안(툴체인 변경): `gnu` 타깃을 사용하면 `link.exe` 대신 GNU 툴체인을 사용할 수 있습니다.

```bash
rustup toolchain install stable-x86_64-pc-windows-gnu
rustup default stable-x86_64-pc-windows-gnu
cargo run -- ../sample_input.txt --top 5 --contains rust
```

- 참고: VS Code만 설치되어 있으면 빌드 도구가 없는 경우가 많아 동일 오류가 발생할 수 있습니다.

### 비교 포인트
- Python: 코드가 짧고 빠르게 작성 가능 (`Counter`, `argparse`).
- Rust: 소유권/에러 처리(`Result`)를 통해 실행 전 안정성을 높일 수 있음.
- Python은 런타임 예외 중심, Rust는 컴파일 타임 검증 중심.
