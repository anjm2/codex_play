use std::collections::HashMap;
use std::env;
use std::fs;

// Python의 정규식 토큰화와 비슷한 역할이지만,
// Rust에서는 &str 슬라이스를 순회한 뒤 String으로 명시적으로 소유권을 만든다.
fn normalize_words(text: &str) -> Vec<String> {
    text.split(|c: char| !c.is_ascii_alphabetic())
        .filter(|w| !w.is_empty())
        .map(|w| w.to_ascii_lowercase())
        .collect()
}

// Python Counter와 유사한 빈도 집계.
// 차이점: Rust는 실패 가능성을 Result로 타입에 드러내며,
// 파일 읽기 실패를 컴파일러가 인지 가능한 흐름으로 강제한다.
fn top_words(path: &str, top_n: usize) -> Result<Vec<(String, usize)>, String> {
    let content = fs::read_to_string(path).map_err(|e| format!("failed to read file: {e}"))?;
    let mut counts: HashMap<String, usize> = HashMap::new();

    for word in normalize_words(&content) {
        *counts.entry(word).or_insert(0) += 1;
    }

    let mut items: Vec<(String, usize)> = counts.into_iter().collect();
    items.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));
    items.truncate(top_n);
    Ok(items)
}

// Python 리스트 컴프리헨션과 비슷한 필터 로직.
// 여기서도 I/O 에러를 예외(throw) 대신 Result로 반환한다.
fn filter_lines(path: &str, keyword: &str) -> Result<Vec<String>, String> {
    let content = fs::read_to_string(path).map_err(|e| format!("failed to read file: {e}"))?;
    let key = keyword.to_ascii_lowercase();

    Ok(content
        .lines()
        .filter(|line| line.to_ascii_lowercase().contains(&key))
        .map(String::from)
        .collect())
}

// Python argparse와 달리 라이브러리 없이 직접 파싱한 버전.
// 학습 포인트: Option<String>으로 "있을 수도/없을 수도" 있는 값을 타입으로 표현한다.
fn parse_args() -> Result<(String, usize, Option<String>), String> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        return Err("usage: cargo run -- <file> [--top N] [--contains KEYWORD]".to_string());
    }

    let file = args[1].clone();
    let mut top_n = 5usize;
    let mut contains: Option<String> = None;

    let mut i = 2;
    while i < args.len() {
        match args[i].as_str() {
            "--top" => {
                i += 1;
                let value = args
                    .get(i)
                    .ok_or_else(|| "missing value for --top".to_string())?;
                top_n = value
                    .parse::<usize>()
                    .map_err(|_| "--top must be a positive integer".to_string())?;
            }
            "--contains" => {
                i += 1;
                let value = args
                    .get(i)
                    .ok_or_else(|| "missing value for --contains".to_string())?;
                contains = Some(value.clone());
            }
            unknown => {
                return Err(format!("unknown argument: {unknown}"));
            }
        }
        i += 1;
    }

    Ok((file, top_n, contains))
}

fn main() {
    // Python이라면 예외 처리(try/except)로 둘 수 있는 부분을,
    // Rust에서는 match로 성공/실패를 명시적으로 분기한다.
    let (file, top_n, contains) = match parse_args() {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{e}");
            std::process::exit(1);
        }
    };

    println!("[Top words]");
    match top_words(&file, top_n) {
        Ok(words) => {
            for (word, count) in words {
                println!("{word}: {count}");
            }
        }
        Err(e) => {
            eprintln!("{e}");
            std::process::exit(1);
        }
    }

    if let Some(keyword) = contains {
        println!("\n[Filtered lines]");
        match filter_lines(&file, &keyword) {
            Ok(lines) => {
                for line in lines {
                    println!("{line}");
                }
            }
            Err(e) => {
                eprintln!("{e}");
                std::process::exit(1);
            }
        }
    }
}
