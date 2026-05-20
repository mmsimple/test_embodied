# 进阶 2：Timeout 统计和风险结论

## 本节目标

在原来的日志分析脚本基础上，新增两个能力：

- 统计日志中包含 `timeout` 的数量
- 当没有严重错误但 `WARN` 数量大于 5 时，结论输出 `RISK`

## 为什么要这样做

真实机器人测试里，不是只有 `ERROR` 才值得关注。

例如：

- `timeout` 可能代表电机、传感器、网络、服务调用或控制链路响应异常
- 大量 `WARN` 可能说明系统还没崩溃，但稳定性已经变差

所以测试结论可以分成三类：

| 结论 | 含义 |
| --- | --- |
| PASS | 没有严重错误，警告数量可接受 |
| RISK | 没有严重错误，但警告数量偏多 |
| FAIL | 出现 `ERROR` 或 `EXCEPTION` |

## 新增逻辑 1：统计 timeout

代码：

```python
timeout_count = sum(
    1 for entry in parsed_entries if "timeout" in entry["message"].lower()
)
```

含义：

- 遍历所有已经解析成功的日志
- 把 `message` 转成小写
- 判断里面是否包含 `timeout`
- 包含就计数一次

为什么使用 `.lower()`：

```text
timeout
Timeout
TIMEOUT
```

这几种写法都应该被识别为同一类问题。

## 新增逻辑 2：判断 RISK

代码：

```python
if severe_count > 0:
    result = "FAIL"
elif warn_count > 5:
    result = "RISK"
else:
    result = "PASS"
```

判断顺序很重要：

1. 只要有严重错误，优先判定为 `FAIL`
2. 没有严重错误，但 `WARN` 超过 5，判定为 `RISK`
3. 两者都没有，判定为 `PASS`

## 运行 FAIL 样例

```powershell
python .\project_01_log_analyzer\analyze_robot_log.py
```

默认分析：

```text
project_01_log_analyzer/sample_robot.log
```

这个样例里有 `ERROR` 和 `EXCEPTION`，所以结论是 `FAIL`。

## 运行 RISK 样例

```powershell
python .\project_01_log_analyzer\analyze_robot_log.py --input .\project_01_log_analyzer\sample_warn_risk.log --output .\project_01_log_analyzer\reports\warn_risk_report.md
```

这个样例没有 `ERROR` 和 `EXCEPTION`，但有 6 条 `WARN`，所以结论是 `RISK`。

## 你应该掌握的点

- 不是所有问题都要等到 `ERROR` 才处理
- 测试工程师需要把日志转换成风险判断
- 风险规则要有清晰优先级
- 报告里既要给统计数字，也要给明确结论

## 练习

修改脚本，新增一个规则：

- 如果 `timeout` 数量大于等于 3，结论也应该是 `RISK`

提示：

```python
elif warn_count > 5 or timeout_count >= 3:
    result = "RISK"
```
