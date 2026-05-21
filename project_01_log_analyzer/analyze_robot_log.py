import argparse
import csv
import re
from collections import Counter
from pathlib import Path


LOG_PATTERN = re.compile(
    r"^(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) "
    r"\[(?P<level>[A-Z]+)\] "
    r"\[(?P<module>[a-zA-Z0-9_-]+)\] "
    r"(?P<message>.*)$"
)

ISSUE_LEVELS = {"WARN", "ERROR", "EXCEPTION"}
SEVERE_LEVELS = {"ERROR", "EXCEPTION"}


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze robot runtime logs.")
    parser.add_argument("--input", help="Path to the robot log file.")
    parser.add_argument("--input-dir", help="Path to a directory containing log files.")
    parser.add_argument("--output", help="Path to the Markdown report.")
    parser.add_argument("--csv-output", help="Path to the defect candidates CSV file.")
    parser.add_argument("--summary-output", help="Path to the batch summary CSV file.")
    return parser.parse_args()


def parse_log_line(line):
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None
    return match.groupdict()


def analyze_log(log_path):
    total_lines = 0
    parsed_entries = []
    invalid_lines = []

    with log_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            total_lines += 1
            entry = parse_log_line(line)
            if entry is None:
                invalid_lines.append((line_number, line.strip()))
                continue
            parsed_entries.append(entry)

    level_counter = Counter(entry["level"] for entry in parsed_entries)
    module_issue_counter = Counter(
        entry["module"] for entry in parsed_entries if entry["level"] in ISSUE_LEVELS
    )
    severe_message_counter = Counter(
        entry["message"] for entry in parsed_entries if entry["level"] in SEVERE_LEVELS
    )
    defect_candidate_counter = Counter(
        (entry["module"], entry["message"])
        for entry in parsed_entries
        if entry["level"] in SEVERE_LEVELS
    )
    timeout_count = sum(
        1 for entry in parsed_entries if "timeout" in entry["message"].lower()
    )

    severe_count = sum(level_counter[level] for level in SEVERE_LEVELS)
    warn_count = level_counter["WARN"]
    if severe_count > 0:
        result = "FAIL"
    elif warn_count > 5 or timeout_count >= 3:
        result = "RISK"
    else:
        result = "PASS"

    return {
        "total_lines": total_lines,
        "parsed_count": len(parsed_entries),
        "invalid_lines": invalid_lines,
        "level_counter": level_counter,
        "module_issue_counter": module_issue_counter,
        "severe_message_counter": severe_message_counter,
        "defect_candidate_counter": defect_candidate_counter,
        "severe_count": severe_count,
        "warn_count": warn_count,
        "timeout_count": timeout_count,
        "result": result,
    }


def format_counter_table(counter, headers):
    if not counter:
        return "_无_"

    lines = [
        f"| {headers[0]} | {headers[1]} |",
        "| --- | ---: |",
    ]
    for key, count in counter.most_common():
        lines.append(f"| {key} | {count} |")
    return "\n".join(lines)


def format_defect_candidates(counter):
    if not counter:
        return "_无_"

    lines = [
        "| 建议标题 | 模块 | 错误信息 | 出现次数 | 建议优先级 |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for (module, message), count in counter.most_common():
        title = f"[{module}] {message}"
        priority = "P1" if count >= 2 else "P2"
        lines.append(f"| {title} | {module} | {message} | {count} | {priority} |")
    return "\n".join(lines)


def build_defect_candidate_rows(counter):
    rows = []
    for (module, message), count in counter.most_common():
        priority = "P1" if count >= 2 else "P2"
        suggestion = (
            "优先建 Bug 并补充复现材料"
            if priority == "P1"
            else "观察是否复现，必要时合并到相关 Bug"
        )
        rows.append(
            {
                "title": f"[{module}] {message}",
                "module": module,
                "message": message,
                "count": count,
                "priority": priority,
                "suggestion": suggestion,
            }
        )
    return rows


def write_defect_candidates_csv(counter, csv_path):
    rows = build_defect_candidate_rows(counter)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["title", "module", "message", "count", "priority", "suggestion"],
        )
        writer.writeheader()
        writer.writerows(rows)


def build_summary_row(log_path, analysis):
    top_issue_module = ""
    if analysis["module_issue_counter"]:
        top_issue_module = analysis["module_issue_counter"].most_common(1)[0][0]

    return {
        "log_file": log_path.name,
        "result": analysis["result"],
        "release_blocker": "YES" if analysis["result"] == "FAIL" else "NO",
        "total_lines": analysis["total_lines"],
        "parsed_count": analysis["parsed_count"],
        "invalid_count": len(analysis["invalid_lines"]),
        "warn_count": analysis["warn_count"],
        "severe_count": analysis["severe_count"],
        "timeout_count": analysis["timeout_count"],
        "top_issue_module": top_issue_module,
    }


def write_batch_summary_csv(input_dir, summary_path):
    log_paths = sorted(input_dir.glob("*.log"))
    rows = [build_summary_row(log_path, analyze_log(log_path)) for log_path in log_paths]
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    with summary_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "log_file",
                "result",
                "release_blocker",
                "total_lines",
                "parsed_count",
                "invalid_count",
                "warn_count",
                "severe_count",
                "timeout_count",
                "top_issue_module",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    return rows


def generate_report(analysis, log_path):
    invalid_preview = analysis["invalid_lines"][:5]
    invalid_lines_text = "_无_"

    if invalid_preview:
        invalid_lines_text = "\n".join(
            f"- 第 {line_number} 行：`{content}`"
            for line_number, content in invalid_preview
        )

    return f"""# 机器人日志分析报告

## 基本信息

- 日志文件：`{log_path}`
- 总行数：{analysis["total_lines"]}
- 可解析行数：{analysis["parsed_count"]}
- 无法解析行数：{len(analysis["invalid_lines"])}
- 分析结论：**{analysis["result"]}**
- Timeout 日志数量：{analysis["timeout_count"]}

## 日志等级统计

{format_counter_table(analysis["level_counter"], ("等级", "数量"))}

## 问题模块分布

统计范围：`WARN`、`ERROR`、`EXCEPTION`

{format_counter_table(analysis["module_issue_counter"], ("模块", "问题数量"))}

## 高频严重错误

统计范围：`ERROR`、`EXCEPTION`

{format_counter_table(analysis["severe_message_counter"], ("错误信息", "数量"))}

## 缺陷候选列表

统计范围：`ERROR`、`EXCEPTION`

{format_defect_candidates(analysis["defect_candidate_counter"])}

## 无法解析的日志行

{invalid_lines_text}

## 测试建议

- 优先处理 `ERROR` 和 `EXCEPTION` 对应的问题。
- 如果结论为 `RISK`，说明当前没有严重错误，但警告数量偏多，建议继续观察稳定性。
- 如果 `timeout` 数量偏高，建议重点检查通信、硬件响应、控制链路或依赖服务。
- 如果某个模块问题数量明显集中，建议先检查该模块最近的版本变更、配置和依赖服务。
- 对高频严重错误补充复现步骤、视频、完整日志和必要的数据包。
"""


def main():
    args = parse_args()
    project_dir = Path(__file__).resolve().parent

    if args.input_dir:
        input_dir = Path(args.input_dir)
        summary_output_path = (
            Path(args.summary_output)
            if args.summary_output
            else project_dir / "reports" / "batch_summary.csv"
        )

        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

        if not input_dir.is_dir():
            raise NotADirectoryError(f"Input path is not a directory: {input_dir}")

        if summary_output_path.suffix.lower() != ".csv":
            raise ValueError(
                "Summary output path should be a CSV file ending with .csv: "
                f"{summary_output_path}"
            )

        rows = write_batch_summary_csv(input_dir, summary_output_path)
        print(f"Input directory: {input_dir}")
        print(f"Batch summary generated: {summary_output_path}")
        print(f"Log files analyzed: {len(rows)}")
        return

    log_path = Path(args.input) if args.input else project_dir / "sample_robot.log"
    output_path = (
        Path(args.output)
        if args.output
        else project_dir / "reports" / "sample_report.md"
    )
    csv_output_path = (
        Path(args.csv_output)
        if args.csv_output
        else output_path.with_name(output_path.stem + "_defects.csv")
    )

    if not log_path.exists():
        raise FileNotFoundError(f"Input log does not exist: {log_path}")

    if output_path.exists() and output_path.is_dir():
        raise IsADirectoryError(
            f"Output path is a directory, please provide a report file path: {output_path}"
        )

    if output_path.suffix.lower() != ".md":
        raise ValueError(
            f"Output path should be a Markdown file ending with .md: {output_path}"
        )

    if csv_output_path.suffix.lower() != ".csv":
        raise ValueError(
            f"CSV output path should be a CSV file ending with .csv: {csv_output_path}"
        )

    analysis = analyze_log(log_path)
    report = generate_report(analysis, log_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    write_defect_candidates_csv(
        analysis["defect_candidate_counter"],
        csv_output_path,
    )
    print(f"Input log: {log_path}")
    print(f"Report generated: {output_path}")
    print(f"Defect CSV generated: {csv_output_path}")
    print(f"Result: {analysis['result']}")


if __name__ == "__main__":
    main()
