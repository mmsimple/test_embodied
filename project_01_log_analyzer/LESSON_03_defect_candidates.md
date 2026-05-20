# 进阶 3：从日志生成缺陷候选列表

## 本节目标

把日志分析结果进一步转成测试工作中更有用的输出：缺陷候选列表。

上一节我们已经能回答：

- 有多少错误
- 哪些模块问题最多
- 哪些错误最高频
- 最终是 `PASS`、`RISK` 还是 `FAIL`

这一节要继续回答：

- 哪些问题应该被提成 Bug
- Bug 标题可以怎么写
- 同一类错误出现了多少次

## 为什么需要缺陷候选列表

测试工程师不能只把整份日志丢给研发。

更好的方式是把日志加工成清晰的问题线索，例如：

| 建议标题 | 模块 | 错误信息 | 出现次数 |
| --- | --- | --- | ---: |
| `[control] motor timeout` | control | motor timeout | 2 |

这样研发可以很快知道：

- 问题属于哪个模块
- 具体现象是什么
- 是偶发还是高频
- 是否值得单独建 Bug

## 新增逻辑

代码：

```python
defect_candidate_counter = Counter(
    (entry["module"], entry["message"])
    for entry in parsed_entries
    if entry["level"] in SEVERE_LEVELS
)
```

含义：

- 只看 `ERROR` 和 `EXCEPTION`
- 把 `module` 和 `message` 组合成一类问题
- 统计同一模块、同一错误信息出现了多少次

例如日志中有两行：

```text
2026-05-20 09:00:05.883 [ERROR] [control] motor timeout
2026-05-20 09:00:08.912 [ERROR] [control] motor timeout
```

会被统计成：

```text
模块：control
错误信息：motor timeout
出现次数：2
```

## 生成表格

代码：

```python
def format_defect_candidates(counter):
    if not counter:
        return "_无_"

    lines = [
        "| 建议标题 | 模块 | 错误信息 | 出现次数 |",
        "| --- | --- | --- | ---: |",
    ]
    for (module, message), count in counter.most_common():
        title = f"[{module}] {message}"
        lines.append(f"| {title} | {module} | {message} | {count} |")
    return "\n".join(lines)
```

这段代码的作用是把统计结果转成 Markdown 表格。

## 运行方式

```powershell
python .\project_01_log_analyzer\analyze_robot_log.py
```

然后打开：

```text
project_01_log_analyzer/reports/sample_report.md
```

查看 `缺陷候选列表`。

## 测试工程师视角

看到缺陷候选列表后，不要马上机械地全都提 Bug。

你需要判断：

- 是否能复现
- 是否影响主流程
- 是否有明确模块归属
- 是否已有重复 Bug
- 是否需要补充视频、截图、rosbag 或更完整日志

## 练习

给缺陷候选列表增加一列：`建议优先级`。

规则：

- 出现次数大于等于 2：`P1`
- 出现次数等于 1：`P2`

提示：

```python
priority = "P1" if count >= 2 else "P2"
```
