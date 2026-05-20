# 进阶 5：给日志分析脚本加自动化测试

## 本节目标

给日志分析脚本补自动化测试，确保这些规则以后不会被改坏：

- 正确解析日志行
- 无效日志行返回 `None`
- 有 `ERROR` 时结论为 `FAIL`
- `WARN` 超过 5 条时结论为 `RISK`
- `timeout` 刚好 3 条时结论为 `RISK`
- 缺陷候选项能生成优先级和建议
- CSV 文件能正确写出

## 为什么测试脚本也要写测试

测试工程师写的工具本身也可能有 Bug。

例如：

- 把 `>= 3` 写成 `> 3`
- 忘记导出新增的 CSV 列
- 正则改坏导致日志解析失败
- 优先级规则被误改

自动化测试能帮助你快速发现这些问题。

## 测试文件

```text
project_01_log_analyzer/test_analyze_robot_log.py
```

## 运行测试

在项目根目录执行：

```powershell
python -m unittest .\project_01_log_analyzer\test_analyze_robot_log.py
```

成功时会看到类似：

```text
.......
----------------------------------------------------------------------
Ran 7 tests in 0.0xxs

OK
```

## 测试用例示例

```python
def test_risk_when_timeout_count_is_three(self):
    lines = [
        "2026-05-20 09:00:01.000 [WARN] [control] motor timeout",
        "2026-05-20 09:00:02.000 [WARN] [camera] frame timeout",
        "2026-05-20 09:00:03.000 [WARN] [task] service timeout",
    ]

    with tempfile.TemporaryDirectory() as temp_dir:
        log_path = Path(temp_dir) / "robot.log"
        log_path.write_text("\n".join(lines), encoding="utf-8")
        analysis = analyze_log(log_path)

    self.assertEqual(analysis["result"], "RISK")
    self.assertEqual(analysis["timeout_count"], 3)
```

这个用例专门防止把 `timeout_count >= 3` 错写成 `timeout_count > 3`。

## 关键工具

### unittest

Python 标准库自带的测试框架，不需要额外安装。

### tempfile

用于创建临时目录和临时文件。

好处：

- 不污染项目目录
- 每次测试都是干净环境
- 测试结束后自动清理

### assertEqual

判断实际结果是否等于期望结果。

例如：

```python
self.assertEqual(analysis["result"], "RISK")
```

## 测试工程师视角

自动化测试不是只给产品写，也应该给自己的测试工具写。

尤其是这些内容值得测试：

- 判断规则
- 边界条件
- 文件输入输出
- 异常格式
- 报告字段

## 练习

新增一个测试用例：

- 当日志里没有 `ERROR`、没有 `EXCEPTION`、`WARN` 不超过 5、`timeout` 少于 3 时，结论应该是 `PASS`

提示：

```python
def test_pass_when_no_risk_or_failure(self):
    ...
    self.assertEqual(analysis["result"], "PASS")
```
