# 机器人日志分析报告

## 基本信息

- 日志文件：`D:\lmm\code\test_embodied\project_01_log_analyzer\sample_robot.log`
- 总行数：15
- 可解析行数：14
- 无法解析行数：1
- 分析结论：**FAIL**
- Timeout 日志数量：2

## 日志等级统计

| 等级 | 数量 |
| --- | ---: |
| INFO | 5 |
| WARN | 5 |
| ERROR | 3 |
| EXCEPTION | 1 |

## 问题模块分布

统计范围：`WARN`、`ERROR`、`EXCEPTION`

| 模块 | 问题数量 |
| --- | ---: |
| nav | 3 |
| perception | 2 |
| control | 2 |
| battery | 1 |
| task_manager | 1 |

## 高频严重错误

统计范围：`ERROR`、`EXCEPTION`

| 错误信息 | 数量 |
| --- | ---: |
| motor timeout | 2 |
| task execution interrupted | 1 |
| recovery behavior failed | 1 |

## 缺陷候选列表

统计范围：`ERROR`、`EXCEPTION`

| 建议标题 | 模块 | 错误信息 | 出现次数 | 建议优先级 |
| --- | --- | --- | ---: | --- |
| [control] motor timeout | control | motor timeout | 2 | P1 |
| [task_manager] task execution interrupted | task_manager | task execution interrupted | 1 | P2 |
| [nav] recovery behavior failed | nav | recovery behavior failed | 1 | P2 |

## 无法解析的日志行

- 第 14 行：`bad log line without expected fields`

## 测试建议

- 优先处理 `ERROR` 和 `EXCEPTION` 对应的问题。
- 如果结论为 `RISK`，说明当前没有严重错误，但警告数量偏多，建议继续观察稳定性。
- 如果 `timeout` 数量偏高，建议重点检查通信、硬件响应、控制链路或依赖服务。
- 如果某个模块问题数量明显集中，建议先检查该模块最近的版本变更、配置和依赖服务。
- 对高频严重错误补充复现步骤、视频、完整日志和必要的数据包。
