# 进阶 6：批量分析多份日志

## 本节目标

把脚本从“分析单个日志”升级成“批量分析一个目录里的多份日志”。

真实测试工作中，你经常会遇到：

- 一轮稳定性测试产生多份日志
- 多台机器人各自产生日志
- 同一个版本跑了多轮回归测试
- 需要快速比较哪些日志是 `PASS`、`RISK`、`FAIL`

这时逐个打开日志效率很低，更好的方式是生成一份汇总表。

## 运行方式

分析 `project_01_log_analyzer` 目录下所有 `.log` 文件：

```powershell
python .\project_01_log_analyzer\analyze_robot_log.py --input-dir .\project_01_log_analyzer
```

默认会生成：

```text
project_01_log_analyzer/reports/batch_summary.csv
```

也可以指定汇总文件：

```powershell
python .\project_01_log_analyzer\analyze_robot_log.py --input-dir .\project_01_log_analyzer --summary-output .\project_01_log_analyzer\reports\my_batch_summary.csv
```

## 汇总表字段

CSV 中每一行代表一份日志：

| 字段 | 含义 |
| --- | --- |
| `log_file` | 日志文件名 |
| `result` | 分析结论：`PASS`、`RISK`、`FAIL` |
| `release_blocker` | 是否阻塞发布 |
| `total_lines` | 总行数 |
| `parsed_count` | 成功解析的行数 |
| `invalid_count` | 无法解析的行数 |
| `warn_count` | `WARN` 数量 |
| `severe_count` | `ERROR` 和 `EXCEPTION` 总数 |
| `timeout_count` | 包含 `timeout` 的日志数量 |
| `top_issue_module` | 问题最多的模块 |

## 新增参数

```python
parser.add_argument("--input-dir", help="Path to a directory containing log files.")
parser.add_argument("--summary-output", help="Path to the batch summary CSV file.")
```

含义：

- `--input-dir`：指定日志目录
- `--summary-output`：指定批量汇总 CSV 的输出路径

## 核心逻辑

```python
def write_batch_summary_csv(input_dir, summary_path):
    log_paths = sorted(input_dir.glob("*.log"))
    rows = [build_summary_row(log_path, analyze_log(log_path)) for log_path in log_paths]
    ...
    writer.writeheader()
    writer.writerows(rows)
```

这段代码做了三件事：

1. 找到目录下所有 `.log` 文件
2. 对每个日志调用 `analyze_log`
3. 把每份日志的结果写入同一个 CSV

## 测试工程师视角

批量汇总表的价值在于快速回答：

- 这一轮测试有几份日志失败
- 哪些日志风险最高
- 哪些模块最常出问题
- timeout 是否集中出现
- 是否需要阻塞版本发布

## 练习

给批量汇总 CSV 增加一列：`release_blocker`。

规则：

- 如果 `result` 是 `FAIL`，输出 `YES`
- 否则输出 `NO`

提示：

```python
"release_blocker": "YES" if analysis["result"] == "FAIL" else "NO"
```

当前项目已经完成这个练习，可以运行批量命令查看输出。
