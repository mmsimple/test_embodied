# 进阶 4：导出缺陷候选 CSV

## 本节目标

把缺陷候选列表从 Markdown 报告中单独导出成 CSV 文件。

CSV 更适合这些场景：

- 粘贴到测试日报
- 交给研发负责人快速筛选
- 导入缺陷管理平台
- 用 Excel 做排序和过滤

## 新增命令

默认运行：

```powershell
python .\project_01_log_analyzer\analyze_robot_log.py
```

会同时生成两个文件：

```text
project_01_log_analyzer/reports/sample_report.md
project_01_log_analyzer/reports/sample_report_defects.csv
```

也可以指定 CSV 输出路径：

```powershell
python .\project_01_log_analyzer\analyze_robot_log.py --csv-output .\project_01_log_analyzer\reports\defects.csv
```

## 新增参数

代码：

```python
parser.add_argument("--csv-output", help="Path to the defect candidates CSV file.")
```

作用：

- 允许用户指定缺陷候选 CSV 的输出路径
- 如果不指定，脚本会自动使用报告文件名生成 CSV 路径

例如：

```text
sample_report.md
```

会对应生成：

```text
sample_report_defects.csv
```

## 生成 CSV 数据行

代码：

```python
def build_defect_candidate_rows(counter):
    rows = []
    for (module, message), count in counter.most_common():
        priority = "P1" if count >= 2 else "P2"
        rows.append(
            {
                "title": f"[{module}] {message}",
                "module": module,
                "message": message,
                "count": count,
                "priority": priority,
            }
        )
    return rows
```

这段代码把原来的统计结果转成一行一行的数据。

每一行代表一个缺陷候选项：

- `title`：建议 Bug 标题
- `module`：模块
- `message`：错误信息
- `count`：出现次数
- `priority`：建议优先级

## 写入 CSV 文件

代码：

```python
def write_defect_candidates_csv(counter, csv_path):
    rows = build_defect_candidate_rows(counter)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["title", "module", "message", "count", "priority"],
        )
        writer.writeheader()
        writer.writerows(rows)
```

关键点：

- `csv.DictWriter` 用来写表格型数据
- `writeheader()` 写表头
- `writerows(rows)` 写所有数据行
- `encoding="utf-8-sig"` 可以让 Excel 更稳定地识别中文
- `newline=""` 可以避免 Windows 下 CSV 出现多余空行

## 测试工程师视角

Markdown 报告适合阅读，CSV 适合流转和二次处理。

这类工具的价值在于：

- 减少手工整理日志的时间
- 让问题描述更统一
- 让高频问题更容易被发现
- 让测试数据可以进入日报、缺陷平台或质量看板

## 练习

给 CSV 增加一列：`suggestion`。

规则：

- 如果 `priority` 是 `P1`，建议写：`优先建 Bug 并补充复现材料`
- 如果 `priority` 是 `P2`，建议写：`观察是否复现，必要时合并到相关 Bug`

提示：

```python
suggestion = (
    "优先建 Bug 并补充复现材料"
    if priority == "P1"
    else "观察是否复现，必要时合并到相关 Bug"
)
```
