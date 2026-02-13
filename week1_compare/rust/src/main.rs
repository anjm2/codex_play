use std::collections::HashMap;
use std::env;
use std::fs;

fn normalize_words(text: &str) -> Vec<String> {
    text.split(|c: char| !c.is_ascii_alphabetic())
        .filter(|w| !w.is_empty())
        .map(|w| w.to_ascii_lowercase())
        .collect()
}

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

fn filter_lines(path: &str, keyword: &str) -> Result<Vec<String>, String> {
    let content = fs::read_to_string(path).map_err(|e| format!("failed to read file: {e}"))?;
    let key = keyword.to_ascii_lowercase();

    Ok(content
        .lines()
        .filter(|line| line.to_ascii_lowercase().contains(&key))
        .map(String::from)
        .collect())
}

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
