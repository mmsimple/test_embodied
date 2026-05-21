# 项目 1：机器人日志分析脚本

## 项目目标

写一个 Python 工具，用来分析机器人运行日志，并生成 Markdown 格式的问题报告。

这个项目模拟入职后很常见的场景：

- 机器人运行异常
- 测试工程师拿到日志
- 需要快速判断错误数量、错误模块、高频问题和风险点
- 最后输出一份可以发给研发或测试负责人的分析报告

## 目录结构

```text
project_01_log_analyzer/
├── README.md
├── analyze_robot_log.py
├── sample_robot.log
└── reports/
```

## 日志格式

样例日志格式：

```text
2026-05-20 09:00:01.120 [INFO] [nav] navigation started
2026-05-20 09:00:02.422 [WARN] [perception] depth frame dropped
2026-05-20 09:00:05.883 [ERROR] [control] motor timeout
```

字段含义：

- 时间：`2026-05-20 09:00:01.120`
- 等级：`INFO`、`WARN`、`ERROR`、`EXCEPTION`
- 模块：`nav`、`perception`、`control` 等
- 消息：具体日志内容

## 运行方式

在当前目录执行：

```powershell
python .\project_01_log_analyzer\analyze_robot_log.py
```

脚本会默认读取：

```text
project_01_log_analyzer/sample_robot.log
```

并默认生成：

```text
project_01_log_analyzer/reports/sample_report.md
```

如果你想指定输入和输出文件，可以执行：

```powershell
python .\project_01_log_analyzer\analyze_robot_log.py --input .\project_01_log_analyzer\sample_robot.log --output .\project_01_log_analyzer\reports\sample_report.md
```

如果要在 PowerShell 里换行，行尾需要使用反引号 `` ` ``，并且反引号后面不能有空格：

```powershell
python .\project_01_log_analyzer\analyze_robot_log.py `
  --input .\project_01_log_analyzer\sample_robot.log `
  --output .\project_01_log_analyzer\reports\sample_report.md
```

如果 `--output` 后面只写了 `.`，脚本会把当前目录当作输出文件，导致无法写入报告。

## 你需要掌握的点

### 1. 日志统计

脚本会统计：

- 总日志行数
- 可解析日志行数
- 不同日志等级数量
- 不同模块的问题数量
- 高频错误消息

### 2. 问题级别

当前规则：

- `ERROR` 和 `EXCEPTION` 视为严重问题
- `WARN` 视为风险问题
- `INFO` 只作为背景信息

### 3. 报告结论

报告会根据严重问题数量生成一个简单结论：

- 没有严重问题：`PASS`
- 有严重问题：`FAIL`

## 练习任务

### 任务 1：跑通脚本

运行脚本并打开生成的报告，确认你能看懂每个统计项。

### 任务 2：新增统计规则

已经增加一个统计项：

- 统计包含 `timeout` 的日志数量

### 任务 3：新增风险判断

已经增加一个规则：

- 如果 `WARN` 数量大于 5，即使没有 `ERROR`，结论也应该是 `RISK`

可以阅读：

```text
project_01_log_analyzer/LESSON_02_timeout_and_risk.md
```

### 任务 4：运行 RISK 样例

```powershell
python .\project_01_log_analyzer\analyze_robot_log.py --input .\project_01_log_analyzer\sample_warn_risk.log --output .\project_01_log_analyzer\reports\warn_risk_report.md
```

### 任务 5：替换样例日志

把你自己构造的日志放进 `sample_robot.log`，观察报告变化。

### 任务 6：生成缺陷候选列表

阅读：

```text
project_01_log_analyzer/LESSON_03_defect_candidates.md
```

运行脚本后，在报告中查看 `缺陷候选列表`。

### 任务 7：导出缺陷候选 CSV

阅读：

```text
project_01_log_analyzer/LESSON_04_csv_export.md
```

运行脚本后，查看：

```text
project_01_log_analyzer/reports/sample_report_defects.csv
```

### 任务 8：给脚本加自动化测试

阅读：

```text
project_01_log_analyzer/LESSON_05_automated_tests.md
```

运行：

```powershell
python -m unittest .\project_01_log_analyzer\test_analyze_robot_log.py
```

### 任务 9：批量分析多份日志

阅读：

```text
project_01_log_analyzer/LESSON_06_batch_summary.md
```

运行：

```powershell
python .\project_01_log_analyzer\analyze_robot_log.py --input-dir .\project_01_log_analyzer
```

查看：

```text
project_01_log_analyzer/reports/batch_summary.csv
```

## 面试或入职表达方式

你可以这样介绍这个项目：

> 我做过一个机器人日志分析小工具，可以从运行日志中统计错误等级、模块分布和高频问题，并自动生成 Markdown 报告。这个工具可以帮助测试人员快速判断问题集中在哪些模块，提升问题复现和定位效率。
